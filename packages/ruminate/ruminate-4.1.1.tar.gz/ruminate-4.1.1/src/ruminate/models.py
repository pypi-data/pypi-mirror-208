import re
import logging

# Django
import modelcluster.models
from django.db import models as django_models
from django.db.models import ForeignKey
from django.db import transaction
from django.conf import settings
from django.http import Http404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, get_language_from_request
from django.utils.functional import cached_property, classproperty
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from django.template.response import TemplateResponse

# Wagtail

from wagtail.snippets.models import register_snippet
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.models import (Page, Orderable, TranslatableMixin, DraftStateMixin, RevisionMixin, PreviewableMixin, Site,
                            Locale)

from wagtail.rich_text import RichText
from wagtail_preference_blocks.decorators import provides_preferences_context

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TagBase, ItemBase

from django_auxiliaries.variable_scope import WagtailPageMixin, reset_variable_scopes, load_variable_scope
from django_auxiliaries.servable import Servable

from wagtail_synopsis.models import AUTHOR_ROLE, build_synopsis_class_for
from wagtail_synopsis.curation import register_synopsis_category

from officekit.models import Person, Organisation, GroupMember
from tour_guide.anchors import AnchorRegistry
from tour_guide.decorators import chooses_navigation_categories

# Panels

from wagtail.admin.panels import (FieldPanel, InlinePanel, TabbedInterface, ObjectList)


# Registration Decorators

from wagtail.utils.decorators import cached_classmethod

from .model_fields import ArticleContentField, ArticleReferencesField
from .blocks import (ArticleBlock, ArticleIntroBlock, ArticleIntroValue)

from .html_to_text import html_to_text

from wagtail_block_model_field.fields import BlockModelField

from .apps import get_app_label
from .wagtail_settings import RuminateSiteSettings

APP_LABEL = get_app_label()

logger = logging.getLogger("passenger_wsgi")


class ArticleTag(TagBase):
    class Meta:
        verbose_name = "article tag"
        verbose_name_plural = "article tags"


class ArticleTagItem(ItemBase):

    class Meta:

        #constraints = [
        #    django_models.UniqueConstraint('content_object',
        #                                   'tag', name='unique_%(app_label)s_%(class)s.unique_tag_assignment')
        #]

        unique_together = (('content_object', 'tag'),)

    tag = django_models.ForeignKey(
        ArticleTag, related_name="tagged_article", on_delete=django_models.CASCADE
    )

    content_object = ParentalKey(
        to=APP_LABEL + '.Article',
        on_delete=django_models.CASCADE,
        related_name='tagged_items'
    )


def create_article_tag(*, tag, content_object):
    return ArticleTagItem(tag=tag, content_object_id=content_object.id)


def text_from_rich_text(rich_text):
    return html_to_text(rich_text.source)


SENTENCE_RE = re.compile(r'\.[ \t\n\r]+[A-Z]')


def extract_article_content_text(article):

    for stream_child in article:
        if stream_child.block_type != 'text':
            continue

        text = text_from_rich_text(stream_child.value)
        match = SENTENCE_RE.search(text)

        if match:
            text = text[:match.start() + 1]

        return text

    return ''


ARTICLE_SYNOPSIS_CATEGORY = register_synopsis_category(APP_LABEL, 'article', 'Article')


class AbstractArticle(WagtailPageMixin, TranslatableMixin,
                      DraftStateMixin, RevisionMixin, AnchorRegistry, PreviewableMixin, Servable):

    class Meta:
        abstract = True
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

        #constraints = [
        #    django_models.UniqueConstraint('first_published_at__year',
        #                                   'first_published_at__month',
        #                                   'first_published_at__day',
        #                                   'slug', name='unique_%(app_label)s_%(class)s.slug_per_date')
        #]

        unique_together = (('year', 'month', 'day', 'slug'),)

    template = APP_LABEL + "/article_page.html"

    preview_template = APP_LABEL + "/article_page.html"
    ajax_preview_template = None

    ARTICLE_BLOCK = ArticleBlock(label="Article")

    year = django_models.PositiveIntegerField(default=0, editable=False, blank=False, null=False)
    month = django_models.PositiveSmallIntegerField(default=0, editable=False, blank=False, null=False)
    day = django_models.PositiveSmallIntegerField(default=0, editable=False, blank=False, null=False)

    created_by_user = django_models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('created by user'),
        null=True,
        blank=True,
        editable=False,
        on_delete=django_models.SET_NULL
    )

    slug = django_models.SlugField(
        verbose_name=_("slug"),
        allow_unicode=True,
        max_length=255,
        help_text=_(
            "The name of the article as it will appear in URLs"
        )
    )

    intro = BlockModelField(ArticleIntroBlock(label="Intro", required=False),
                            ArticleIntroValue, blank=True, null=True)

    content = ArticleContentField(
                blank=True,
                help_text=
                "An article is composed by creating one or more sections, " +
                "each starting with a title and consisting of blocks of content such as text or images.")

    references = ArticleReferencesField(
                    blank=True)

    tags = ClusterTaggableManager(through=APP_LABEL + '.ArticleTagItem', blank=True)

    content_panels = [
        InlinePanel('authors', heading="Authors"),
        FieldPanel('content', heading="Article"),
    ]

    reference_panels = [
        FieldPanel('references')
    ]

    @cached_property
    def author_names(self):

        authors = [author.author.specific for author in self.authors.all()] # noqa
        authors = [author for author in authors if author]
        value = self.ARTICLE_BLOCK.child_blocks['authors'].value_from_group_members(authors) # noqa
        result = self.ARTICLE_BLOCK.child_blocks['authors'].render(value)
        return result

    @property
    def article_synopsis(self):

        if self.synopsis and self.synopsis.count() > 0: # noqa
            return self.synopsis.first() # noqa

        return None

    @property
    def as_block_value(self):
        return self.ARTICLE_BLOCK.value_for_article(self)

    def get_context(self, request):

        context = super().get_context(request)

        env = {
            'request': request,
            'page': None
        }

        reset_variable_scopes(env)

        load_variable_scope("tour_guide", anchor_registry=self)

        preferences_context = getattr(self, 'preferences_context', None)

        context.update({
            'article': self,
            'page_template': settings.RUMINATE_ARTICLE_PAGE_TEMPLATE,
            'preferences': preferences_context,
        })

        return context

    def get_preview_context(self, request, mode_name):

        context = super(AbstractArticle, self).get_preview_context(request, mode_name)

        context.update(
            self.get_context(request)
        )

        return context

    def get_preview_template(self, request, mode_name):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.ajax_preview_template or self.preview_template
        else:
            return self.preview_template

    def render(self, request):

        template = self.get_template(request)
        context = self.get_context(request)

        result = render_to_string(template, context=context, request=request)
        return result

    def serve(self, request):
        return super().serve(request)

    def sync_synopsis(self, synopsis):

        synopsis.category = ARTICLE_SYNOPSIS_CATEGORY.identifier

        synopsis.rubric = ''
        synopsis.rubric_url = ''

        if not synopsis.summary:
            synopsis.summary = RichText(extract_article_content_text(self.content)) # noqa

        authors = [author.author.specific for author in self.authors.all()] # noqa
        authors = [author for author in authors if author]
        value = self.ARTICLE_BLOCK.child_blocks['authors'].json_from_group_members(authors) # noqa
        value['role'] = AUTHOR_ROLE

        synopsis.names = value

    def determine_url(self, request, current_site=None):
        return ''

    def __str__(self):
        return self.title # noqa


@register_snippet
@provides_preferences_context
class Article(AbstractArticle, modelcluster.models.ClusterableModel):

    class Meta:
        unique_together = [("translation_key", "locale")]

    title = django_models.CharField(
        verbose_name=_("title"),
        max_length=255,
        help_text=_("The article title as you'd like it to be seen by the public"),
    )

    seo_title = django_models.CharField(
        verbose_name=_("title tag"),
        max_length=255,
        blank=True,
        help_text=_(
            "The name of the page displayed on search engine results as the clickable headline."
        ),
    )

    search_description = django_models.TextField(
        verbose_name=_("meta description"),
        blank=True,
        help_text=_(
            "The descriptive text displayed underneath a headline in search engine results."
        ),
    )

    content_panels = [
        FieldPanel('title', heading="Title", classname="title"),
        FieldPanel('slug', heading="Slug"),
        FieldPanel('tags', heading="Tags")
    ] + AbstractArticle.content_panels

    promote_panels = [
        FieldPanel('seo_title'),
        FieldPanel('search_description')
    ]

    def full_clean(self, *args, **kwargs):

        # Set the locale
        if self.locale_id is None:
            self.locale = self.get_default_locale()

        super().full_clean(*args, **kwargs)

    def clean(self):
        super().clean()

        queryset = Article.objects.all().filter(year=self.year, month=self.month, day=self.day, slug=self.slug, locale=self.locale)

        if self.id:
            queryset = queryset.exclude(id=self.id)

        if queryset.exists():
            raise ValidationError({"slug": _("The slug '%s' is already in use for locale %s" % (self.slug, str(self.locale)))})

    def sync_synopsis(self, synopsis):
        super(Article, self).sync_synopsis(synopsis)

        synopsis.heading = self.title
        synopsis.created_at = self.first_published_at or timezone.now()
        synopsis.updated_at = self.last_published_at

    def with_content_json(self, content):
        obj = super().with_content_json(content)

        if self.first_published_at:
            obj.year = self.first_published_at.year
            obj.month = self.first_published_at.month
            obj.day = self.first_published_at.day

        return obj

    @transaction.atomic
    def save(self, update_fields=None, clean=True, **kwargs):

        did_update_fields = False

        if self.first_published_at:
            self.year = self.first_published_at.year
            self.month = self.first_published_at.month
            self.day = self.first_published_at.day
            did_update_fields = True

        if clean:
            self.full_clean()

        if update_fields is not None and did_update_fields:
            update_fields_index = frozenset(update_fields)

            if 'year' not in update_fields_index:
                update_fields.append('year')

            if 'month' not in update_fields_index:
                update_fields.append('month')

            if 'day' not in update_fields_index:
                update_fields.append('day')

        super().save(update_fields=update_fields, **kwargs)

    def determine_url(self, request, current_site=None):

        if current_site is None:
            current_site = Site.find_for_request(request)

        if current_site is None:
            current_site = Site.objects.get(is_default_site=True)

        ruminate_settings = RuminateSiteSettings.for_site(current_site)

        if not ruminate_settings.canonical_article_index_page or not self.first_published_at:
            return ''
        
        canonical_index_page = ruminate_settings.canonical_article_index_page
        localized_index_page = canonical_index_page.get_translation_or_none(self.locale)

        if localized_index_page is None:
            default_locale = canonical_index_page.get_default_locale()
            localized_index_page = canonical_index_page.get_translation_or_none(default_locale)

        if localized_index_page is None:
            localized_index_page = canonical_index_page

        result = localized_index_page.get_url(request=request, current_site=current_site)
        result = f"{result}{self.first_published_at.year}/{self.first_published_at.month}/{self.first_published_at.day}/{self.slug}/"
        return result

    _edit_handler = None

    @classproperty
    def edit_handler(cls):

        if cls._edit_handler:
            return cls._edit_handler

        tabs = []

        if cls.content_panels:
            tabs.append(ObjectList(cls.content_panels, heading=_("Content")))

        tabs.append(ObjectList([FieldPanel('intro')], heading='Intro'))

        synopsis_adapter = ArticleSynopsis.install_synopsis_adapter_for(
            editable_fields=['summary', 'visual'],
            sync_method=Article.sync_synopsis,
            tagged_item_class=ArticleTagItem,
            tags_field='tags',
            tagged_items_field='tagged_items'
        )

        tabs.append(synopsis_adapter.create_synopsis_panel_for(cls))

        if cls.reference_panels:
            tabs.append(ObjectList(cls.reference_panels, heading='References'))

        if cls.promote_panels:
            tabs.append(ObjectList(cls.promote_panels, heading=_("Promote")))

        edit_handler = TabbedInterface(tabs)

        bound_handler = edit_handler.bind_to_model(cls)
        cls._edit_handler = bound_handler
        return bound_handler


class NthAuthorInArticle(Orderable):

    class Meta(Orderable.Meta):
        verbose_name = 'Author in Article'
        verbose_name_plural = 'Authors in Article'
        unique_together = (('author', 'article'),)

    article = ParentalKey(Article, related_name="authors", on_delete=django_models.CASCADE, blank=False)
    author = ForeignKey(GroupMember, related_name="articles", on_delete=django_models.CASCADE, blank=False)

    panels = [
        FieldPanel('article'),
        FieldPanel('author'),
    ]

    def __str__(self):
        author = self.author.specific # noqa

        if isinstance(author, Person):
            name = author.full_name
        elif isinstance(author, Organisation):
            name = author.name
        else:
            name = '[unknown group member type]'

        return f"{name} in {self.article.title}" # noqa


ArticleSynopsis = build_synopsis_class_for(Article)


@chooses_navigation_categories
class ArticleIndexPage(RoutablePageMixin, AnchorRegistry, Page):

    template = APP_LABEL + "/article_index_page.html"
    default_redirect_target = settings.RUMINATE_ARTICLE_INDEX_REDIRECT_TARGET

    @path('')
    def default_view(self, request):

        if self.default_redirect_target:
            return redirect(self.default_redirect_target, permanent=False)

        if settings.RUMINATE_ARTICLE_INDEX_NOT_ACCESSIBLE:
            raise Http404('Not found.')

        return self.index_route(request)

    @path('<int:year>/<int:month>/<int:day>/<str:slug>/')
    def serve_article(self, request, year, month, day, slug):

        locale = self.locale

        if locale is None:

            language = get_language_from_request(request)

            try:
                locale = Locale.objects.get_for_language(language)
            except Locale.DoesNotExist:
                locale = Locale.get_active()

        try:
            article = Article.objects.get(live=True,
                                          first_published_at__year=year, first_published_at__month=month,
                                          first_published_at__day=day, slug__iexact=slug, locale_id=locale.id)
        except Article.DoesNotExist:

            try:
                locale = Locale.objects.get_for_language('en')
            except Locale.DoesNotExist:
                locale = None

            articles = Article.objects.filter(
                                        live=True,
                                        first_published_at__year=year, first_published_at__month=month,
                                        first_published_at__day=day, slug__iexact=slug, locale_id=locale.id).order_by(
                'locale__language_code')

            if not articles.exists():
                raise Http404('Not found.')

            article = articles.first()

        return article.serve(request)

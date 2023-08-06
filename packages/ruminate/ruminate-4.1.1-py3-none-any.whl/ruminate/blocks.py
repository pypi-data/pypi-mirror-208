import weakref

from django import forms
from django.apps import apps
from django.conf import settings

from django.utils.functional import cached_property

from wagtail import blocks
from wagtail.embeds import blocks as embed_blocks
from wagtail.documents import blocks as document_blocks
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.admin.staticfiles import versioned_static
from wagtail.telepath import register

from media_catalogue.blocks import MediaItemChooserBlock

from wagtail_richer_text.templatetags.wagtail_richer_text_tags import richertext

from wagtail_switch_block.blocks import SwitchBlock, SwitchValue, TYPE_FIELD_NAME as SWITCH_BLOCK_TYPE_FIELD_NAME

from wagtail_tags_block.blocks import TagsBlock, TagsValue

from model_porter.support_mixin import ModelPorterSupportMixin
from swatchbook.blocks import ColourBlock
from figurative.blocks import FigureBlock, SlideshowBlock

from officekit.blocks import NameListBlock

from bibster.blocks import ReferenceBlock


from wagtail_richer_text.blocks import RichTextBlock

from .apps import get_app_label

__all__ = ['ArticleIntroBlock', 'ArticleIntroValue',
           'ArticleBoilerplateBlock', 'ArticleBoilerplateBlockValue',
           'ArticleBlock', 'ArticleBlockValue',
           'ArticleContentBlock', 'ArticleContentBlockValue',
           'ArticleReferencesBlock', 'ArticleReferencesBlockValue',
           'SectionBlock',
           'NoteBlock', 'NoteCategory', 'register_note_category', 'lookup_note_category',
           'ENDNOTE_NOTE_CATEGORY', 'ASIDE_NOTE_CATEGORY'] # noqa

APP_LABEL = get_app_label()


class ArticleBlockChildValue(blocks.StructValue):

    def article(self):
        article_ref = self['article_ref']

        if not article_ref:
            return None

        return article_ref()


class BaseIntroBlock(ModelPorterSupportMixin, blocks.StructBlock):

    class Meta:
        value_class = ArticleBlockChildValue
        form_classname = "struct-block article-intro-block"

    article_ref = blocks.StaticBlock()  # placeholder for article value

    @property
    def article_block(self):

        from .models import Article
        return Article.ARTICLE_BLOCK


class BaseIntroBlockAdapter(StructBlockAdapter):

    def js_args(self, block):
        result = super(BaseIntroBlockAdapter, self).js_args(block)
        return result

    @cached_property
    def media(self):
        # noinspection SpellCheckingInspection
        return forms.Media(css={'all': [
            versioned_static(APP_LABEL + '/css/ruminate_admin.css'),
        ]},
            js=[
            ])


register(BaseIntroBlockAdapter(), BaseIntroBlock)


class NoneIntroBlock(BaseIntroBlock):

    class Meta:
        icon = 'link'
        template = APP_LABEL + "/blocks/none_intro_block.html"
        classname = settings.RUMINATE_NONE_INTRO_BLOCK_CLASSNAME

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class MinimalIntroBlock(BaseIntroBlock):

    class Meta:
        icon = 'link'
        template = APP_LABEL + "/blocks/minimal_intro_block.html"
        classname = settings.RUMINATE_MINIMAL_INTRO_BLOCK_CLASSNAME

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


SpreadFigureBlock = FigureBlock(user_configurable_content=False, default_anchor_category=None)


class SpreadIntroBlock(BaseIntroBlock):

    class Meta:
        icon = 'link'
        template = APP_LABEL + "/blocks/spread_intro_block.html"
        classname = settings.RUMINATE_SPREAD_INTRO_BLOCK_CLASSNAME

    visual = MediaItemChooserBlock(required=False, help_text="Include visual media.", max_num_choices=1)

    title_colour = ColourBlock(label="Title Colour", required=False)
    summary_colour = ColourBlock(label="Summary Colour", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        intro_visual = SpreadFigureBlock.get_default()
        intro_visual['arrange_as'] = FigureBlock.arrangement_choices[0][0]
        intro_visual['fit_width'] = 'viewport'
        intro_visual['format'] = 'viewport'
        intro_visual['content_fit'] = 'cover'
        intro_visual['anchor_category'] = None

        context['intro_visual'] = intro_visual

        return context

    # noinspection PyMethodMayBeStatic
    def from_repository(self, value, context):

        value['visual'] = self.child_blocks['visual'].from_repository(value['visual'], context)

        return value


ArticleBoilerplateBlockValue = ArticleBlockChildValue


class ArticleBoilerplateBlock(blocks.StructBlock):

    class Meta:
        classname = settings.RUMINATE_ARTICLE_BOILERPLATE_BLOCK_CLASSNAME
        author_visual_scale_factor = settings.RUMINATE_ARTICLE_BOILERPLATE_AUTHOR_VISUAL_SCALE_FACTOR
        value_class = ArticleBoilerplateBlockValue
        template = APP_LABEL + "/blocks/article_boilerplate_block.html"

    article_ref = blocks.StaticBlock()  # placeholder for article value
    author_visual = FigureBlock(user_configurable_content=False, default_anchor_category=None)

    @property
    def article_block(self):

        from .models import Article
        return Article.ARTICLE_BLOCK

    def get_context(self, value, parent_context=None):

        context = super().get_context(value, parent_context)

        article = value['article_ref']() if value['article_ref'] else None

        context['article'] = article
        context['author_visual_scale_factor'] = self.meta.author_visual_scale_factor

        author_visual = value['author_visual']
        author_visual['image_filter_expr'] = 'saturate-0'

        all_authors_have_visual = False

        if article:

            all_authors_have_visual = bool(article['authors']['names'])

            for stream_child in article['authors']['names']:

                if stream_child.block_type == 'person':

                    if not stream_child.value['identify_with'] or not stream_child.value['identify_with'].portrait.value:
                        all_authors_have_visual = False
                        break

                elif stream_child.block_type == 'organisation':

                    if not stream_child.value.identify_with or not stream_child.value['identify_with'].logo.value:
                        all_authors_have_visual = False
                        break

                else:
                    all_authors_have_visual = False
                    break

        context['all_authors_have_visual'] = all_authors_have_visual

        return context


ArticleIntroValue = SwitchValue


class ArticleIntroBlock(SwitchBlock):

    class Meta:
        icon = 'link'
        default_block_name = 'minimal'
        default = {'__type__': 'minimal', 'minimal': {'article_ref': None}}

    none = NoneIntroBlock()
    minimal = MinimalIntroBlock()
    spread = SpreadIntroBlock()

    def __init__(self, **kwargs):
        super(ArticleIntroBlock, self).__init__(**kwargs)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs

    def render_basic(self, value, context=None):

        if not value:
            return ''

        block_type = value.get(SWITCH_BLOCK_TYPE_FIELD_NAME, 'none')

        if block_type == 'none':
            return ''

        block_value = value.get(block_type, None)

        # block_def = self.child_blocks[block_type]
        # if isinstance(block_def, BaseIntroBlock):
        #     block_value['article'] = value['article']

        return block_value.render_as_block(context=context)


class NoteCategory:

    @property
    def identifier(self):
        return self.app_label + ":" + self.local_identifier

    def __init__(self, app_label, local_identifier, name, anchor_category):
        self.app_label = app_label
        self.local_identifier = local_identifier
        self.name = name
        self.anchor_category = anchor_category

        app = apps.get_app_config(self.app_label)
        self.app_name = app.verbose_name


NOTE_CATEGORIES = dict()


def register_note_category(app_label, local_identifier, name, anchor_category):

    method = NoteCategory(app_label=app_label, local_identifier=local_identifier, name=name,
                          anchor_category=anchor_category)
    NOTE_CATEGORIES[method.identifier] = method
    return method


def lookup_note_category(identifier, default=None):
    return NOTE_CATEGORIES.get(identifier, default)


def get_note_category_choices():

    result = [(identifier, category.name + " [{}]".format(category.app_name.title()))
              for identifier, category in NOTE_CATEGORIES.items()]

    return result


ENDNOTE_NOTE_CATEGORY = register_note_category(APP_LABEL, "endnote", "Endnote", "endnote") # noqa
ASIDE_NOTE_CATEGORY = register_note_category(APP_LABEL, "aside", "Aside", None)


class NoteBlock(blocks.StructBlock):

    class Meta:
        template = APP_LABEL + "/blocks/note_block.html"

    category = blocks.ChoiceBlock(label="Category",
                                  choices=get_note_category_choices,
                                  required=True, default=APP_LABEL + ":endnote") # noqa

    anchor_identifier = blocks.CharBlock(label="Anchor Identifier", required=False, default="")

    text = RichTextBlock(label='Text',
                         editor='ruminate.richtextarea', # noqa
                         required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class SectionBlock(blocks.StructBlock):

    class Meta:
        icon = 'form'
        template = APP_LABEL + '/blocks/section_block.html'

    heading = blocks.CharBlock(label="Section Heading", required=True, default="",
                               help_text="Specify a title for this section.")
    level = blocks.ChoiceBlock(label="Level", required=True,
                               choices=[(i, "Level {:d}".format(i)) for i in range(2, 6)], default=2)
    anchor_identifier = blocks.CharBlock(label="Anchor Identifier", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


section_begin = blocks.StaticBlock()
section_begin.name = 'section_begin'

section_end = blocks.StaticBlock()
section_end.name = 'section_end'


ArticleContentBlockValue = blocks.StreamValue


class ArticleContentBlock(blocks.StreamBlock):

    class Meta:
        icon = 'form'
        container_element = None
        default = []
        template = APP_LABEL + '/blocks/article_content_block.html'

    section = SectionBlock(label="Section")

    text = RichTextBlock(label='Text',
                         editor=APP_LABEL + '.richtextarea',  # noqa
                         required=False,
                         help_text=("Use a text block for writing a sequence of paragraphs and to "
                                    "apply semantic styles. Paragraphs are defined by inserting "
                                    "line breaks from the editor toolbar."))

    figure = FigureBlock(label='Figure', help_text="Present visual media in a figure.", required=False)
    slideshow = SlideshowBlock(label='Slideshow', help_text="Present visual media as a slideshow",
                               required=False)

    embed = embed_blocks.EmbedBlock(label="Embed", required=False)
    document = document_blocks.DocumentChooserBlock(label="Document", required=False)
    note = NoteBlock(label='Note', help_text="Endnotes and asides.", required=False)  # noqa

    @property
    def anchor_category(self):
        return "section"

    def to_python(self, value):

        value = blocks.StreamBlock.to_python(self, value)
        return value

    def get_prep_value(self, value):

        value = blocks.StreamBlock.get_prep_value(self, value)
        return value

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        path = APP_LABEL + '.ArticleContentBlock'
        return path, [], kwargs

    def create_stream_child(self, type_name, value, block_id=None):

        if type_name == 'section_begin':
            block_def = section_begin
        elif type_name == 'section_end':
            block_def = section_end
        else:
            block_def = self.child_blocks[type_name]

        return blocks.StreamValue.StreamChild(block_def, value, id=block_id)

    def render(self, value, context=None):

        result = []

        previous_section_level = 1
        section_level = 1

        for stream_index, stream_child in enumerate(value):

            if not isinstance(stream_child.block, SectionBlock):
                result.append(stream_child)
                continue

            section_level = stream_child.value.get('level', previous_section_level)

            try:
                section_level = int(section_level)
            except ValueError:
                section_level = previous_section_level

            for index in range(section_level, previous_section_level + 1):
                filler = self.create_stream_child('section_end', None)
                result.append(filler)

            for index in range(previous_section_level + 1, section_level):
                filler = self.create_stream_child('section_begin', None)
                result.append(filler)

            filler = self.create_stream_child('section_begin', stream_child.value)
            result.append(filler)

            result.append(stream_child)

            previous_section_level = section_level

        for index in range(section_level, previous_section_level + 1):
            filler = self.create_stream_child('section_end', None)
            result.append(filler)

        value = blocks.StreamValue(self, result)
        result = super().render(value, context=context)
        return result


ArticleReferencesBlockValue = blocks.StreamValue


class ArticleReferencesBlock(blocks.StreamBlock):

    class Meta:
        template = APP_LABEL + '/blocks/article_references_block.html'

    reference = ReferenceBlock(label="Reference")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        if 'label_references' not in context:
            context['label_references'] = False

        return context

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


ArticleTagsBlockValue = TagsValue


class ArticleTagsBlock(TagsBlock):

    class Meta:
        template = APP_LABEL + '/blocks/article_tags_block.html'
        classname = settings.RUMINATE_ARTICLE_TAGS_BLOCK_CLASSNAME
        tag_model = APP_LABEL + ".articletag"
        tag_classname = settings.RUMINATE_ARTICLE_TAGS_BLOCK_TAG_CLASSNAME
        container_element = settings.RUMINATE_ARTICLE_TAGS_BLOCK_CONTAINER_ELEMENT


ArticleBlockValue = blocks.StructValue


class ArticleBlock(blocks.StructBlock):

    class Meta:
        classname = settings.RUMINATE_ARTICLE_BLOCK_CLASSNAME
        content_classname = settings.RUMINATE_ARTICLE_BLOCK_CONTENT_CLASSNAME
        tabs_classname = settings.RUMINATE_ARTICLE_BLOCK_TABS_CLASSNAME
        parts_classname = settings.RUMINATE_ARTICLE_BLOCK_PARTS_CLASSNAME
        template = APP_LABEL + '/blocks/article_block.html'

    intro = ArticleIntroBlock(required=False)
    title = blocks.CharBlock(required=False)
    first_published_at = blocks.DateBlock(label="First Published", required=False, default={})
    last_published_at = blocks.DateBlock(label="Last Published", required=False, default={})
    summary = RichTextBlock(required=False)
    authors = NameListBlock(required=False, classname=settings.RUMINATE_ARTICLE_BLOCK_AUTHORS_CLASSNAME,
                            container_element="ol")

    boilerplate = ArticleBoilerplateBlock(label="Boilerplate", classname=settings.RUMINATE_ARTICLE_BOILERPLATE_BLOCK_CLASSNAME)

    tags = ArticleTagsBlock(required=False)
    content = ArticleContentBlock(required=False)
    endnotes = blocks.StaticBlock() # noqa
    references = ArticleReferencesBlock(required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs

    def value_for_article(self, article):

        authors = self.child_blocks['authors'].value_from_group_members(
            [assignment.author for assignment in article.authors.all()])

        boilerplate = self.child_blocks['boilerplate'].get_default()

        tags = []

        for article_tag in article.tags.all(): # noqa
            tags.append(article_tag.name)

        endnotes = [] # noqa

        for child_block in article.content:
            if child_block.block_type == "note" and child_block.value['category'] == APP_LABEL + ':endnote': # noqa
                endnotes.append(child_block)

        intro = blocks.StructValue(article.intro.block, article.intro)

        value = blocks.StructValue(self, {
            "intro": article.intro,
            "title": article.title,
            "first_published_at": article.first_published_at,
            "last_published_at": article.last_published_at,
            "summary": richertext(article.article_synopsis.summary),
            "authors": authors,
            "boilerplate": boilerplate,
            "tags": self.child_blocks['tags'].to_python(tags),
            "content": article.content,
            "endnotes": endnotes, # noqa
            "references": article.references
        })

        if isinstance(article.intro.block.child_blocks[intro['__type__']], BaseIntroBlock):
            intro[intro['__type__']]['article_ref'] = weakref.ref(value)

        if isinstance(self.child_blocks['boilerplate'], ArticleBoilerplateBlock):
            boilerplate['article_ref'] = weakref.ref(value)

        return value

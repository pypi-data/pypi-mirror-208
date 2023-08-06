
from wagtail.contrib.modeladmin.views import CreateView, EditView
from wagtail.contrib.modeladmin.options import (ModelAdmin)

from .models import Article
from .side_panels import ArticleSidePanels


class ArticleCreateView(CreateView):

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(form, **kwargs)

        side_panels = ArticleSidePanels(
            self.request,
            form.instance if form else None
        )

        # context['side_panels'] = side_panels

        return context


class ArticleEditView(EditView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        side_panels = ArticleSidePanels(
            self.request,
            self.instance
        )

        context['side_panels'] = side_panels.side_panels

        return context


class ArticleAdmin(ModelAdmin):

    model = Article
    menu_icon = 'thumbtack'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = True  # or True to exclude pages of this type from Wagtail's explorer view
    exclude_from_admin_menu = False

    create_view_class = ArticleCreateView
    edit_view_class = ArticleEditView

    inspect_view_enabled = False

    list_display = ('title', 'updated_at', 'author_names')
    list_filter = ('tags',)
    search_fields = ('title',)
    ordering = ('-updated_at', 'title')

    index_view_extra_js = []

    instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ArticleAdmin.instance = self

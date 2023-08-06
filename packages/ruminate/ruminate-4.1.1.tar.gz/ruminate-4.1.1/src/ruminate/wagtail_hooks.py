
from django.contrib.admin.utils import quote
from django.urls import include, path, reverse
from django.utils.translation import gettext_lazy as _

from wagtail.admin.menu import MenuItem
from wagtail import hooks
from wagtail.permissions import ModelPermissionPolicy

from . import admin_urls

from .apps import get_app_label
from .models import Article

APP_LABEL = get_app_label()


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path(APP_LABEL + '/', include(admin_urls, namespace=APP_LABEL)),
    ]


class ArticlesMenuItem(MenuItem):

    permission_policy = ModelPermissionPolicy(Article)

    def __init__(self, label, *args, **kwargs):

        app_label = Article._meta.app_label
        model_name = Article._meta.model_name

        url = reverse(
            f"wagtailsnippets_{app_label}_{model_name}:list"
        )

        super(ArticlesMenuItem, self).__init__(label, url, *args, **kwargs)

    def is_shown(self, request):
        return self.permission_policy.user_has_any_permission(
                    request.user, ["add", "edit", "delete"]
                ),


@hooks.register('register_admin_menu_item')
def register_article_menu_item():
    return ArticlesMenuItem(
        _('Articles'),
        name='articles', icon_name='thumbtack', order=300
    )


# from wagtail.contrib.modeladmin.options import modeladmin_register
# from .model_admin import ArticleAdmin
# modeladmin_register(ArticleAdmin)

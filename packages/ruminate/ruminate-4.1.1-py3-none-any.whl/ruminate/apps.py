from types import SimpleNamespace
import sys

from django.conf import settings
from django.db import DEFAULT_DB_ALIAS

from django.urls import reverse
from django.apps import AppConfig
from django.apps import apps
from django.utils.translation import gettext_lazy as _


def is_running_without_database():
    engine = settings.DATABASES[DEFAULT_DB_ALIAS]['ENGINE']
    return engine == 'django.db.backends.dummy'


class RuminateConfig(AppConfig):
    name = 'ruminate'
    label = 'ruminate'
    verbose_name = _("Ruminate")
    default_auto_field = 'django.db.models.BigAutoField'
    app_settings_getters = SimpleNamespace()

    def import_models(self):

        from django_auxiliaries.app_settings import configure

        self.app_settings_getters = configure(self)

        super().import_models()

    def ready(self):

        # noinspection SpellCheckingInspection
        if is_running_without_database() or "makemigrations" in sys.argv or "migrate" in sys.argv:
            return

        from officekit.models import Person
        from wagtail.admin.panels import MultiFieldPanel
        from wagtail_association_panel.association_panel import AssociationPanel

        panel = MultiFieldPanel([
            AssociationPanel('articles', edit_url_name="wagtailadmin_pages:edit"),
        ], "Articles")

        Person.panels.append(panel)

        # Make sure synopsis adapter is installed!

        from .models import Article
        _ = Article.edit_handler



def get_app_label():
    return RuminateConfig.label


def reverse_app_url(identifier):
    return reverse(f'{RuminateConfig.label}:{identifier}')


def get_app_config():
    return apps.get_app_config(RuminateConfig.label)

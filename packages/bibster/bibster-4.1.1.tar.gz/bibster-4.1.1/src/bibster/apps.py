# -*- coding: utf-8 -*-

from types import SimpleNamespace
import sys
from django.apps import apps
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS
from django.urls import reverse
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


def is_running_without_database():
    engine = settings.DATABASES[DEFAULT_DB_ALIAS]['ENGINE']
    return engine == 'django.db.backends.dummy'


# noinspection SpellCheckingInspection
class BibsterConfig(AppConfig):
    # noinspection SpellCheckingInspection
    name = 'bibster'
    # noinspection SpellCheckingInspection
    label = 'bibster'
    # noinspection SpellCheckingInspection
    verbose_name = _("Bibster")
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
            AssociationPanel('publications', edit_url_name=self.label + "_publication_modeladmin_edit"),
        ], "Publications")

        Person.panels.append(panel)


def get_app_label():
    return BibsterConfig.label


def reverse_app_url(identifier):
    return reverse(f'{BibsterConfig.label}:{identifier}')


def get_app_config():
    return apps.get_app_config(BibsterConfig.label)


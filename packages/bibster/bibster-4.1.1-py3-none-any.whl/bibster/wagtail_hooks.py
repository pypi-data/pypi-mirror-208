from django.conf.urls import include
from django.urls import re_path

from wagtail import hooks
from wagtail.contrib.modeladmin.options import modeladmin_register

from . import admin_urls

from .model_admin import PublicationModelAdmin
from .apps import get_app_label

APP_LABEL = get_app_label()


@hooks.register('register_admin_urls')
def register_admin_urls():
    result = [
        re_path(r'^bibliography/', include(admin_urls, namespace=APP_LABEL)),
    ]

    return result


modeladmin_register(PublicationModelAdmin)

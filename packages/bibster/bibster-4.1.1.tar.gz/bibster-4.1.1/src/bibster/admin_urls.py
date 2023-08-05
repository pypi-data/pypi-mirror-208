from django.urls import re_path

from .views.lookup import lookup
from .views.action import action
from .apps import get_app_label
from .content_admin import publication_admin

app_name = get_app_label()


urlpatterns = publication_admin.create_chooser_admin_urls() + [
    re_path(r'^lookup/$', lookup, name='lookup_reference'),
    re_path(r'^action/$', action, name='action'),
]


from django import forms

from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property

from wagtail.telepath import Adapter, register
from wagtail.admin.staticfiles import versioned_static

from django_auxiliaries.templatetags.django_auxiliaries_tags import tagged_static

from .apps import get_app_label

APP_LABEL = get_app_label()


class ContentChooserState(object):

    @property
    def items(self):
        return self.items_[:]

    def __init__(self):
        self.items_ = []

    def add_item(self, item):
        self.items_.append(item)


class ContentChooserStateAdapter(Adapter):

    js_constructor = APP_LABEL + '.widgets.ContentChooserState'

    def js_args(self, state):
        meta = {
            'strings': {
                'MOVE_UP': _("Move up"),
                'MOVE_DOWN': _("Move down"),
                'DUPLICATE': _("Duplicate"),
                'DELETE': _("Delete"),
                'ADD': _("Add"),
            },
        }

        help_text = ''
        meta['helpText'] = help_text

        return [
            state.items,
            meta
        ]

    @cached_property
    def media(self):
        return forms.Media(css={
            'all': [tagged_static(APP_LABEL + '/css/wagtail_content_admin.css')]
        }, js=[
            versioned_static('wagtailadmin/js/wagtailadmin.js'),
            tagged_static(APP_LABEL + '/js/wagtail_content_admin.js'),
        ])


register(ContentChooserStateAdapter(), ContentChooserState)

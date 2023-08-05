
from django.apps import apps

from .identifiers import *
from .formatting.markup import *
from .harvard_style import harvard_style
from .html_markup import REFERENCE_MARKUP
from .apps import get_app_label

__all__ = ['format_reference', 'create_markup_cache',
           'DEFAULT_MARKUP_FORMAT', 'PLAIN_MARKUP_FORMAT', 'HTML_MARKUP_FORMAT',
           'DEFAULT_STYLE', 'HARVARD_STYLE',
           'DEFAULT_LABEL_STYLE', 'HARVARD_LABEL_STYLE']


APP_LABEL = get_app_label()

HARVARD_STYLE_INSTANCE = harvard_style()
HARVARD_LABEL_STYLE_INSTANCE = harvard_style(label_mode=True)

STYLE_REGISTRY = {
    HARVARD_STYLE: HARVARD_STYLE_INSTANCE,
    HARVARD_LABEL_STYLE: HARVARD_LABEL_STYLE_INSTANCE,
    DEFAULT_STYLE: HARVARD_STYLE_INSTANCE,
    DEFAULT_LABEL_STYLE: HARVARD_LABEL_STYLE_INSTANCE,
}


class MarkupFormatRegistration:

    @property
    def identifier(self):
        return self.app_label + ":" + self.local_identifier

    def __init__(self, app_label, local_identifier, name, markup_format):
        self.app_label = app_label
        self.local_identifier = local_identifier
        self.name = name
        self.markup_format = markup_format

        app = apps.get_app_config(self.app_label)
        self.app_name = app.verbose_name


def register_markup_format(app_label, local_identifier, name, markup_format):

    registration = MarkupFormatRegistration(app_label=app_label, local_identifier=local_identifier,
                                            name=name, markup_format=markup_format)
    MARKUP_FORMAT_REGISTRY[registration.identifier] = registration
    return registration


def get_markup_format_choices():

    result = [(identifier, category.name + " [{}]".format(category.app_name.title()))
              for identifier, category in MARKUP_FORMAT_REGISTRY.items()]

    return result


MARKUP_FORMAT_REGISTRY = dict()

PLAIN_FORMAT = register_markup_format(APP_LABEL, "plain", "Plain Text", MarkupFormat())
HTML_FORMAT = register_markup_format(APP_LABEL, "html", "HTML", REFERENCE_MARKUP)

PLAIN_MARKUP_FORMAT = PLAIN_FORMAT.identifier
HTML_MARKUP_FORMAT = HTML_FORMAT.identifier

DEFAULT_MARKUP_FORMAT = PLAIN_MARKUP_FORMAT


def lookup_markup_format(identifier, default=None):
    return MARKUP_FORMAT_REGISTRY.get(identifier, default)


def create_markup_cache():
    return {}


def format_reference(value, style_name, markup_format_name=None, placeholder="", markup_cache=None, bypass_cache=False):

    if markup_format_name is None:
        markup_format_name = DEFAULT_MARKUP_FORMAT

    parts = markup_format_name.split(':')

    if len(parts) == 1:
        markup_format_name = APP_LABEL + ":" + markup_format_name

    if markup_cache and not bypass_cache:
        cache_entry = lookup_in_cache(markup_cache, style_name, markup_format_name)

        if cache_entry is not None:
            return cache_entry[0], cache_entry[1]

    format_entry = MARKUP_FORMAT_REGISTRY.get(markup_format_name, PLAIN_FORMAT)

    # from .models import ReferenceStyle
    # style_object = ReferenceStyle.objects.get(identifier=style_name)
    # style = style_object.format_instance

    style = STYLE_REGISTRY.get(style_name, None)

    if not style:
        return placeholder, MarkupMetadata()

    result, metadata = style(value, [(0, [(0, value)])], format_entry.markup_format)

    if markup_cache is not None:
        update_cache(markup_cache, result, metadata, style_name, format_entry)

    return result, metadata


def lookup_in_cache(markup_cache, style_name, markup_format_name=None):

    if markup_format_name is None:
        markup_format_name = DEFAULT_MARKUP_FORMAT

    style_cache_entry = markup_cache.get(style_name, {})
    cache_entry = style_cache_entry.get(markup_format_name, {})
    result = cache_entry.get("content", None)
    metadata = cache_entry.get("metadata", None)

    if metadata is not None:
        metadata = MarkupMetadata.from_json(metadata)

    if result is not None:

        if metadata is None:
            metadata = MarkupMetadata()

        return result, metadata

    return None


def update_cache(markup_cache, content, metadata, style_name, format_entry):

    style_cache_entry = markup_cache.get(style_name, None)

    if style_cache_entry is None:
        style_cache_entry = {}
        markup_cache[style_name] = style_cache_entry

    cache_entry = style_cache_entry.get(format_entry.identifier, None)

    if cache_entry is None:
        cache_entry = {}
        style_cache_entry[format_entry.identifier] = cache_entry

    cache_entry["version"] = string_from_version(format_entry.markup_format.version)
    cache_entry["content"] = content
    cache_entry["metadata"] = metadata.to_json()


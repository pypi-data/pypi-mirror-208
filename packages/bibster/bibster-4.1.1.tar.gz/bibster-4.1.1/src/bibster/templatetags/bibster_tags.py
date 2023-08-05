from django import template
from django.utils.html import mark_safe
from django.templatetags.static import static

from wagtail import blocks

from ..format_auxiliaries import format_reference, DEFAULT_STYLE, DEFAULT_MARKUP_FORMAT, DEFAULT_LABEL_STYLE, \
                                 PLAIN_MARKUP_FORMAT

from ..blocks import ReferenceBlock

register = template.Library()

REFERENCE_BLOCK_DEF = ReferenceBlock()


@register.simple_tag(name="format_reference")
def format_reference_tag(value, style_name=DEFAULT_STYLE, markup_format_name=DEFAULT_MARKUP_FORMAT, markup_cache=None, bypass_cache=False):

    if isinstance(value, blocks.StructValue):
        value = REFERENCE_BLOCK_DEF.get_prep_value(value)

    output, metadata = format_reference(value, style_name, markup_format_name, markup_cache=markup_cache, bypass_cache=bypass_cache)
    output = mark_safe(output)
    return output


@register.simple_tag(name="format_reference_label")
def format_reference_label_tag(value, style_name=DEFAULT_LABEL_STYLE, markup_cache=None, bypass_cache=False):

    if isinstance(value, blocks.StructValue):
        value = REFERENCE_BLOCK_DEF.get_prep_value(value)

    output, metadata = format_reference(value, style_name, PLAIN_MARKUP_FORMAT, markup_cache=markup_cache, bypass_cache=bypass_cache)
    return output


@register.simple_tag(takes_context=True)
def bibster_support(context, *, is_admin_tag=False, container_element='body'):

    if container_element == 'head':
        return mark_safe('<link rel="stylesheet" type="text/css" href="{}">'.format(static("bibster/css/bibster.css")))

    return ''

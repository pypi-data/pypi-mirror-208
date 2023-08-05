

from wagtail.blocks import StreamValue

from wagtail_switch_block.blocks import TYPE_FIELD_NAME

from model_porter.config import ModelPorterConfig
from model_porter.utilities import define_tags as define_generic_tags
from media_catalogue.model_porter import media_chooser_value

from taggit.models import Tag

from .auto_fill import identify_reference
from .blocks import ReferenceBlock
from .models import PublicationTag

REFERENCE_BLOCK_DEF = ReferenceBlock()


def lookup_doi(*, doi):
    lookup_result = identify_reference(doi)

    if lookup_result is None:
        return None

    reference_type = None

    for key in lookup_result.keys():
        reference_type = key
        break

    lookup_result[TYPE_FIELD_NAME] = reference_type
    value = REFERENCE_BLOCK_DEF.to_python(lookup_result)
    return value


def define_tags(*, tag_values, context):
    return define_generic_tags(tag_values=tag_values, tag_class=Tag, tag_item_class=PublicationTag, context=context)


def build_attachments(*, refs, context):

    attachments = []

    for ref in refs:
        attachment_key, items = ref

        if attachment_key == 'media':
            items = media_chooser_value(items=items, context=context)

        attachments.append((attachment_key, items))

    return attachments


class BibsterConfig(ModelPorterConfig):

    def __init__(self, app_label, module):
        super(BibsterConfig, self).__init__(app_label, module)
        self.register_function_action(lookup_doi)
        self.register_function_action(build_attachments, context_argument='context')
        self.register_function_action(define_tags, context_argument='context')

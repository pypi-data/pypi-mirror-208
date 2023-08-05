import codecs

from .base import ALL_XML_CLASSES as ALL_XML_BASE_CLASSES
from .value_converters import ALL_XML_CLASSES as ALL_XML_CONVERTER_CLASSES
from .predicate_format import ALL_XML_CLASSES as ALL_XML_PREDICATE_CLASSES
from .grouping_format import ALL_XML_CLASSES as ALL_XML_GROUPING_CLASSES

from .sequence_map import SequenceMap
from .sequence_format import SequenceFormat
from .value_format import ValueFormat
from .dictionary_format import DictionaryFormat
from .switch_format import SwitchFormat

from ..xml_io import camelcase_to_snakecase, inflate_object_from_xml, deflate_object_to_xml

__all__ = ['inflate_style_from_xml', 'inflate_style_from_xml_file', 'deflate_style_to_xml', 'deflate_style_to_xml_file']

ELEMENT_REGISTRY_ITEMS = [
    SequenceMap,
    ValueFormat,
    SequenceFormat,
    DictionaryFormat,
    SwitchFormat,

]

ELEMENT_REGISTRY_ITEMS.extend(ALL_XML_BASE_CLASSES)
ELEMENT_REGISTRY_ITEMS.extend(ALL_XML_CONVERTER_CLASSES)
ELEMENT_REGISTRY_ITEMS.extend(ALL_XML_PREDICATE_CLASSES)
ELEMENT_REGISTRY_ITEMS.extend(ALL_XML_GROUPING_CLASSES)

ELEMENT_REGISTRY_ITEMS = [(camelcase_to_snakecase(x.__name__), x) for x in ELEMENT_REGISTRY_ITEMS]
ELEMENT_REGISTRY = dict(ELEMENT_REGISTRY_ITEMS)


def inflate_style_from_xml(xml_text):

    style = inflate_object_from_xml(xml_text, ELEMENT_REGISTRY)
    return style


def inflate_style_from_xml_file(path):

    with codecs.open(path, "rb", encoding="utf-8") as file:
        xml_text = file.read()
        return inflate_style_from_xml(xml_text)


def deflate_style_to_xml(style):

    xml_text = deflate_object_to_xml(style)
    return xml_text


def deflate_style_to_xml_file(style, path):

    xml_text = deflate_style_to_xml(style)

    with codecs.open(path, "wb+", encoding="utf-8") as file:
        file.write(xml_text)
        file.flush()
        file.close()

from collections import OrderedDict

from .formatting import *
from .harvard_style import *

__all__ = ['name_list_plain_style']


def person_plain_style():

    attribute_formats = OrderedDict([
        ("given_names_and_initials", given_names_and_initials_harvard_style()),
        ("family_name", family_name_harvard_style()),
    ])

    apply_name_prefix(attribute_formats, "person.")

    attribute_order = ("given_names_and_initials", "family_name")
    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ", "))
    format = DictionaryFormat(attribute_order, attribute_formats, seq_format)

    format.set_xml_name("person_plain_style")
    return format


def name_plain_style():

    case_formats = OrderedDict([
        ("person", person_plain_style()),
    ])

    apply_name_prefix(case_formats, "name.")

    format = SwitchFormat(case_formats, switch_markup_class="name")
    format.set_xml_name("name_harvard_style")
    return format


def name_list_plain_style(outer_markup_class=None):

    ellipsis = None

    seq_format = SequenceFormat(name_plain_style(), SequenceMap(((0, ""), (-1, "")), "; "), ellipsis=ellipsis)

    attribute_items = [
        ("names", seq_format)
    ]

    attribute_formats = OrderedDict(attribute_items)

    apply_name_prefix(attribute_formats, "name_list.")

    attribute_order = [item[0] for item in attribute_items]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), " "))

    if outer_markup_class is None:
        outer_markup_class = "name_list"

    format = DictionaryFormat(attribute_order, attribute_formats, seq_format,
                              default_attribute_values={"names": []},
                              dictionary_markup_class=outer_markup_class)

    format.set_xml_name("name_list_plain_style")
    return format

from typing import Any, Text, Tuple, List
import copy
import collections

from ..xml_io import XMLBase, xml_capture_caller_arguments
from .base import Format, MarkupFormat, MarkupMetadata, split_metadata, fuse_metadata, MatchAny
from .value_format import ValueFormat
from .sequence_format import SequenceFormat
from .sequence_map import SequenceMap
from .value_converters import DictionaryConverter

__all__ = ['GroupingFormat', 'StaticGroup']


class StaticGroup(XMLBase):

    def __init__(self, value):

        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.group_value_ = value
        self.xml_name_ = ""

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

    def get_xml_name(self):
        return self.xml_name_

    def set_xml_name(self, name):
        self.xml_name_ = name


class GroupingFormat(Format):

    def __init__(self,
                 key_group_formats=None,
                 converter=None,
                 key_group_sequence_format=None,
                 default_key_values=None):

        super().__init__()

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if key_group_formats is None:
            key_group_formats = []

        if converter is None:
            converter = []
        elif not isinstance(converter, collections.abc.Iterable):
            converter = [converter]

        if key_group_sequence_format is None:
            key_group_sequence_format = SequenceFormat(ValueFormat(), SequenceMap([], ""))

        if default_key_values is None:
            default_key_values = {}

        self.converter_ = list(converter)
        self.converter_.insert(0, DictionaryConverter())

        self.key_group_formats_ = copy.copy(key_group_formats)
        self.key_group_sequence_format_ = key_group_sequence_format
        self.default_key_values_ = copy.copy(default_key_values)

    def __call__(self, dictionary: dict, path: List[Tuple[int, List[Tuple[Any, Any]]]], markup_format: MarkupFormat) \
            -> Tuple[Text, MarkupMetadata]:

        dictionary, _ = split_metadata(dictionary)

        for converter in self.converter_:
            dictionary = converter(dictionary, path)

        remaining_attributes = set(dictionary.keys())
        default_key_group_index = None

        key_groups = []

        for keys, fmt in self.key_group_formats_:

            group = {}

            if isinstance(keys, StaticGroup):
                group = keys.group_value_
                key_groups.append((len(key_groups), group, fmt))
                continue

            for key in keys:

                if isinstance(key, MatchAny):
                    default_key_group_index = len(key_groups)
                    continue

                if key not in dictionary:

                    parts = key.split(".")

                    if len(parts) < 2:
                        continue

                    nested_dictionary = dictionary
                    is_nested_key = True
                    part = None

                    for part_index, part in enumerate(parts):

                        if part not in nested_dictionary:
                            is_nested_key = False
                            break

                        if part_index + 1 < len(parts):
                            nested_dictionary = nested_dictionary[part]

                    if not is_nested_key:
                        continue

                    group[part] = nested_dictionary[part]
                    continue

                remaining_attributes.remove(key)
                group[key] = dictionary[key]

            if len(keys) == 1:

                if len(group) == 1:
                    group = list(group.values())[0]
                else:
                    group = ""

            key_groups.append((len(key_groups), group, fmt))

        if default_key_group_index is not None:
            default_key_group = key_groups[default_key_group_index][1]

            for key in remaining_attributes:
                default_key_group[key] = dictionary[key]

        path_level = [(index, key_group) for index, key_group, _ in key_groups]

        formatted_values = []

        for index, entry in enumerate(key_groups):

            key_group = entry[1]
            fmt = entry[2]

            path.append((index, path_level))

            key_group_value, key_group_metadata = fmt(key_group, path, markup_format)
            key_group_value = fuse_metadata(key_group_value, key_group_metadata)

            path.pop()

            formatted_values.append(key_group_value)

        result, metadata = self.key_group_sequence_format_(formatted_values, path, markup_format)

        return result, metadata

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_


ALL_XML_CLASSES = [
    GroupingFormat,
    StaticGroup,
]

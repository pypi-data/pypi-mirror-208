from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa
import copy
import collections

from ..xml_io import XMLBase, xml_capture_caller_arguments # noqa
from .base import Format, MarkupFormat, MarkupMetadata, split_metadata, fuse_metadata, \
    prefix_merge_mode, suffix_merge_mode, MatchAny # noqa
from .value_format import ValueFormat
from .sequence_map import SequenceMap
from .sequence_format import SequenceFormat
from .value_converters import DictionaryConverter

__all__ = ['DictionaryFormat']


class DictionaryFormat(Format):

    def __init__(self,
                 attribute_order=None,
                 attribute_formats=None,
                 attribute_sequence_format=None,
                 converter=None,
                 include_keys=False,
                 default_attribute_values=None,
                 dictionary_markup_class=None):

        super().__init__()

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if converter is None:
            converter = []
        elif not isinstance(converter, collections.abc.Iterable):
            converter = [converter]

        self.converter_ = list(converter)
        self.converter_.insert(0, DictionaryConverter())

        if attribute_formats is None:
            attribute_formats = {}

        if attribute_order is None:
            attribute_order = sorted(attribute_formats.keys())

        if attribute_sequence_format is None:
            attribute_sequence_format = SequenceFormat(ValueFormat(), SequenceMap([], ""))

        if default_attribute_values is None:
            default_attribute_values = {}

        self.attribute_formats_ = copy.copy(attribute_formats)
        self.attribute_order_ = attribute_order
        self.attribute_sequence_format_ = attribute_sequence_format
        self.default_attribute_format_ = None

        for attribute_key in self.attribute_order_:
            if isinstance(attribute_key, MatchAny):
                self.default_attribute_format_ = self.attribute_formats_[attribute_key]
                break

        self.include_keys_ = include_keys
        self.default_attribute_values_ = copy.copy(default_attribute_values)
        self.dictionary_markup_class_ = dictionary_markup_class

    def __call__(self, dictionary: Any, path: List[Tuple[int, List[Tuple[Any, Any]]]], markup_format: MarkupFormat) \
            -> Tuple[Text, MarkupMetadata]:

        dictionary, _ = split_metadata(dictionary)

        for converter in self.converter_:
            dictionary = converter(dictionary, path)

        attribute_values = []
        attribute_formats = []

        default_attribute_offset = None

        remaining_attributes = set(dictionary.keys())

        for attribute_key in self.attribute_order_:

            if isinstance(attribute_key, MatchAny):
                default_attribute_offset = len(attribute_values)
                continue

            if attribute_key not in dictionary:

                if attribute_key not in self.default_attribute_values_:
                    continue

                attribute_value = self.default_attribute_values_[attribute_key]
            else:
                remaining_attributes.remove(attribute_key)
                attribute_value = dictionary[attribute_key]

            attribute_values.append((attribute_key, attribute_value))

            attribute_format = self.attribute_formats_[attribute_key]
            attribute_formats.append(attribute_format)

        if self.default_attribute_format_ is not None and default_attribute_offset is not None:

            for attribute_key in remaining_attributes:

                attribute_value = dictionary[attribute_key]
                attribute_values.insert(default_attribute_offset, (attribute_key, attribute_value))
                attribute_formats.insert(default_attribute_offset, self.default_attribute_format_)
                default_attribute_offset += 1

        formatted_attribute_values = []

        for index, attribute_format in enumerate(attribute_formats):

            attribute_key, attribute_value = attribute_values[index]

            path.append((index, attribute_values))

            attribute_value, attribute_metadata = attribute_format(attribute_value, path, markup_format)
            attribute_value = fuse_metadata(attribute_value, attribute_metadata)

            if self.include_keys_:
                formatted_attribute_values.append((attribute_key, attribute_value))
            else:
                formatted_attribute_values.append(attribute_value)

            path.pop()

        result, metadata = self.attribute_sequence_format_(formatted_attribute_values, path, markup_format)

        if result and self.dictionary_markup_class_:
            result, metadata = markup_format.apply(result, metadata, self.dictionary_markup_class_, dictionary)

        return result, metadata

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_


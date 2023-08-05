from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa
import collections

from ..xml_io import xml_capture_caller_arguments
from .base import Format, MarkupFormat, MarkupMetadata, split_metadata, join_value_metadata_sequence
from .value_format import ValueFormat
from .sequence_map import SequenceMap
from .value_converters import ListConverter
from .ellipsis import SequenceEllipsis

__all__ = ['SequenceFormat']


class SequenceFormat(Format):

    def __init__(self,
                 element_format: ValueFormat,
                 separator_map: SequenceMap,
                 sequence_markup_class: Any = None,
                 separator_markup_class: Any = None,
                 converter=None,
                 empty_substitution_value="",
                 collapse_separators=True,
                 ellipsis=None): # noqa

        super().__init__()

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if converter is None:
            converter = []
        elif not isinstance(converter, collections.abc.Iterable):
            converter = [converter]

        if ellipsis is None:
            ellipsis = SequenceEllipsis() # noqa

        self.converter_ = list(converter)
        self.converter_.insert(0, ListConverter())

        self.element_format_ = element_format
        self.separator_map_ = separator_map
        self.sequence_markup_class_ = sequence_markup_class
        self.separator_markup_class_ = separator_markup_class
        self.empty_substitution_value_ = empty_substitution_value
        self.collapse_separators_ = collapse_separators
        self.separator_substitutions_ = [("]. ", " ")]
        self.ellipsis_ = ellipsis

    # noinspection PyMethodMayBeStatic
    def is_separator_substitution(self, token, gap, separator_exception):

        index = gap + 1 - len(separator_exception)

        if index < 0:
            index = 0

        while index < gap:

            index = token.find(separator_exception, index)

            if index == -1:
                return False

            if (index < gap) and (index + len(separator_exception) > gap):
                return True

            index += 1

        return False

    def check_separator_substitutions(self, token, gap):

        for trigger_token, substitution in self.separator_substitutions_:

            if self.is_separator_substitution(token, gap, trigger_token):
                return True, substitution

        return False, None

    def __call__(self, sequence: Iterable, path: List[Tuple[int, List[Tuple[Any, Any]]]], markup_format: MarkupFormat) \
            -> Tuple[Text, MarkupMetadata]:

        sequence, _ = split_metadata(sequence)

        element_list = sequence

        for converter in self.converter_:
            element_list = converter(element_list, path)

        element_list = list(element_list)

        element_list = list(zip(range(len(element_list)), element_list))
        element_and_separator_text = [("", None)] * (len(element_list) * 2 + 1)
        element_index = 0

        for _, element in element_list:

            path.append((element_index, element_list))

            element_text, element_metadata = self.element_format_(element, path, markup_format)

            if element_text:
                element_and_separator_text[element_index * 2 + 1] = element_text, element_metadata # noqa
                element_index += 1

            path.pop()

        if element_index > 0:

            element_and_separator_text = element_and_separator_text[:element_index * 2 + 1]

            separator_positions = element_index + 1

            for separator_index in range(separator_positions):
                i = 2 * separator_index

                element_and_separator_text[i] = self.separator_map_.lookup(separator_index, separator_positions)
                element_and_separator_text[i] = markup_format.escape(element_and_separator_text[i])

                separator = element_and_separator_text[i].strip() # noqa

                if self.collapse_separators_ and element_and_separator_text[i]:

                    if i > 0:
                        if element_and_separator_text[i - 1][0].endswith(separator):
                            element_and_separator_text[i] = element_and_separator_text[i].strip(separator) # noqa

                    if i + 1 < len(element_and_separator_text):
                        if element_and_separator_text[i + 1][0].startswith(separator):
                            element_and_separator_text[i] = element_and_separator_text[i].strip(separator) # noqa

                if self.separator_substitutions_ and element_and_separator_text[i]:

                    if i > 0:

                        do_substitute, substitution = self.check_separator_substitutions(
                            element_and_separator_text[i - 1][0] + element_and_separator_text[i], # noqa
                            len(element_and_separator_text[i - 1][0]))

                        if do_substitute:
                            element_and_separator_text[i] = substitution

                    if i + 1 < len(element_and_separator_text):

                        do_substitute, substitution = self.check_separator_substitutions(
                            element_and_separator_text[i] + element_and_separator_text[i + 1][0], # noqa
                            len(element_and_separator_text[i]))

                        if do_substitute:
                            element_and_separator_text[i] = substitution

                element_and_separator_text[i] = element_and_separator_text[i], MarkupMetadata() # noqa

        element_and_separator_text = self.ellipsis_(element_and_separator_text)

        if self.separator_markup_class_:

            for separator_index in range(element_index + 1):
                i = 2 * separator_index

                if not element_and_separator_text[i][0]:
                    continue

                separator = markup_format.apply(element_and_separator_text[i][0], element_and_separator_text[i][1],
                                                self.separator_markup_class_, element_and_separator_text[i][0])
                element_and_separator_text[i] = separator

        result, metadata = join_value_metadata_sequence(element_and_separator_text)

        if not result:
            result = markup_format.escape(self.empty_substitution_value_)
            metadata = MarkupMetadata()

        if result and self.sequence_markup_class_:
            element_list = list(zip(*element_list))[1] if element_list else []
            result, metadata = markup_format.apply(result, metadata, self.sequence_markup_class_, element_list)

        return result, metadata

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

    """
    
        self.converter_ = list(converter)
        self.converter_.insert(0, ListConverter())

        self.element_format_ = element_format
        self.separator_map_ = separator_map
        self.sequence_markup_class_ = sequence_markup_class
        self.empty_substitution_value_ = empty_substitution_value
        self.collapse_separators_ = collapse_separators
        self.separator_substitutions_ = [("]. ", " ")]
    """

    def __hash__(self):
        return hash((self.separator_map_, self.sequence_markup_class_, self.empty_substitution_value_,
                     self.collapse_separators_, tuple(self.separator_substitutions_)))

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, SequenceFormat):
            return False

        return self.converter_ == other.converter_ and \
            self.element_format_ == other.element_format_ and \
            self.sequence_markup_class_ == other.sequence_markup_class_ and \
            self.empty_substitution_value_ == other.empty_substitution_value_ and \
            self.collapse_separators_ == other.collapse_separators_ and \
            self.separator_substitutions_ == other.separator_substitutions_

    def __ne__(self, other):
        return not self.__eq__(other)

from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa
import copy
import collections

from ..xml_io import XMLBase, xml_capture_caller_arguments # noqa
from .base import Format, MarkupFormat, MarkupMetadata, MatchAny, split_metadata, join_value_metadata_sequence # noqa
from .value_converters import DictionaryConverter

__all__ = ['SwitchFormat']


class SwitchFormat(Format):

    def __init__(self,
                 case_formats=None,
                 switch_markup_class=None,
                 converter=None,
                 empty_substitution_value="",
                 use_stream_format=True):

        super().__init__()

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if case_formats is None:
            case_formats = {}

        self.default_case_format_ = None

        for case_key, case_format in case_formats.items():

            if isinstance(case_key, MatchAny):
                self.default_case_format_ = case_format
                break

        if converter is None:
            converter = []
        elif not isinstance(converter, collections.abc.Iterable):
            converter = [converter]

        self.converter_ = list(converter)
        self.converter_.insert(0, DictionaryConverter())

        self.case_formats_ = copy.copy(case_formats)
        self.empty_substitution_value_ = empty_substitution_value
        self.switch_markup_class_ = switch_markup_class
        self.use_stream_format_ = use_stream_format

    def __call__(self, dictionary: Any, path: List[Tuple[int, List[Tuple[Any, Any]]]], markup_format: MarkupFormat) \
            -> Tuple[Text, MarkupMetadata]:

        dictionary, _ = split_metadata(dictionary)

        for converter in self.converter_:
            dictionary = converter(dictionary, path)

        if self.use_stream_format_:
            switch_type = dictionary.get("type", None)
            switch_value = dictionary.get("value", None)
        else:
            switch_type = dictionary.get("__type__", None)

            if switch_type:
                switch_value = dictionary.get(switch_type, None)
            else:
                switch_value = None

        switch_format = self.case_formats_.get(switch_type, self.default_case_format_)

        result = ""
        metadata = MarkupMetadata()

        if switch_format:
            result, metadata = switch_format(switch_value, path, markup_format)

        if not result:
            result = markup_format.escape(self.empty_substitution_value_)
            metadata = MarkupMetadata()

        if result and self.switch_markup_class_:
            result, metadata = markup_format.apply(result, metadata, self.switch_markup_class_, dictionary)

        return result, metadata

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

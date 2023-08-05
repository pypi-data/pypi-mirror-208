from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa
import collections

from ..xml_io import XMLBase, xml_capture_caller_arguments # noqa
from .base import Format, MarkupMetadata, split_metadata, prefix_merge_mode, suffix_merge_mode

__all__ = ['ValueFormat']


class ValueFormat(Format):
    """Applies a converter, adds inner markup, adds a prefix and a suffix
       and applies outer markup to a value.

        outer_markup_class( prefix + inner_markup_class(transformation(element)) + suffix )
    """

    def __init__(self, prefix="", suffix="", inner_markup_class=None, outer_markup_class=None,
                 prefix_markup_class=None, suffix_markup_class=None, converter=None,
                 inner_empty_substitution_value="", outer_empty_substitution_value="", trim_whitespace=True,
                 do_escape=True):

        super().__init__()

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if converter is None:
            converter = []
        elif not isinstance(converter, collections.abc.Iterable):
            converter = [converter]

        self.converter_ = list(converter)
        self.prefix_ = prefix
        self.suffix_ = suffix
        self.inner_markup_class_ = inner_markup_class
        self.outer_markup_class_ = outer_markup_class
        self.prefix_markup_class_ = prefix_markup_class
        self.suffix_markup_class_ = suffix_markup_class
        self.inner_empty_substitution_value_ = inner_empty_substitution_value
        self.outer_empty_substitution_value_ = outer_empty_substitution_value
        self.trim_whitespace_ = trim_whitespace
        self.do_escape_ = do_escape

    def __call__(self, value: Any, path: List[Tuple[int, List[Tuple[Any, Any]]]], markup_format) \
            -> Tuple[Any, MarkupMetadata]:

        value, metadata = split_metadata(value, create_metadata=True)

        for converter in self.converter_:
            value = converter(value, path)

        if self.trim_whitespace_:
            value = value.strip()

        if not value:
            value = markup_format.escape(self.inner_empty_substitution_value_)
            metadata = MarkupMetadata()

        if value:

            if self.do_escape_:
                value = markup_format.escape(value)

            if self.inner_markup_class_:
                value, metadata = markup_format.apply(value, metadata, self.inner_markup_class_, value)

            prefix = markup_format.escape(self.prefix_)

            if prefix and self.prefix_markup_class_:
                prefix, prefix_metadata = markup_format.apply(prefix, MarkupMetadata(), self.prefix_markup_class_,
                                                              self.prefix_)
                metadata.merge(prefix_metadata, mode=prefix_merge_mode(prefix_length=len(prefix)))

            suffix = markup_format.escape(self.suffix_)

            if suffix and self.suffix_markup_class_:
                suffix, suffix_metadata = markup_format.apply(suffix, MarkupMetadata(), self.suffix_markup_class_,
                                                              self.suffix_)
                metadata.merge(suffix_metadata, mode=suffix_merge_mode(target_length=len(prefix) + len(value)))

            value = prefix + value + suffix

        if not value:
            value = markup_format.escape(self.outer_empty_substitution_value_)
            metadata = MarkupMetadata()

        if value and self.outer_markup_class_:
            value, metadata = markup_format.apply(value, metadata, self.outer_markup_class_, value)

        return value, metadata

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

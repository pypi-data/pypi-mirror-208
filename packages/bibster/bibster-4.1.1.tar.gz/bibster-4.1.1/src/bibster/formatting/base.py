from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa

from .markup import MarkupFormat, MarkupMetadata, split_metadata, fuse_metadata, join_value_metadata_sequence, \
    prefix_merge_mode, suffix_merge_mode # noqa

from ..xml_io import XMLBase

__all__ = ['MatchAny', 'Format']


class MatchAny(XMLBase):

    def __init__(self):
        self.xml_name_ = ""

    def __hash__(self):
        return 1

    def __eq__(self, other):
        return isinstance(other, MatchAny)

    def __ne__(self, other):
        return not isinstance(other, MatchAny)

    def get_xml_name(self):
        return self.xml_name_

    def set_xml_name(self, name):
        self.xml_name_ = name


class Format(XMLBase):

    """Base class for all formats.

    A format is a callable that translates a value to text and accompanying markup data.

    .. automethod:: __call__
    """

    def __init__(self):
        self.xml_name_ = ""

    def __call__(self, value: Any, path: List[Tuple[int, List[Tuple[Any, Any]]]], markup_format: MarkupFormat) \
            -> Tuple[Text, MarkupMetadata]:
        """Format the provided value using a path and markup_format.

        :param value: A value of interest
        :param path: A path
        :param markup_format: The markup format to be used
        :return: A tuple consisting of the output text and accompanying markup data
        """
        return "", MarkupMetadata()

    def get_xml_keyword_assignments(self):
        return []

    def get_xml_name(self):
        return self.xml_name_

    def set_xml_name(self, name):
        self.xml_name_ = name


ALL_XML_CLASSES = [
    MatchAny,
    Format
]
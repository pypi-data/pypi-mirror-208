import json
from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa
from ..xml_io import escape_xml_text

__all__ = ['MarkupFormat', 'HTMLMarkup', 'MarkupMetadata', 'version_from_string', 'string_from_version',
           'compare_version']


def version_from_string(string):
    """Converts a string to a markup version.

    :param string: A string of the format YYYYMMDD
    :return: A tuple of year, month, day
    """
    string = string.strip()

    year = int(string[:4])
    month = int(string[4:6])
    day = int(string[6:8])

    return year, month, day


def string_from_version(version):
    """Formats a version tuple as a string

    :param version:
    :return: A string of the format YYYYMMDD
    """

    result = "{:04d}{:02d}{:02d}".format(version[0], version[1], version[2])
    return result


def version_to_serial_days(version):
    """Converts a version to the absolute number of days.
    :param version: A tuple (year, month, day)
    :return: A number
    """
    return version[0] * 365 + version[1] * 30 + version[2]


def compare_version(left_version, right_version):
    """Compares to versions by converting each to an absolute number days.

    :return: A numeric value representing `left_version < right_version`
    """
    return version_to_serial_days(left_version) - version_to_serial_days(right_version)


class MergeMode(object):

    def __init__(self, **kwargs):
        self.kwargs_ = kwargs
        self.locations_ = lambda target, source, **inner_kwargs: target.extend(source)

    def locations(self, target, source):
        self.locations_(target, source, **self.kwargs_)


def merge_locations_from_prefix(target, source, prefix_length):

    if target == source:
        source = list(target)

    x = prefix_length

    for i, value in enumerate(target):
        target[i] = value + x

    for i, value in enumerate(reversed(source)):
        target.insert(0, value)


def prefix_merge_mode(prefix_length):
    mode = MergeMode(prefix_length=prefix_length)
    mode.locations_ = merge_locations_from_prefix
    return mode


def merge_locations_from_suffix(target, source, target_length):

    if target == source:
        source = list(target)

    x = target_length

    for value in source:
        target.append(value + x)


def suffix_merge_mode(target_length):
    mode = MergeMode(target_length=target_length)
    mode.locations_ = merge_locations_from_suffix
    return mode


class MarkupMetadata(object):
    """A collection of metadata.

    """

    def __init__(self, bookmarks=None):

        if bookmarks is None:
            bookmarks = {}

        self.bookmarks_ = bookmarks

    def sorted_locations_for_bookmark(self, key, reverse=True):

        locations = self.bookmarks_.get(key, None)

        if locations is None:
            return []

        return sorted(locations, reverse=reverse)

    def merge(self, metadata, mode=None):

        if mode is None:
            mode = MergeMode()

        for key, other_locations in metadata.bookmarks_.items():

            locations = self.bookmarks_.get(key, None)

            if locations is None:
                locations = []
                self.bookmarks_[key] = locations

            mode.locations(locations, other_locations)

    def to_json(self):
        return json.dumps({"bookmarks": self.bookmarks_})

    @staticmethod
    def from_json(string):
        dictionary = json.loads(string)
        bookmarks = dictionary.get("bookmarks", {})
        return MarkupMetadata(bookmarks)


def join_value_metadata_sequence(sequence, separator=""):

    result = ""
    joined_metadata = MarkupMetadata()
    index = 0
    for value, metadata in sequence:

        if metadata:
            joined_metadata.merge(metadata, mode=suffix_merge_mode(target_length=len(result)))

        if index:
            result += separator

        result += value

        index += 1

    return result, joined_metadata


class AnnotatedValue(object):

    def __init__(self, value, metadata=None):

        if metadata is None:
            metadata = MarkupMetadata()

        self.value_ = value
        self.metadata_ = metadata


def split_metadata(value, create_metadata=False):

    if isinstance(value, AnnotatedValue):
        return value.value_, value.metadata_

    return value, MarkupMetadata() if create_metadata else None


def fuse_metadata(value, metadata):
    return AnnotatedValue(value, metadata)


class MarkupFormat(object):
    """A class for formatting a value as markup.

    """

    @property
    def version(self):
        return 2019, 2, 1

    def apply(self, value: Any, metadata: MarkupMetadata, markup_class: Text, original_value: Any) \
            -> Tuple[Text, MarkupMetadata]:
        return value, metadata

    def escape(self, value):
        return value


class HTMLMarkup(MarkupFormat):

    class Entry:
        def __init__(self, tag_name="span", attributes=None):

            if attributes is None:
                attributes = []

            self.tag_name_ = tag_name
            self.attributes_ = list(attributes)

        def __call__(self, value, metadata, original_value):
            attributes = []

            for name, attribute_value in self.attributes_:

                attribute_metadata = MarkupMetadata()

                if callable(attribute_value):
                    attribute_value, attribute_metadata = attribute_value(name, value, metadata, original_value)

                attributes.append(("{}=\"{}\"".format(name, attribute_value), attribute_metadata))

            attributes, metadata = join_value_metadata_sequence(attributes, " ")

            if attributes:
                attributes = " " + attributes
                metadata.merge(metadata, mode=prefix_merge_mode(prefix_length=1))

            result = "<{}{}>{}</{}>".format(self.tag_name_, attributes, value, self.tag_name_)
            metadata.merge(metadata, mode=prefix_merge_mode(prefix_length=1 + len(self.tag_name_)))

            return result, metadata

    @property
    def version(self):
        return 2019, 2, 1

    def __init__(self):
        self.entries_ = {}
        self.default_ = None

    def map(self, markup_class, tag_name, attributes):
        entry = HTMLMarkup.Entry(tag_name, attributes)

        if markup_class is None:
            self.default_ = entry
        else:
            self.entries_[markup_class] = entry

    def map_function(self, markup_class, markup_function):

        if markup_class is None:
            self.default_ = markup_function
        else:
            self.entries_[markup_class] = markup_function

    def apply(self, value: Any, metadata: MarkupMetadata, markup_class: Text, original_value: Any) \
            -> Tuple[Text, MarkupMetadata]:
        entry = self.entries_.get(markup_class, self.default_)

        if not entry:
            return value, MarkupMetadata()

        value, metadata = entry(value, metadata, original_value)
        return value, metadata

    def escape(self, value):
        if not value:
            return value

        return escape_xml_text(value)

from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa
import copy

from ..xml_io import XMLBase, xml_capture_caller_arguments
from .base import Format, MarkupFormat, MarkupMetadata, split_metadata

__all__ = ['Key', 'PreviousKey', 'Condition', 'NotBlank', 'LengthEquals', 'LengthGreaterThan', 'Predicate',
           'PredicateFormat']


class Key(XMLBase):

    @property
    def is_optional(self):
        return self.is_optional_

    def __init__(self, is_optional=True):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.is_optional_ = is_optional
        self.xml_name_ = ""

    def __call__(self, path):
        return False, None

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

    def get_xml_name(self):
        return self.xml_name_

    def set_xml_name(self, name):
        self.xml_name_ = name


class PreviousKey(Key):

    def __init__(self, is_optional=True):
        super().__init__(is_optional)
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

    def __call__(self, path):

        if not path:
            return False, None

        index, arguments = path[-1]

        if index == 0:
            return False, None

        return True, arguments[index - 1]


class Condition(XMLBase):

    def __init__(self):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.xml_name_ = ""

    def __call__(self, value):
        return True

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

    def get_xml_name(self):
        return self.xml_name_

    def set_xml_name(self, name):
        self.xml_name_ = name


class NotBlank(Condition):

    def __init__(self, converter=None):

        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.converter_ = converter

    def __call__(self, value):

        if self.converter_:
            value = self.converter_(value, [])

        try:
            return len(value.strip()) != 0
        except ValueError:
            return False


class LengthEquals(Condition):

    def __init__(self, value, converter=None):

        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.value_ = value
        self.converter_ = converter

    def __call__(self, value):

        if self.converter_:
            value = self.converter_(value, [])

        try:
            return len(list(value)) == self.value_
        except ValueError:
            return False


class LengthGreaterThan(Condition):

    def __init__(self, value, converter=None):

        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.value_ = value
        self.converter_ = converter

    def __call__(self, value):

        if self.converter_:
            value = self.converter_(value, [])

        try:
            return len(list(value)) > self.value_
        except ValueError:
            return False


class Predicate(XMLBase):

    AND_OPERATOR = 1
    OR_OPERATOR = 2

    def __init__(self, key_conditions: List[Tuple[Key, Condition]]=None, operator=AND_OPERATOR):
        super().__init__()

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if key_conditions is None:
            key_conditions = []

        self.key_conditions_ = copy.copy(key_conditions)
        self.operator_ = operator
        self.xml_name_ = ""

    def __call__(self, value: Any, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        for key, condition in self.key_conditions_:

            did_match, key_value = key(path)

            if not did_match:
                if key.is_optional:
                    continue

                return False

            condition_value = condition(key_value)

            if self.operator_ == Predicate.AND_OPERATOR:
                if not condition_value:
                    return False

            if self.operator_ == Predicate.OR_OPERATOR:
                if condition_value:
                    return True

        if self.operator_ == Predicate.AND_OPERATOR:
                return True

        if self.operator_ == Predicate.OR_OPERATOR:
                return False

        return False

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

    def get_xml_name(self):
        return self.xml_name_

    def set_xml_name(self, name):
        self.xml_name_ = name


class PredicateFormat(Format):

    def __init__(self,
                 predicate_mappings: List[Tuple[Predicate, Format]]=None,
                 default_format=None,
                 predicate_markup_class=None):

        super().__init__()

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if predicate_mappings is None:
            predicate_mappings = []

        self.predicate_mappings_ = copy.copy(predicate_mappings)
        self.default_format_ = default_format
        self.predicate_markup_class_ = predicate_markup_class

    def __call__(self, value: Any, path: List[Tuple[int, List[Tuple[Any, Any]]]], markup_format: MarkupFormat) -> Tuple[Text, MarkupMetadata]:

        unwrapped_value, metadata = split_metadata(value)

        for predicate, format in self.predicate_mappings_:
            if predicate(unwrapped_value, path):
                result, metadata = format(value, path, markup_format)
                if result and self.predicate_markup_class_:
                    result, metadata = markup_format.apply(result, metadata, self.predicate_markup_class_, value)

                return result, metadata

        if self.default_format_:
            result, metadata = self.default_format_(value, path, markup_format)
            if result and self.predicate_markup_class_:
                result, metadata = markup_format.apply(result, metadata, self.predicate_markup_class_, value)

            return result, metadata

        return "", MarkupMetadata()

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_


ALL_XML_CLASSES = [

    Key,
    PreviousKey,
    Condition,
    LengthGreaterThan,
    NotBlank,
    LengthEquals,
    Predicate,
    PredicateFormat,
]

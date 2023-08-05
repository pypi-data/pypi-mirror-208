from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa
import copy, re, datetime, collections

from django.utils.dateparse import parse_datetime

from ..xml_io import XMLBase, xml_capture_caller_arguments

from .titlecase import titlecase, paragraph
from .base import MatchAny

__all__ = ['ValueConverter', 'TitlecaseConverter', 'ParagraphConverter', 'TrimConverter', 'RangeFromPairConverter',
           'FlattenDictionaryConverter', 'EmbedInDictionaryConverter', 'SubstituteByRegexpConverter',
           'SplitByRegexpConverter', 'DateConverter', 'IndexedElement', 'JsonStreamValueConverter',
           'ListConverter', 'DictionaryConverter', 'DecimalConverter', 'OrdinalConverter', 'MappingConverter',
           'GivenNameAndInitialConverter']


class ValueConverter(XMLBase):

    def __init__(self):
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.xml_name_ = ""

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):
        return value

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

    def get_xml_name(self):
        return self.xml_name_

    def set_xml_name(self, name):
        self.xml_name_ = name


class TitlecaseConverter(ValueConverter):

    def __init__(self, min_n_uppercase=2):

        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.min_n_uppercase_ = min_n_uppercase

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):
        value = titlecase(value, min_n_uppercase=self.min_n_uppercase_)
        return value

    def __hash__(self):
        return hash(self.min_n_uppercase_)

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, TitlecaseConverter):
            return False

        return self.min_n_uppercase_ == other.min_n_uppercase_

    def __ne__(self, other):
        return not self.__eq__(other)


class ParagraphConverter(ValueConverter):

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        value = paragraph(value)
        return value

    def __hash__(self):
        return hash(self.__class__)

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, ParagraphConverter):
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class TrimConverter(ValueConverter):

    def __init__(self, trim_characters=" \t\r\n"):

        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.trim_characters_ = trim_characters

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):
        value = value.strip()
        return value

    def __hash__(self):
        return hash(self.trim_characters_)

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, TrimConverter):
            return False

        return self.trim_characters_ == other.trim_characters_

    def __ne__(self, other):
        return not self.__eq__(other)


class RangeFromPairConverter(ValueConverter):

    def __init__(self, separator="", regular_prefix="", regular_suffix="", simple_prefix="", simple_suffix="", do_collapse=True):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        self.separator_ = separator
        self.regular_prefix_ = regular_prefix
        self.regular_suffix_ = regular_suffix
        self.simple_prefix_ = simple_prefix
        self.simple_suffix_ = simple_suffix
        self.do_collapse_ = do_collapse

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        if len(value) != 2:
            return ""

        if value[0] is None and value[1] is None:
            return ""

        first = value[0] if value[0] is not None else value[1]
        last = value[1] if value[1] is not None else value[0]

        try:
            first_number = int(first)
            last_number = int(last)

            if first_number > last_number:
                return ""

        except ValueError:
            pass

        if first != last or not self.do_collapse_:
            result = "{}{}{}{}{}".format(self.regular_prefix_, first, self.separator_, last, self.regular_suffix_)
        else:
            result = "{}{}{}".format(self.simple_prefix_, first, self.simple_suffix_)

        return result

    def __hash__(self):
        return hash((self.separator_, self.regular_prefix_, self.regular_suffix_, self.simple_prefix_, self.simple_suffix_))

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, RangeFromPairConverter):
            return False

        return self.separator_ == other.separator_ and \
                self.regular_prefix_ == other.regular_prefix_ and \
                self.regular_suffix_ == other.regular_suffix_ and \
                self.simple_prefix_ == other.simple_prefix_ and \
                self.simple_suffix_ == other.simple_suffix_

    def __ne__(self, other):
        return not self.__eq__(other)


class FlattenDictionaryConverter(ValueConverter):

    def __init__(self, attribute_order=None, include_keys=False, default_attribute_values=None):

        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if attribute_order is None:
            attribute_order = [MatchAny()]

        if default_attribute_values is None:
            default_attribute_values = {}

        self.attribute_order_ = attribute_order
        self.include_keys_ = include_keys
        self.default_attribute_values_ = copy.copy(default_attribute_values)

    def __call__(self, dictionary, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        attribute_values = []

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

            if self.include_keys_:
                value = (attribute_key, attribute_value)
            else:
                value = attribute_value

            attribute_values.append(value)

        if default_attribute_offset is not None:

            for attribute_key in remaining_attributes:

                attribute_value = dictionary[attribute_key]

                if self.include_keys_:
                    value = (attribute_key, attribute_value)
                else:
                    value = attribute_value

                attribute_values.insert(default_attribute_offset, value)
                default_attribute_offset += 1

        result = attribute_values
        return result


class EmbedInDictionaryConverter(ValueConverter):

    def __init__(self, attribute_name):

        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        self.attribute_name_ = attribute_name

    def __call__(self, dictionary, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        result = {
            self.attribute_name_: dictionary
        }

        return result


class SubstituteByRegexpConverter(ValueConverter):

    def __init__(self, pattern_string, replacement_string):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        self.pattern_ = re.compile(pattern_string, re.UNICODE)
        self.replacement_string_ = replacement_string

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        value = self.pattern_.sub(self.replacement_string_, value)
        return value


class SplitByRegexpConverter(ValueConverter):

    def __init__(self, pattern_string):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        self.pattern_ = re.compile(pattern_string, re.UNICODE)

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        matches = []

        pos = 0

        while pos < len(value):

            match = self.pattern_.match(value, pos=pos)

            if match is None:
                break

            matches.append(match)

            pos = match.endpos

        return matches


MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December"]


class DateConverter(ValueConverter):

    def __init__(self):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        if isinstance(value, str):
            value = parse_datetime(value)

        if not isinstance(value, datetime.datetime):
            return ""

        date = value.date()

        year = date.year
        month = date.month
        day = date.day

        if year and month and day:

            try:
                date = datetime.date(year, month, day)
            except ValueError:
                return ""

            month = MONTH_NAMES[month - 1]

            result = "{:d} {} {:d}".format(day, month, year)
            return result
        else:
            return ""

    def __hash__(self):
        return hash(DateConverter)

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, DateConverter):
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class IndexedElement(ValueConverter):

    def __init__(self, element_key):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        self.element_key_ = element_key

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):
        return value[self.element_key_]

    def __hash__(self):
        return hash((self.element_key_,))

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, IndexedElement):
            return False

        return self.element_key_ == other.element_key_

    def __ne__(self, other):
        return not self.__eq__(other)


class JsonStreamValueConverter(ValueConverter):

    def __init__(self):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        if not isinstance(value, list) and not isinstance(value, collections.abc.Iterable):
            value = []

        for element in value:

            if not isinstance(element, dict) or "value" not in element:
                continue

            element["value"]

        return value

    def __hash__(self):
        return hash(ListConverter)

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, ListConverter):
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class ListConverter(ValueConverter):

    def __init__(self):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        if not isinstance(value, list) and not isinstance(value, collections.abc.Iterable):
            value = []

        return value

    def __hash__(self):
        return hash(ListConverter)

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, ListConverter):
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class DictionaryConverter(ValueConverter):

    def __init__(self):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        if not isinstance(value, dict):
            value = {}

        return value

    def __hash__(self):
        return hash(DictionaryConverter)

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, DictionaryConverter):
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class DecimalConverter(ValueConverter):

    def __init__(self, strict=True):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        self.strict_ = strict

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        is_list = False

        if not isinstance(value, str):
            try:
                value = list(value)
                is_list = True
            except TypeError:
                pass

        if not is_list:
            value = [value]

        result = []

        for element in value:
            try:
                element = "{:d}".format(element)
            except ValueError:
                if self.strict_:
                    element = ""
            except TypeError:
                if self.strict_:
                    element = ""

            result.append(element)

        if not is_list:
            result = result[0]

        return result

    def __hash__(self):
        return hash((self.strict_,))

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, DecimalConverter):
            return False

        return self.strict_ == other.strict_

    def __ne__(self, other):
        return not self.__eq__(other)


class OrdinalConverter(ValueConverter):

    def __init__(self, strict=True):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        self.strict_ = strict

    def ordinal_for(self, number):

        if number:

            try:
                number = int(number)
            except ValueError:
                if self.strict_:
                    return ""
            except TypeError:
                if self.strict_:
                    return ""

            if number > 1:

                number_root = number % 10

                if number_root == 1:
                    number_root = "st"
                elif number_root == 2:
                    number_root = "nd"
                elif number_root == 3:
                    number_root = "rd"
                else:
                    number_root = "th"

                number = str(number) + number_root
        else:
            number = ""

        return number

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        is_list = False

        if not isinstance(value, str):
            try:
                value = list(value)
                is_list = True
            except TypeError:
                pass

        if not is_list:
            value = [value]

        result = []

        for element in value:
            element = self.ordinal_for(element)
            result.append(element)

        if not is_list:
            result = result[0]

        return result

    def __hash__(self):
        return hash((self.strict_,))

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, OrdinalConverter):
            return False

        return self.strict_ == other.strict_

    def __ne__(self, other):
        return not self.__eq__(other)


class MappingConverter(ValueConverter):

    def __init__(self, mappings=None, default_mapping=""):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if mappings is None:
            mappings = {}

        self.mappings_ = mappings
        self.default_mapping_ = default_mapping

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        value = self.mappings_.get(value, self.default_mapping_)
        return value

    def __hash__(self):
        return hash((tuple(self.mappings_.items()), self.default_mapping_))

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, MappingConverter):
            return False

        return self.mappings_ == other.mappings_ and \
                self.default_mapping_ == other.default_mapping_

    def __ne__(self, other):
        return not self.__eq__(other)


class GivenNameAndInitialConverter(ValueConverter):

    def __call__(self, value, path: List[Tuple[int, List[Tuple[Any, Any]]]]):

        result = []
        parts = []

        for part in value.split():
            fragments = [p for p in part.split(".") if p]

            if not fragments:
                continue

            if fragments[0] == part:
                parts.append(part)
                continue

            for f in fragments:
                parts.append(f + ".")

        for part in parts:

            if part.endswith(".") or len(part) == 1:
                result.append(part.strip(".") + ".")
            else:
                result.append(part[0] + ".")

        return result

    def __hash__(self):
        return hash(GivenNameAndInitialConverter)

    def __eq__(self, other):

        if self is other:
            return True

        if not isinstance(other, GivenNameAndInitialConverter):
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


ALL_XML_CLASSES = [
    ValueConverter,
    TitlecaseConverter,
    ParagraphConverter,
    TrimConverter,
    RangeFromPairConverter,
    FlattenDictionaryConverter,
    EmbedInDictionaryConverter,
    SubstituteByRegexpConverter,
    SplitByRegexpConverter,
    DateConverter,
    IndexedElement,
    ListConverter,
    DictionaryConverter,
    DecimalConverter,
    OrdinalConverter,
    MappingConverter,
    GivenNameAndInitialConverter,
]
from typing import Any, Iterable, Text, Tuple, List, Sequence, Mapping # noqa

from ..xml_io import XMLBase, xml_capture_caller_arguments

__all__ = ['WordSubstitution', 'DictionaryRule', 'PrefixRule', 'DefaultTitlecaseRule', 'TitlecaseRule', 'titlecase',  # noqa
           'paragraph']


class WordSubstitution(XMLBase):

    def __init__(self):

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.xml_name_ = ""

    def __call__(self, word, previous, next, position): # noqa
        return True, word

    def get_xml_keyword_assignments(self):
        return self.xml_keyword_assignments_

    def get_xml_name(self):
        return self.xml_name_

    def set_xml_name(self, name):
        self.xml_name_ = name


class DictionaryRule(WordSubstitution):

    def __init__(self, dictionary, non_applicable_positions=None):

        super().__init__()

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        if non_applicable_positions is None:
            non_applicable_positions = []

        self.dictionary_ = dict()
        self.non_applicable_positions_ = non_applicable_positions

        for key, value in dictionary.items():
            key = key.lower()
            self.dictionary_[key] = value

    def __call__(self, word, previous, next, position): # noqa

        key = word.lower()

        if key not in self.dictionary_ or position in self.non_applicable_positions_:
            return False, word

        return True, self.dictionary_[key]

    @staticmethod
    def from_list(words, non_applicable_positions=None):

        dictionary = {}

        for word in words:
            dictionary[word.lower()] = word

        return DictionaryRule(dictionary, non_applicable_positions)


class PrefixRule(WordSubstitution):

    def __init__(self, prefix, operator):

        super().__init__()

        self.xml_keyword_assignments_ = xml_capture_caller_arguments()

        self.prefix_ = prefix
        self.operator_ = operator

    def __call__(self, word, previous, next, position): # noqa

        key = word.lower()

        if not key.startswith(self.prefix_):
            return False, word

        return True, self.operator_(word)


class DefaultTitlecaseRule(WordSubstitution): # noqa

    def __call__(self, word, previous, next, position): # noqa

        if not word.isupper():
            word = word.title()

        return True, word


TITLECASE_RULES = [ # noqa

    DictionaryRule.from_list(
        ["a", "an", "the", "and", "but", "for", "at", "by", "from", "in", "to", "on", "of", "during", "without",
         "under", "over"],
        [0]),

    PrefixRule("mc", lambda word: "Mc" + word[2:].title()),
    PrefixRule("mac", lambda word: "Mac" + word[2:].title()),
    DefaultTitlecaseRule()
]


class TitlecaseRule(WordSubstitution): # noqa

    def __init__(self):
        super().__init__()
        self.xml_keyword_assignments_ = xml_capture_caller_arguments()
        self.particles_ = {"a", "an", "the", "and", "but", "or", "for", "at", "by", "from", "with", "under", "over",
                           "in", "to", "on", "of", "as", "et", "al", "s"}
        self.prefix_rules_ = [
            PrefixRule("mc", lambda word: "Mc" + word[2:].title()),
            PrefixRule("mac", lambda word: "Mac" + word[2:].title()),
        ]

    def apply_prefix_rules(self, word, previous, next, position): # noqa

        for prefix in self.prefix_rules_:

            did_apply, result = prefix(word, previous, next, position)

            if did_apply:
                return True, result

        return False, word

    def __call__(self, word, previous, next, position): # noqa

        if not word.isupper():

            key = word.lower()

            if key.strip(".:,") in self.particles_ and position != 0 and not previous.endswith(":"):
                return True, key

            did_apply, word = self.apply_prefix_rules(word, previous, next, position)

            if did_apply:
                return True, word

            word = word.title()

            if word.endswith("'S"):
                word = word[:-1] + "s"

            return True, word

        return False, word


TITLECASE_RULE = TitlecaseRule() # noqa
SEPARATORS = [".", ":", ",", "-"]


def titlecase(value, min_n_uppercase=2): # noqa

    result = []
    words = value.split()

    """
    for part in value.split():

        last = 0
        pos = 0

        for character in part:

            fragment = None
            separator = None

            if character in SEPARATORS:
                fragment = part[last:pos]
                separator = character
                last = pos + 1

            pos += 1

            if fragment:
                words.append(fragment)

            if separator:
                words.append(separator)

        fragment = part[last:pos]

        if fragment:
            words.append(fragment)
    """

    is_shouting = True

    for index, word in enumerate(words):

        previous = words[index - 1] if index > 0 else None
        next = words[index + 1] if index + 1 < len(words) else None # noqa

        _, word = TITLECASE_RULE(word, previous, next, index)

        result.append(word)

        is_shouting = is_shouting and (len(word) < 2 or word.isupper())

    if is_shouting and len(result) >= min_n_uppercase:

        for index, word in enumerate(result):

            previous = result[index - 1].lower() if index > 0 else None
            next = result[index + 1].lower() if index + 1 < len(result) else None # noqa

            _, word = TITLECASE_RULE(word.lower(), previous, next, index)
            result[index] = word

    merged_result = []

    for index, word in enumerate(result):

        if word in SEPARATORS and merged_result:
            merged_result[-1] = merged_result[-1] + word
        else:
            merged_result.append(word)

    result = " ".join(merged_result)
    return result


def paragraph(value):

    result = []
    words = value.split()

    apply_titlecase = True # noqa

    for word in words:

        if apply_titlecase:

            if not word.isupper():
                word = word.title()

        apply_titlecase = word.endswith(".") # noqa
        result.append(word)

    result = " ".join(words)
    return result

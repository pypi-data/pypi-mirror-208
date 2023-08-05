from typing import Optional

from .formatting import *
from .identifiers import *
from collections import OrderedDict

__all__ = [
    'apply_name_prefix',
    'harvard_style',
    'family_name_harvard_style',
    'given_names_and_initials_harvard_style',
    'person_harvard_style',
    'organisation_name_harvard_style',
    'organisation_harvard_style',
    'name_harvard_style',
    'name_role_harvard_style',
    'name_list_harvard_style',
    'title_harvard_style',
    'paragraph_harvard_style',
    'year_harvard_style',
    'isbn_harvard_style',
    'medium_harvard_style',
    'volume_number_harvard_style',
    'issue_number_or_name_harvard_style',
    'issue_harvard_style',
    'pages_harvard_style',
    'publication_status_harvard_style',
    'publisher_harvard_style',
    'repository_name_harvard_style',
    'edition_harvard_style',
    'label_harvard_style',
    'names_year_title_group_harvard_style',
    'issue_pages_and_identifier_harvard_style',
    'book_and_pages_harvard_style',
    'identifier_harvard_style',
    'scale_harvard_style',
    'identifier_scale_harvard_style',
    'doi_harvard_style',
    'access_date_harvard_style',
    'url_reference_harvard_style',
    'series_harvard_style',
    'primary_sequence_format',
    'journal_article_harvard_style',
    'preprint_article_harvard_style',
    'book_harvard_style',
    'book_chapter_harvard_style',
    'proceedings_article_harvard_style',
    'published_standard_harvard_style',
    'patent_harvard_style',
    'report_harvard_style',
    'map_harvard_style',
    'website_harvard_style'
]


def apply_name_prefix(dictionary, prefix):

    for value in dictionary.values():
        value.set_xml_name(prefix + value.get_xml_name())


def harvard_style(label_mode=False):

    case_formats = OrderedDict([
        ("journal_article", journal_article_harvard_style(label_mode=label_mode)),
        ("preprint_article", preprint_article_harvard_style(label_mode=label_mode)),
        ("book_chapter", book_chapter_harvard_style(label_mode=label_mode)),
        ("book", book_harvard_style(label_mode=label_mode)),
        ("proceedings_article", proceedings_article_harvard_style(label_mode=label_mode)),
        ("patent", patent_harvard_style(label_mode=label_mode)),
        ("report", report_harvard_style(label_mode=label_mode)),
        ("map", map_harvard_style(label_mode=label_mode)),
        ("website", website_harvard_style(label_mode=label_mode)),
    ])

    fmt = SwitchFormat(case_formats, switch_markup_class="source_reference", use_stream_format=False)
    fmt.set_xml_name("harvard_style")
    return fmt


def family_name_harvard_style():

    fmt = ValueFormat(converter=TitlecaseConverter(min_n_uppercase=1), outer_markup_class="family_name")
    fmt.set_xml_name("family_name_harvard_style")
    return fmt


def given_names_and_initials_harvard_style():

    fmt = SequenceFormat(ValueFormat(),
                         SequenceMap(((0, ""), (-1, "")), " "),
                         sequence_markup_class="given_names_and_initials",
                         converter=GivenNameAndInitialConverter())
    fmt.set_xml_name("given_names_and_initials_harvard_style")
    return fmt


def person_harvard_style(label_mode=False):

    if not label_mode:
        attribute_formats = [
            ("family_name", family_name_harvard_style()),
            ("given_names_and_initials", given_names_and_initials_harvard_style())
        ]

        attribute_order = ("family_name", "given_names_and_initials")
    else:
        attribute_formats = [
            ("family_name", family_name_harvard_style()),
        ]

        attribute_order = ("family_name",)

    attribute_formats = OrderedDict(attribute_formats)

    apply_name_prefix(attribute_formats, "person.")

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ", "))

    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format)
    fmt.set_xml_name("person_harvard_style")
    return fmt


def organisation_name_harvard_style():

    fmt = ValueFormat(outer_markup_class="organisation_name", converter=TitlecaseConverter())
    fmt.set_xml_name("organisation_name_harvard_style")
    return fmt


def organisation_harvard_style(label_mode=False): # noqa

    attribute_formats = OrderedDict([
        ("name", organisation_name_harvard_style()),
    ])

    apply_name_prefix(attribute_formats, "organisation.")

    attribute_order = list(attribute_formats.keys())
    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ", "))
    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format)
    fmt.set_xml_name("organisation_harvard_style")
    return fmt


def name_harvard_style(label_mode=False):

    case_formats = OrderedDict([
        ("person", person_harvard_style(label_mode=label_mode)),
        ("organisation", organisation_harvard_style(label_mode=label_mode)),
    ])

    apply_name_prefix(case_formats, "name.")

    fmt = SwitchFormat(case_formats, switch_markup_class="name")
    fmt.set_xml_name("name_harvard_style")
    return fmt


def name_role_harvard_style():

    singular_format = ValueFormat(converter=MappingConverter(
        mappings={
            EDITOR_ROLE: "(ed.)",
        }
    ))

    plural_format = ValueFormat(converter=MappingConverter(
        mappings={
            EDITOR_ROLE: "(eds.)",
        }
    ))

    p = Predicate([(PreviousKey(), LengthGreaterThan(1, converter=IndexedElement(1)))])
    s = Predicate([(PreviousKey(), LengthEquals(1, converter=IndexedElement(1)))])

    fmt = PredicateFormat([(s, singular_format), (p, plural_format)], predicate_markup_class="name_role")
    fmt.set_xml_name("name_role_harvard_style")
    return fmt


def name_list_harvard_style(include_role=True, ellipsis_limit=None, ellipsis_replacement=" et al.",
                            outer_markup_class=None, label_mode=False):

    if ellipsis_limit is None:
        ep = None
    else:
        if not label_mode:
            ep = EndEllipsis(limit=ellipsis_limit, replacement=ellipsis_replacement)
        else:
            ep = FixedEllipsis(limit=ellipsis_limit, replacement=ellipsis_replacement)

    seq_format = SequenceFormat(name_harvard_style(label_mode=label_mode), # noqa
                                SequenceMap(((0, ""), (-1, ""), (-2, " and "),), ", "), ellipsis=ep)

    attribute_items = [
        ("names", seq_format)
    ]

    if include_role:
        attribute_items.append(
            ("role", name_role_harvard_style())
        )

    attribute_formats = OrderedDict(attribute_items)

    apply_name_prefix(attribute_formats, "name_list.")

    attribute_order = [item[0] for item in attribute_items]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), " "))

    if outer_markup_class is None:
        outer_markup_class = "name_list"

    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format,
                           default_attribute_values={"names": []},
                           dictionary_markup_class=outer_markup_class)

    fmt.set_xml_name("name_list_harvard_style")
    return fmt


def title_harvard_style(converter=None, outer_markup_class: Optional[str] = "title", prefix="", suffix="",
                        prefix_markup_class=None, suffix_markup_class=None):

    all_converters = [TitlecaseConverter()]

    if converter is not None:
        all_converters.insert(0, converter)

    fmt = ValueFormat(prefix=prefix, suffix=suffix,
                      prefix_markup_class=prefix_markup_class,
                      suffix_markup_class=suffix_markup_class,
                      outer_markup_class=outer_markup_class,
                      converter=all_converters)

    fmt.set_xml_name("title_harvard_style")
    return fmt


def paragraph_harvard_style(converter=None, outer_markup_class="paragraph"):

    all_converters = [ParagraphConverter()]

    if converter is not None:
        all_converters.insert(0, converter)

    fmt = ValueFormat(outer_markup_class=outer_markup_class, converter=all_converters)
    fmt.set_xml_name("sentence_harvard_style")
    return fmt


def year_harvard_style(label_mode=False):

    fmt = ValueFormat(outer_markup_class="year",
                      prefix_markup_class="year_prefix",
                      suffix_markup_class="year_suffix",
                      converter=DecimalConverter(),
                      prefix="(" if not label_mode else "",
                      suffix=")" if not label_mode else "",
                      outer_empty_substitution_value="[No Year]")

    fmt.set_xml_name("year_harvard_style")
    return fmt


def isbn_harvard_style():

    fmt = ValueFormat(outer_markup_class="isbn")
    fmt.set_xml_name("isbn_harvard_style")
    return fmt


def medium_harvard_style():

    attribute_formats = OrderedDict([
        ("description", title_harvard_style(outer_markup_class="description")),
    ])

    apply_name_prefix(attribute_formats, "medium.")

    attribute_order = list(attribute_formats.keys())
    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, "["), (-1, "]")), " "),
                                empty_substitution_value="")

    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format, dictionary_markup_class="medium")
    fmt.set_xml_name("medium_harvard_style")
    return fmt


def volume_number_harvard_style():

    fmt = ValueFormat(outer_markup_class="volume_number",
                      converter=DecimalConverter(strict=False),
                      outer_empty_substitution_value="") # [No Volume Number]

    fmt.set_xml_name("volume_harvard_style")
    return fmt


def issue_number_or_name_harvard_style():
    fmt = ValueFormat(outer_markup_class="issue_number_or_name",
                      converter=[DecimalConverter(strict=False), TitlecaseConverter()],
                      prefix="(", suffix=")"
                      )  # outer_empty_substitution_value="[No Issue Number]")
    fmt.set_xml_name("issue_number_or_name_harvard_style")
    return fmt


def issue_harvard_style():

    attribute_formats = OrderedDict([
        ("volume_number", volume_number_harvard_style()),
        ("issue_number_or_name", issue_number_or_name_harvard_style()),
    ])

    apply_name_prefix(attribute_formats, "issue.")

    attribute_order = list(attribute_formats.keys())
    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), " "),
                                empty_substitution_value="[No Issue]")

    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format, dictionary_markup_class="issue")
    fmt.set_xml_name("issue_harvard_style")
    return fmt


def pages_harvard_style(separator=" – ", regular_prefix="pp. ", simple_prefix="p. ", do_collapse=True,
                        outer_markup_class="pages"): # noqa

    attribute_order = ["first", "last"]
    converters = [FlattenDictionaryConverter(attribute_order, False),
                  DecimalConverter(strict=False),
                  RangeFromPairConverter(separator=separator, regular_prefix=regular_prefix,
                                         simple_prefix=simple_prefix, do_collapse=do_collapse)]

    fmt = ValueFormat(outer_markup_class="pages", converter=converters)
    fmt.set_xml_name("pages_harvard_style")
    return fmt


def publication_status_harvard_style():

    converter = MappingConverter(
        mappings={
            UNKNOWN_PUBLICATION_STATUS: "",
            SUBMITTED_PUBLICATION_STATUS: "Submitted to",
            TO_BE_PUBLISHED_PUBLICATION_STATUS: "To be published in",
        }
    )

    attribute_formats = OrderedDict([
        ("status", paragraph_harvard_style(outer_markup_class="status", converter=converter)),
        ("journal_name", title_harvard_style(outer_markup_class="container_title")),
    ])

    apply_name_prefix(attribute_formats, "publication_status.")

    attribute_order = list(attribute_formats.keys())
    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), " "))
    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format, dictionary_markup_class="publication_status")
    fmt.set_xml_name("publication_status_harvard_style")
    return fmt


def publisher_harvard_style():

    attribute_formats = OrderedDict([
        ("place", title_harvard_style(outer_markup_class=None)),
        ("name", title_harvard_style(outer_markup_class=None)),
    ])

    apply_name_prefix(attribute_formats, "publisher.")

    attribute_order = list(attribute_formats.keys())
    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ", "),
                                separator_markup_class="secondary_separator")
    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format, dictionary_markup_class="publisher")
    fmt.set_xml_name("publisher_harvard_style")
    return fmt


def repository_name_harvard_style():

    converter = TitlecaseConverter()
    fmt = ValueFormat(outer_markup_class="repository_name", converter=converter,
                      outer_empty_substitution_value="[No Repository]")
    fmt.set_xml_name("repository_harvard_style")
    return fmt


def edition_harvard_style():

    fmt = ValueFormat(outer_markup_class="edition", converter=OrdinalConverter(), suffix=" ed.")
    fmt.set_xml_name("edition_harvard_style")
    return fmt


def label_harvard_style(names_identifier="authors", names_markup_class=None):

    group_formats = [
        ((names_identifier,), name_list_harvard_style(include_role=False,
                                                      ellipsis_limit=3,
                                                      outer_markup_class=names_markup_class,
                                                      label_mode=True)),
        (("year",), year_harvard_style(label_mode=True))
    ]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ", "))
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    return fmt


def names_year_title_group_harvard_style(name_prefix, names_identifier="authors", title_identifier="title", # noqa
                                         include_role=False, include_year=True,
                                         prefix="", suffix="",
                                         names_markup_class=None,
                                         title_markup_class="title",
                                         prefix_markup_class=None,
                                         suffix_markup_class=None):

    group_formats = [
        ((names_identifier,), name_list_harvard_style(include_role, outer_markup_class=names_markup_class)),
        ((title_identifier,), title_harvard_style(outer_markup_class=title_markup_class)),
    ]

    if include_year:
        group_formats.insert(1, (("year",), year_harvard_style()))

    if prefix:
        group_formats.insert(0, (StaticGroup(prefix), ValueFormat(do_escape=True,
                                                                  outer_markup_class=prefix_markup_class)))

    if suffix:
        group_formats.append((StaticGroup(suffix), ValueFormat(do_escape=True,
                                                               outer_markup_class=suffix_markup_class)))

    # apply_name_prefix(attribute_formats, name_prefix)

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), " "))
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    # fmt.set_xml_name("journal_article_harvard_style")
    return fmt


def issue_pages_and_identifier_harvard_style(name_prefix):

    attribute_formats = OrderedDict([
        ("issue", issue_harvard_style()),
        ("pages", pages_harvard_style(regular_prefix="", simple_prefix="", do_collapse=False))
    ])

    apply_name_prefix(attribute_formats, name_prefix)

    attribute_order = ["issue", "pages"]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ", "),
                                separator_markup_class="secondary_separator")

    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format,
                           dictionary_markup_class="issue_pages_and_identifier")
    # fmt.set_xml_name("journal_article_harvard_style")
    return fmt


def issue_pages_and_identifier_harvard_style_new(name_prefix):

    attribute_formats = OrderedDict([
        ("issue", issue_harvard_style()),
        ("pages", pages_harvard_style(regular_prefix="", simple_prefix="", do_collapse=False)),
        ("identifier", identifier_harvard_style())
    ])

    apply_name_prefix(attribute_formats, name_prefix)

    attribute_order = ["issue", "pages"]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ", "),
                                separator_markup_class="secondary_separator")

    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format,
                           dictionary_markup_class="issue_pages_and_identifier")
    # fmt.set_xml_name("journal_article_harvard_style")

    attribute_order = ["issue", "pages", "identifier"]

    converters = [FlattenDictionaryConverter(attribute_order, False),
                  RangeFromPairConverter(separator=separator, regular_prefix=regular_prefix,
                                         simple_prefix=simple_prefix, do_collapse=do_collapse)]

    fmt = ValueFormat(outer_markup_class="pages", converter=converters)
    fmt.set_xml_name("pages_harvard_style")
    return fmt

    return fmt


def book_and_pages_harvard_style(name_prefix):

    attribute_formats = OrderedDict([
        ("pages", pages_harvard_style())
    ])

    apply_name_prefix(attribute_formats, name_prefix)
    attribute_order = ["pages"]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ""))
    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format,
                           converter=EmbedInDictionaryConverter("pages"), dictionary_markup_class="pages_in_book")

    group_formats = [
        (("book",), book_harvard_style(for_chapter=True)),
        (("pages",), fmt),
    ]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ", "),
                                separator_markup_class="primary_separator")

    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    return fmt


def identifier_harvard_style():

    fmt = ValueFormat(outer_markup_class="identifier", converter=TrimConverter())
    fmt.set_xml_name("identifier_harvard_style")
    return fmt


def scale_harvard_style():

    fmt = ValueFormat(outer_markup_class="scale", converter=TrimConverter())
    fmt.set_xml_name("scale_harvard_style")
    return fmt


def identifier_scale_harvard_style(name_prefix):

    attribute_formats = OrderedDict([
        ("identifier", identifier_harvard_style()),
        ("scale", scale_harvard_style())
    ])

    apply_name_prefix(attribute_formats, name_prefix)

    attribute_order = ["identifier", "scale"]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), ", "),
                                separator_markup_class="secondary_separator")
    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format)
    fmt.set_xml_name("identifier_scale_harvard_style")
    return fmt


def doi_harvard_style(name_prefix):

    attribute_formats = OrderedDict([
        ("identifier", identifier_harvard_style()),
    ])

    apply_name_prefix(attribute_formats, name_prefix)

    attribute_order = ["identifier"]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, "DOI: "), (-1, "")), " "),
                                sequence_markup_class="doi")
    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format)
    # fmt.set_xml_name("journal_article_harvard_style")
    return fmt


def access_date_harvard_style(name_prefix): # noqa

    fmt = ValueFormat(converter=DateConverter(), prefix="[Accessed ", suffix="]",
                      outer_empty_substitution_value="[No Date]")

    p = Predicate([(PreviousKey(), NotBlank(converter=IndexedElement(1)))])

    fmt = PredicateFormat([(p, fmt)], predicate_markup_class="access_date")
    return fmt


def url_reference_harvard_style(name_prefix):

    attribute_formats = OrderedDict([
        ("url", ValueFormat(outer_markup_class="url", converter=TrimConverter())),
        ("access_date", access_date_harvard_style("url_reference.")),
    ])

    apply_name_prefix(attribute_formats, name_prefix)

    attribute_order = ["url", "access_date"]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, "Available from: "), (-1, "")), " "))
    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format, dictionary_markup_class="url_reference")
    # fmt.set_xml_name("journal_article_harvard_style")
    return fmt


def series_harvard_style(name_prefix):

    attribute_formats = OrderedDict([
        ("name", ValueFormat(converter=TitlecaseConverter())),
        ("identifier", identifier_harvard_style()),
    ])

    apply_name_prefix(attribute_formats, name_prefix)

    attribute_order = ["name", "identifier"]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), " "))
    fmt = DictionaryFormat(attribute_order, attribute_formats, seq_format, dictionary_markup_class="series")
    # fmt.set_xml_name("journal_article_harvard_style")
    return fmt


def primary_sequence_format(prefix="", suffix=".", sequence_markup_class=None,
                            separator_markup_class="primary_separator"):

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, prefix), (-1, suffix)), ". "),
                                sequence_markup_class=sequence_markup_class,
                                separator_markup_class=separator_markup_class)
    return seq_format


def journal_article_harvard_style(label_mode=False):

    if label_mode:
        return label_harvard_style(names_markup_class="primary_names")

    group_formats = [
        (("authors", "year", "title"), names_year_title_group_harvard_style(
                                        "journal_article.", names_markup_class="primary_names")),
        (("journal_name",), title_harvard_style(outer_markup_class="container_title")),
        (("issue", "pages", "identifier"), issue_pages_and_identifier_harvard_style("journal_article.")),
        (("doi",), doi_harvard_style("journal_article."))
    ]

    seq_format = primary_sequence_format()
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("journal_article_harvard_style")
    return fmt


def preprint_article_harvard_style(label_mode=False):

    if label_mode:
        return label_harvard_style(names_markup_class="primary_names")

    group_formats = [
        (("authors", "year", "title"), names_year_title_group_harvard_style(
                                        "preprint_article.", names_markup_class="primary_names")),
        (("publication_status",), publication_status_harvard_style()),
        (("repository_name",), title_harvard_style(outer_markup_class="repository_name")),
        (StaticGroup("[Preprint]"), ValueFormat()),
        (("url",), url_reference_harvard_style("preprint_article.")),
    ]

    seq_format = primary_sequence_format()
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("preprint_article_harvard_style")
    return fmt


def book_harvard_style(for_chapter=False, label_mode=False):

    names_markup_class = "secondary_names" if for_chapter else "primary_names"

    if label_mode:
        return label_harvard_style(names_markup_class=names_markup_class)

    group_formats = [
        (("authors_or_editors", "year", "title"),
         names_year_title_group_harvard_style("book.",
                                              names_identifier="authors_or_editors",
                                              include_role=for_chapter,
                                              include_year=(not for_chapter),
                                              prefix="In: " if for_chapter else "",
                                              names_markup_class=names_markup_class,
                                              title_markup_class=None if for_chapter else "title",
                                              prefix_markup_class="container_title_prefix" if for_chapter else None)),
        (("edition",), edition_harvard_style()),
        (("series",), series_harvard_style("book.")),
        (("publisher",), publisher_harvard_style()),
    ]

    if not for_chapter:
        group_formats.append((("doi",), doi_harvard_style("book.")))
        group_formats.append((("url",), url_reference_harvard_style("book.")))

    seq_format = primary_sequence_format(suffix="" if for_chapter else ".",
                                         sequence_markup_class="container_title" if for_chapter else None,
                                         separator_markup_class="secondary_separator" if for_chapter
                                         else "primary_separator")

    # if for_chapter:
    #    seq_format = primary_sequence_format()
    # else:
    #    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), " "),
    #    sequence_markup_class="container_title", separator_markup_class="secondary_separator")

    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("book_harvard_style")
    return fmt


def book_chapter_harvard_style(label_mode=False):

    if label_mode:
        return label_harvard_style(names_markup_class="primary_names")

    group_formats = [
        (("authors", "year", "title"), names_year_title_group_harvard_style(
            "book_chapter.", names_markup_class="primary_names")),
        (("book", "pages"), book_and_pages_harvard_style("book_chapter.")),
        (("doi",), doi_harvard_style("book_chapter.")),
        (("url",), url_reference_harvard_style("book_chapter."))
    ]

    seq_format = primary_sequence_format(prefix="", suffix=".")
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("book_chapter_harvard_style")
    return fmt


def proceedings_article_harvard_style(label_mode=False):

    if label_mode:
        return label_harvard_style(names_markup_class="primary_names")

    group_formats = [
        (("authors", "year", "title"), names_year_title_group_harvard_style(
            "proceedings_article.", names_markup_class="primary_names")),
        (("editors", "conference_title"), names_year_title_group_harvard_style("proceedings_article.",
                                                                               names_identifier="editors",
                                                                               title_identifier="conference_title",
                                                                               include_role=True,
                                                                               include_year=False,
                                                                               prefix="In: ",
                                                                               names_markup_class="secondary_names",
                                                                               title_markup_class="container_title")),
        (("publisher",), publisher_harvard_style()),
        (("pages",), pages_harvard_style()),
        (("doi",), doi_harvard_style("proceedings_article.")),
        (("url",), url_reference_harvard_style("proceedings_article.")),
    ]

    seq_format = primary_sequence_format(prefix="", suffix=".")
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("proceedings_article_harvard_style")
    return fmt


def published_standard_harvard_style(label_mode=False):

    if label_mode:
        return label_harvard_style(names_identifier="authority", names_markup_class="primary_names")

    attribute_formats = OrderedDict([
        ("authority", organisation_harvard_style()),
        ("year", year_harvard_style()),
        ("identifier", identifier_harvard_style()),
    ])

    apply_name_prefix(attribute_formats, "published_standard.")

    attribute_order = ["authority", "year", "identifier", "title", "publisher", "url"]

    seq_format = SequenceFormat(ValueFormat(do_escape=False), SequenceMap(((0, ""), (-1, "")), " "))
    group_format = DictionaryFormat(attribute_order, attribute_formats, seq_format)

    group_formats = [
        (("authority", "year", "identifier"), group_format),
        (("title",), title_harvard_style()),
        (("publisher",), publisher_harvard_style()),
        (("url",), url_reference_harvard_style("published_standard."))
    ]

    seq_format = primary_sequence_format(prefix="", suffix=".")
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("published_standard_harvard_style")
    return fmt


def patent_harvard_style(label_mode=False):

    if label_mode:
        return label_harvard_style(names_identifier="inventors", names_markup_class="primary_names")

    group_formats = [
        (("inventors", "year", "title"),
         names_year_title_group_harvard_style("patent.", names_identifier="inventors", include_role=False,
                                              include_year=True,
                                              names_markup_class="primary_names")),
        (("identifier",), identifier_harvard_style()),
        (("url",), url_reference_harvard_style("patent."))
    ]

    seq_format = primary_sequence_format(prefix="", suffix=".")
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("patent_harvard_style")
    return fmt


def report_harvard_style(label_mode=False):

    if label_mode:
        return label_harvard_style(names_identifier="authors_or_editors", names_markup_class="primary_names")

    group_formats = [
        (("authors_or_editors", "year", "title"),
         names_year_title_group_harvard_style("report.", names_identifier="authors_or_editors", include_role=False,
                                              include_year=True,
                                              names_markup_class="primary_names")),
        (("identifier",), identifier_harvard_style()),
        (("series",), series_harvard_style("report.")),
        (("publisher",), publisher_harvard_style()),
        (("url",), url_reference_harvard_style("report."))
    ]

    seq_format = primary_sequence_format(prefix="", suffix=".")
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("report_harvard_style")
    return fmt


def map_harvard_style(label_mode=False):

    if label_mode:
        return label_harvard_style(names_identifier="authors_or_editors", names_markup_class="primary_names")

    group_formats = [
        (("authors_or_editors", "year", "title"),
         names_year_title_group_harvard_style("map.", names_identifier="authors_or_editors", include_role=True,
                                              include_year=True,
                                              names_markup_class="primary_names")),
        (("identifier", "scale"), identifier_scale_harvard_style("map.")),
        (("series",), series_harvard_style("map.")),
        (("publisher",), publisher_harvard_style()),
        (("url",), url_reference_harvard_style("map."))
    ]

    seq_format = primary_sequence_format(prefix="", suffix=".")
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("map_harvard_style")
    return fmt


def website_harvard_style(label_mode=False):

    if label_mode:
        return label_harvard_style(names_identifier="authors_or_editors", names_markup_class="primary_names")

    group_formats = [
        (("authors_or_editors", "year", "title"),
         names_year_title_group_harvard_style("website.", names_identifier="authors_or_editors", include_role=True,
                                              include_year=True,
                                              names_markup_class="primary_names")),
        (StaticGroup("[Online]"), ValueFormat()),
        (("url",), url_reference_harvard_style("website."))
    ]

    seq_format = primary_sequence_format(prefix="", suffix=".")
    fmt = GroupingFormat(key_group_formats=group_formats, key_group_sequence_format=seq_format)
    fmt.set_xml_name("website_harvard_style")
    return fmt

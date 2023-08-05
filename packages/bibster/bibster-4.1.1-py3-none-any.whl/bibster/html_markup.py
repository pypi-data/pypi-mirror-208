
from officekit.models import Person

from .formatting.markup import HTMLMarkup, MarkupMetadata, prefix_merge_mode, suffix_merge_mode
from . import identifiers

__all__ = ['REFERENCE_MARKUP']


REFERENCE_PREFIX = "pubref" # noqa

REFERENCE_CSS_CLASSES = [

    REFERENCE_PREFIX + "-primary_separator",
    REFERENCE_PREFIX + "-secondary_separator",
    REFERENCE_PREFIX + "-title",
    REFERENCE_PREFIX + "-container_title",
    REFERENCE_PREFIX + "-container_title_prefix",
    REFERENCE_PREFIX + "-volume_number",
    REFERENCE_PREFIX + "-year",
    REFERENCE_PREFIX + "-issue_number_or_name",
    REFERENCE_PREFIX + "-issue",
    REFERENCE_PREFIX + "-pages",
    REFERENCE_PREFIX + "-container_location",
    REFERENCE_PREFIX + "-publisher",
    REFERENCE_PREFIX + "-series",
    REFERENCE_PREFIX + "-url_reference",
    REFERENCE_PREFIX + "-access_date",
    REFERENCE_PREFIX + "-url",
    REFERENCE_PREFIX + "-doi",
    REFERENCE_PREFIX + "-person",

    REFERENCE_PREFIX + "-primary_names",
    REFERENCE_PREFIX + "-secondary_names",

    REFERENCE_PREFIX + "-author_names",
    REFERENCE_PREFIX + "-editor_names",
    REFERENCE_PREFIX + "-inventor_names",

    REFERENCE_PREFIX,

    REFERENCE_PREFIX + "-" + identifiers.JOURNAL_ARTICLE_REFERENCE,
    REFERENCE_PREFIX + "-" + identifiers.PREPRINT_ARTICLE_REFERENCE,
    REFERENCE_PREFIX + "-" + identifiers.BOOK_CHAPTER_REFERENCE,
    REFERENCE_PREFIX + "-" + identifiers.BOOK_REFERENCE,
    REFERENCE_PREFIX + "-" + identifiers.PROCEEDINGS_ARTICLE_REFERENCE,
    REFERENCE_PREFIX + "-" + identifiers.PUBLISHED_STANDARD_REFERENCE,
    REFERENCE_PREFIX + "-" + identifiers.PATENT_REFERENCE,
    REFERENCE_PREFIX + "-" + identifiers.REPORT_REFERENCE,
    REFERENCE_PREFIX + "-" + identifiers.MAP_REFERENCE,
    REFERENCE_PREFIX + "-" + identifiers.WEBSITE_REFERENCE,
]


def markup_doi(value, metadata, original_value):

    if value.startswith("DOI: "):
        value = value[5:]

    value = "https://doi.org/" + value.strip()

    # TODO: Implement correct tracking of metadata bookmarks
    return value, MarkupMetadata()


def markup_url(value, metadata, original_value):
    result = "<a class=\"{}\" href=\"{}\">{}</a>".format(REFERENCE_PREFIX + "-url", original_value, value)

    # TODO: Implement correct tracking of metadata bookmarks
    return result, MarkupMetadata()


def markup_name(value, metadata, original_value):

    # TODO: Implement correct tracking of metadata bookmarks
    metadata = MarkupMetadata()

    name_type = original_value.get("type", None)

    if name_type is None or name_type not in ("person", "organisation"):
        return value, metadata

    original_value = original_value.get("value", {})

    if name_type == "person":
        person = original_value.get("identify_with", None)

        if person is None:
            return value, metadata

        try:
            person = Person.objects.get(pk=person)
        except Person.DoesNotExist:
            return value, metadata

        if not person.link:
            return value, metadata

        person_link = person.link.as_rich_link()
        person_url = person_link.determine_url()

        if not person_url:
            return value, metadata

        relationships = person_link.relationships_as_html

        if relationships:
            " rel=\"{}\"".format(relationships)

        result = "<a class=\"{}\" href=\"{}\"{}>{}</a>".format(REFERENCE_PREFIX + "-person",
                                                               person_url, relationships, value)
    else:
        result = value

    return result, metadata


def markup_name_list(value, metadata, original_value, identifier="names"):
    role = original_value.get("role", None)
    attributes = " class=\"" + REFERENCE_PREFIX + "-" + identifier + \
                 ("{}\"".format(" " + REFERENCE_PREFIX + "-" + role + "-names") if role else "")
    result = "<span{}>{}</span>".format(attributes, value)

    # TODO: Implement correct tracking of metadata bookmarks
    return result, MarkupMetadata()


def markup_reference(value, metadata, original_value):
    reference_type = original_value.get("type", None)
    attributes = " class=\"" + REFERENCE_PREFIX + "{}\"".format(" " + REFERENCE_PREFIX + "-" + reference_type
                                                                if reference_type else "")
    result = "<span{}>{}</span>".format(attributes, value)

    prefix_length = 6 + len(attributes)
    metadata.merge(MarkupMetadata(bookmarks={"reference:start": [prefix_length]}),
                   mode=prefix_merge_mode(prefix_length=prefix_length))
    target_length = len(result) - 7
    metadata.merge(MarkupMetadata(bookmarks={"reference:end": [0]}),
                   mode=suffix_merge_mode(target_length=target_length))

    return result, metadata


REFERENCE_MARKUP = HTMLMarkup()

REFERENCE_MARKUP.map("doi", "a", [("class", REFERENCE_PREFIX + "-doi"),
                                  ("href",
                                   lambda name, value, metadata, original_value:
                                   markup_doi(value, metadata, original_value))])

REFERENCE_MARKUP.map("title", "span", [("class", REFERENCE_PREFIX + "-title")])
REFERENCE_MARKUP.map("container_title", "span", [("class", REFERENCE_PREFIX + "-container_title")])
REFERENCE_MARKUP.map("container_title_prefix", "span", [("class", REFERENCE_PREFIX + "-container_title_prefix")])

REFERENCE_MARKUP.map("year", "span", [("class", REFERENCE_PREFIX + "-year")])
REFERENCE_MARKUP.map("year_prefix", "span", [("class", REFERENCE_PREFIX + "-year_prefix")])
REFERENCE_MARKUP.map("year_suffix", "span", [("class", REFERENCE_PREFIX + "-year_suffix")])
REFERENCE_MARKUP.map("volume_number", "span", [("class", REFERENCE_PREFIX + "-volume_number")])
REFERENCE_MARKUP.map("issue_number_or_name", "span", [("class", REFERENCE_PREFIX + "-issue_number_or_name")])
REFERENCE_MARKUP.map("issue", "span", [("class", REFERENCE_PREFIX + "-issue")])
REFERENCE_MARKUP.map("pages", "span", [("class", REFERENCE_PREFIX + "-pages")])
REFERENCE_MARKUP.map("issue_pages_and_identifier", "span", [("class", REFERENCE_PREFIX + "-container_location")])
REFERENCE_MARKUP.map("pages_in_book", "span", [("class", REFERENCE_PREFIX + "-container_location")])
REFERENCE_MARKUP.map("publisher", "span", [("class", REFERENCE_PREFIX + "-publisher")])
REFERENCE_MARKUP.map("access_date", "span", [("class", REFERENCE_PREFIX + "-access_date")])
REFERENCE_MARKUP.map("url_reference", "span", [("class", REFERENCE_PREFIX + "-url_reference")])
REFERENCE_MARKUP.map("series", "span", [("class", REFERENCE_PREFIX + "-series")])
REFERENCE_MARKUP.map("primary_separator", "span", [("class", REFERENCE_PREFIX + "-primary_separator")])
REFERENCE_MARKUP.map("secondary_separator", "span", [("class", REFERENCE_PREFIX + "-secondary_separator")])

REFERENCE_MARKUP.map_function("url", markup_url)

REFERENCE_MARKUP.map_function("name", markup_name)
REFERENCE_MARKUP.map_function("primary_names", lambda x, y, z: markup_name_list(x, y, z, "primary_names"))
REFERENCE_MARKUP.map_function("secondary_names", lambda x, y, z: markup_name_list(x, y, z, "secondary_names"))
REFERENCE_MARKUP.map_function("source_reference", markup_reference)

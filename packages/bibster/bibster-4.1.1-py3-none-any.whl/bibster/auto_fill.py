import requests
import datetime
import re
from html import unescape as unescape_html

from habanero import Crossref

from officekit.models import Person

from .identifiers import *

"""
funder (singleton)
prefix (singleton)
member (singleton)
work (singleton)
work-list (list)
funder-list (list)
prefix-list (list)
"""


SPACE_RE = re.compile(r"\s+")
INITIALS_RE = re.compile(r"(\s|^)([A-Za-z])(\.+)(\s|$)")


def clean_given_names_and_initials(value, remove_initials=True):

    value = value.strip()
    value = SPACE_RE.sub(' ', value)
    value = INITIALS_RE.sub('' if remove_initials else '\1\2.\3', value)
    value = value.title()
    return value


def clean_family_name(value):

    value = value.strip()
    value = SPACE_RE.sub(' ', value)
    value = value.title()
    return value


def identify_person_with_name(name):

    given_names_and_initials = clean_given_names_and_initials(name['given_names_and_initials'], remove_initials=True)
    family_name = clean_family_name(name['family_name'])

    people = Person.objects.all().filter(
                family_name__iexact=family_name,
                given_names_and_initials__iexact=given_names_and_initials)

    n = people.count()

    if n != 1:
        return None

    person = people[0]
    return person


def name_list_from_contributor_list(contributor_list, role):

    result = []

    for person in contributor_list:

        family_name = clean_family_name(person.get("family", ""))
        given_names_and_initials = clean_given_names_and_initials(person.get("given", ""))

        value = {"family_name": family_name,
                 "given_names_and_initials": given_names_and_initials}

        person = identify_person_with_name(value)
        value["identify_with"] = person.pk if person else None

        value = {"type": "person", "value": value}
        result.append(value)

    result = {
        "names": result,
        "role": role,
    }

    return result


def get_string_from_list(metadata, field_name, default_string=""):

    string_list = metadata.get(field_name, [default_string])

    if not string_list:
        value = default_string
    else:
        value = string_list[0]

    value = unescape_html(value)

    return value


def get_string_list_from_list(metadata, field_name, default_string=""):

    string_list = metadata.get(field_name, [default_string])

    if not string_list:
        value = [default_string]
    else:
        value = string_list

    return value


def get_partial_date(metadata, field_name, default_year=None):

    if default_year is None:
        default_year = datetime.datetime.now().year

    partial_date = metadata.get(field_name, { "date-parts": [[default_year]] })
    partial_date = partial_date.get("date-parts", [[default_year]])
    partial_date = partial_date[0]

    year = None
    month = None
    day = None

    if len(partial_date) > 0:
        year = partial_date[0]

    if len(partial_date) > 1:
        month = partial_date[1]

    if len(partial_date) > 2:
        day = partial_date[2]

    return year, month, day


def get_page_range(metadata, field_name, default_page_range=None):

    if default_page_range is None:
        default_page_range = {}

    pages = metadata.get(field_name, default_page_range)

    if isinstance(pages, str):
        parts = pages.split("-")

        if len(parts) == 2:
            return {"first": parts[0], "last": parts[1]}

        if len(parts) == 1:
            return {"first": parts[0], "last": parts[0]}

        return default_page_range

    return pages


def get_article_number(metadata, field_name, default_article_number=None):

    article_number = metadata.get(field_name, default_article_number)
    return article_number


def get_issue(metadata):

    volume = metadata.get("volume", "")
    issue_number_or_name = metadata.get("issue", "")

    return { "volume_number": volume, "issue_number_or_name": issue_number_or_name }


def get_doi(metadata):

    doi = metadata.get("DOI", "")
    doi = { "identifier": doi }
    return doi


def get_isbn(metadata):

    isbn = get_string_from_list(metadata, "ISBN", default_string="")
    isbn = { "number": isbn }
    return isbn


def get_issn(metadata):

    issn = get_string_from_list(metadata, "ISSN", default_string="")
    isbn = { "number": issn }
    return isbn


def get_url_reference(metadata):

    url = metadata.get("URL", "")
    url_reference = { "url": url, "access_date": None }
    return url_reference


def get_publisher(metadata):

    publisher = metadata.get("publisher", "")

    publisher = { "name": publisher, "place": ""}
    return publisher


def get_alternative_id(metadata):
    return metadata.get("alternative-id", "")


def get_year(metadata):

    print_year, _, _ = get_partial_date(metadata, "published-print")
    online_year, _, _ = get_partial_date(metadata, "published-online")

    if print_year and online_year:
        year = online_year if online_year < print_year else print_year
    elif print_year:
        year = print_year
    elif online_year:
        year = online_year
    else:
       year, _, _ = get_partial_date(metadata, "issued")

    return year


def journal_article_reference_from_metadata(metadata):

    authors = metadata.get("author", {})
    authors = name_list_from_contributor_list(authors, AUTHOR_ROLE)

    title = get_string_from_list(metadata, "title")
    journal_name = get_string_from_list(metadata, "container-title")
    journal_short_name = get_string_from_list(metadata, "short-container-title")

    if not journal_short_name:
        journal_short_name = journal_name

    year = get_year(metadata)

    pages = get_page_range(metadata, "page")
    article_number = get_article_number(metadata, "article-number")
    issue = get_issue(metadata)
    doi = get_doi(metadata)

    result = {
        "title": title,
        "year": year,
        "authors": authors,
        "journal_name": journal_name,
        "short_journal_name": journal_short_name,
        "issue": issue,
        "pages": pages,
        "doi": doi
    }

    return result


def book_chapter_reference_from_metadata(metadata):

    authors = metadata.get("author", {})
    authors = name_list_from_contributor_list(authors, AUTHOR_ROLE)

    title = get_string_from_list(metadata, "title")
    book_title = get_string_list_from_list(metadata, "container-title")
    published_date = get_partial_date(metadata, "published")

    pages = get_page_range(metadata, "page")
    isbn = get_isbn(metadata)
    issn = get_issn(metadata)
    doi = get_doi(metadata)

    for book_title_part in reversed(book_title):
        book = identify_book_from_isbn_issn_and_title(isbn.get("number", ""), issn.get("number", ""), book_title_part, published_date)
        if book:
            break

    book_metadata = book.get("book", {})
    year = book_metadata.get("year", "")

    book_editors = book_metadata.get("authors_or_editors", {})
    book_editors["role"] = EDITOR_ROLE

    book_metadata["authors_or_editors"] = book_editors

    result = {
        "title": title,
        "year": year,
        "authors": authors,
        "pages": pages,
        "book": book_metadata,
        "doi": doi
    }

    return result


def book_reference_from_metadata(metadata):

    authors_or_editors = metadata.get("author", None)

    if authors_or_editors is None:
        authors_or_editors = metadata.get("editor", {})
        role = EDITOR_ROLE
    else:
        role = AUTHOR_ROLE

    authors_or_editors = name_list_from_contributor_list(authors_or_editors, role)

    title = get_string_from_list(metadata, "title")

    year = get_year(metadata)

    publisher = get_publisher(metadata)

    isbn = get_isbn(metadata)
    doi = get_doi(metadata)

    result = {
        "title": title,
        "year": year,
        "authors_or_editors": authors_or_editors,
        "publisher": publisher,
        "isbn": isbn,
        "doi": doi
    }

    return result


def proceedings_article_reference_from_metadata(metadata):

    authors = metadata.get("author", {})
    authors = name_list_from_contributor_list(authors, AUTHOR_ROLE)

    editors = metadata.get("editor", {})
    editors = name_list_from_contributor_list(editors, EDITOR_ROLE)

    title = get_string_from_list(metadata, "title")
    conference_title = get_string_from_list(metadata, "container-title")

    year = get_year(metadata)

    publisher = get_publisher(metadata)
    pages = get_page_range(metadata, "page")
    doi = get_doi(metadata)
    url_reference = get_url_reference(metadata)

    result = {
        "title": title,
        "year": year,
        "authors": authors,
        "pages": pages,

        "conference_title": conference_title,
        "editors": editors,
        "publisher": publisher,
        "doi": doi,
        "url": url_reference,
    }

    return result


def published_standard_reference_from_metadata(metadata):

    title = get_string_from_list(metadata, "title")

    year = get_year(metadata)

    publisher = get_publisher(metadata)
    pages = get_page_range(metadata, "page")
    identifier = get_alternative_id(metadata)
    url_reference = get_url_reference(metadata)

    result = {
        "title": title,
        "year": year,
        "pages": pages,

        "identifier": identifier,
        "publisher": publisher,

        "url": url_reference,
    }

    return result


def report_reference_from_metadata(metadata):

    authors_or_editors = metadata.get("author", None)

    if authors_or_editors is None:
        authors_or_editors = metadata.get("editor", {})
        role = EDITOR_ROLE
    else:
        role = AUTHOR_ROLE

    authors_or_editors = name_list_from_contributor_list(authors_or_editors, role)

    title = get_string_from_list(metadata, "title")

    year = get_year(metadata)

    pages = get_page_range(metadata, "page")
    identifier = get_alternative_id(metadata)
    url_reference = get_url_reference(metadata)

    result = {
        "title": title,
        "year": year,
        "authors_or_editors": authors_or_editors,
        "identifier": identifier,
        "pages": pages,
        "url": url_reference,
    }

    return result


REFERENCE_TYPE_HANDLERS = {
    "journal-article": (JOURNAL_ARTICLE_REFERENCE, journal_article_reference_from_metadata),
    "proceedings-article": (PROCEEDINGS_ARTICLE_REFERENCE, proceedings_article_reference_from_metadata),
    "book-chapter": (BOOK_CHAPTER_REFERENCE, book_chapter_reference_from_metadata),
    "book-section": (BOOK_CHAPTER_REFERENCE, book_chapter_reference_from_metadata),
    "book": (BOOK_REFERENCE, book_reference_from_metadata),
    "edited-book": (BOOK_REFERENCE, book_reference_from_metadata),
    "standard": (PUBLISHED_STANDARD_REFERENCE, published_standard_reference_from_metadata),
    "report": (REPORT_REFERENCE, report_reference_from_metadata),
}


def reference_from_metadata(metadata):

    """Create a JSON representation for a reference block from the given (CrossRef) metadata.

    :param metadata:
    :return:
    """

    crossref_type = metadata["type"]
    reference_type, reference_handler = REFERENCE_TYPE_HANDLERS.get(crossref_type, (None, None))

    if reference_handler is None:
        return {}

    result = {reference_type: reference_handler(metadata)}
    return result


def identify_book_from_isbn_issn_and_title(isbn, issn, title, published_date=None, cr=None):

    if cr is None:
        cr = Crossref()

    filter_spec = {"type": "book"}

    if isbn:
        filter_spec["isbn"] = isbn

    if issn:
        filter_spec["issn"] = issn

    if published_date is not None:
        year, month, day = published_date

        if year:
            filter_spec["from-pub-date"] = "{:d}".format(year)
            filter_spec["until-pub-date"] = "{:d}".format(year)


    try:
        results = reference_from_content(title, cr=cr, filter=filter_spec, is_title=False)
    except requests.exceptions.HTTPError as error:
        results = []

    if not results:
        return {}

    return results[0]


def reference_from_doi(dois, cr=None):

    if cr is None:
        cr = Crossref()

    try:
        crossref_reply = cr.works(ids=dois)
    except requests.exceptions.HTTPError as error:
        return []

    if crossref_reply["status"].lower() != "ok":
        return []

    if not crossref_reply["message-type"].lower().endswith("-list"):
        crossref_results = [crossref_reply['message']]
    else:
        crossref_results = crossref_reply['message']['items']

    results = []

    for index, metadata in enumerate(crossref_results):

        if index >= len(dois):
            break

        doi = dois[index]
        doi = doi.lstrip().rstrip().lower()

        if metadata["DOI"] != doi:
            results.append(None)
            continue

        reference = reference_from_metadata(metadata)
        results.append(reference)

    return results


def reference_from_content(content_text="", cr=None, filter=None, is_title=False):

    if cr is None:
        cr = Crossref()

    query_type = 'query_bibliographic' if not is_title else 'query_container_title'
    arguments = {
        query_type: content_text,
        "sort": "score",
        "filter": filter
    }

    try:
        crossref_reply = cr.works(**arguments)
    except requests.exceptions.HTTPError as error:
        return []

    if crossref_reply["status"].lower() != "ok":
        return []

    if not crossref_reply["message-type"].lower().endswith("-list"):
        crossref_results = [crossref_reply['message']]
    else:
        crossref_results = crossref_reply['message']['items']

    results = []

    for index, metadata in enumerate(crossref_results):

        reference = reference_from_metadata(metadata)
        results.append(reference)

    return results


def identify_reference(identifier, cr=None):

    if not identifier:
        return {}

    if cr is None:
        cr = Crossref()

    results = reference_from_doi([identifier], cr=cr)

    if not results:

        results = reference_from_content(identifier, cr=cr)

    if not results:
        return {}

    return results[0]


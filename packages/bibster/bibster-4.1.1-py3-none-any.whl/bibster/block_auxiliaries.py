import officekit.models as base

from wagtail_switch_block.blocks import TYPE_FIELD_NAME
from .identifiers import *

__all__ = ['get_reference_type',
           'get_book',

           'get_title',
           'get_journal_article_title',
           'get_preprint_article_title',
           'get_book_chapter_title',
           'get_book_title',
           'get_proceedings_article_title',
           'get_published_standard_title',
           'get_patent_title',
           'get_report_title',
           'get_map_title',
           'get_website_title',

           'get_year',
           'get_journal_article_year',
           'get_preprint_article_year',
           'get_book_chapter_year',
           'get_book_year',
           'get_proceedings_article_year',
           'get_published_standard_year',
           'get_patent_year',
           'get_report_year',
           'get_map_year',
           'get_website_year',

           'get_names_for_role',
           'get_authors',
           'get_journal_article_authors',
           'get_preprint_article_authors',
           'get_book_chapter_authors',
           'get_book_authors',
           'get_proceedings_article_authors',
           'get_report_authors',
           'get_map_authors',
           'get_website_authors',

           'get_published_standard_authority',
           'get_patent_inventors',
           'get_book_editors',
           'get_proceedings_article_editors',
           'get_report_editors',
           'get_website_editors',

           'get_publisher_name',
           'get_journal_article_publisher_name',
           'get_preprint_article_publisher_name',
           'get_book_chapter_publisher_name',
           'get_book_publisher_name',
           'get_proceedings_article_publisher_name',
           'get_published_standard_publisher_name',
           'get_patent_publisher_name',
           'get_report_publisher_name',
           'get_map_publisher_name',
           'get_website_publisher_name',

           'get_journal_article_journal_name',
           'get_preprint_article_journal_name',
           'get_preprint_article_repository_name',
           'get_book_chapter_book_title',
           'get_proceedings_article_conference_title',

           'get_book_edition',
           'get_journal_article_issue',
           'get_book_isbn',

           'get_identifier',
           'get_journal_article_identifier',
           'get_preprint_article_identifier',
           'get_book_chapter_identifier',
           'get_book_identifier',
           'get_proceedings_article_identifier',
           'get_published_standard_identifier',
           'get_patent_identifier',
           'get_report_identifier',
           'get_map_identifier',
           'get_website_identifier',

           'get_medium',
           'get_journal_article_medium',
           'get_preprint_article_medium',
           'get_book_chapter_medium',
           'get_book_medium',
           'get_proceedings_article_medium',
           'get_published_standard_medium',
           'get_patent_medium',
           'get_report_medium',
           'get_map_medium',
           'get_website_medium',

           'get_series',
           'get_book_series',
           'get_report_series',
           'get_map_series',
           'get_map_scale',

           'get_doi',
           'get_journal_article_doi',
           'get_preprint_article_doi',
           'get_book_chapter_doi',
           'get_book_doi',
           'get_proceedings_article_doi',
           'get_published_standard_doi',
           'get_patent_doi',
           'get_report_doi',
           'get_map_doi',
           'get_website_doi',

           'get_url_reference',
           'get_journal_article_url_reference',
           'get_preprint_article_url_reference',
           'get_book_chapter_url_reference',
           'get_book_url_reference',
           'get_proceedings_article_url_reference',
           'get_published_standard_url_reference',
           'get_patent_url_reference',
           'get_report_url_reference',
           'get_map_url_reference',
           'get_website_url_reference',

           'journal_article_reference_json',
           'preprint_article_reference_json',
           'book_chapter_reference_json',
           'book_reference_json',
           'proceedings_article_reference_json',
           'published_standard_reference_json',
           'patent_reference_json',
           'report_reference_json',
           'map_reference_json',
           'website_reference_json']


def get_reference_type(value):
    return value.get(TYPE_FIELD_NAME, None)


def get_reference_choice(value, default_value=None):
    ref_type = get_reference_type(value)
    return value.get(ref_type, default_value)


def get_book(value, default_value=""):
    reference = get_reference_choice(value, {})
    book = reference.get(BOOK_REFERENCE, default_value)
    return {TYPE_FIELD_NAME: BOOK_REFERENCE, BOOK_REFERENCE: book}


def get_title(value, default_value=""):
    reference = get_reference_choice(value, {})
    title = reference.get("title", default_value)
    return title


get_journal_article_title = get_title
get_preprint_article_title = get_title
get_book_chapter_title = get_title
get_book_title = get_title
get_proceedings_article_title = get_title
get_published_standard_title = get_title
get_patent_title = get_title
get_report_title = get_title
get_map_title = get_title
get_website_title = get_title


def get_year(value, default_value=None):
    reference = get_reference_choice(value, {})
    year = reference.get("year", default_value)
    return year


get_journal_article_year = get_year
get_preprint_article_year = get_year
get_book_chapter_year = get_year
get_book_year = get_year
get_proceedings_article_year = get_year
get_published_standard_year = get_year
get_patent_year = get_year
get_report_year = get_year
get_map_year = get_year
get_website_year = get_year


def get_names_for_role(value, role, identifier, default_value=None, style=None): # noqa
    reference = get_reference_choice(value)
    names = reference.get(identifier, {"role": "", "names": []})

    names_role = names.get("role", "")

    if names_role != role:
        return default_value

    # result = names.get("names", default_value)
    result = names
    return result


def get_authors(value, default_value=None):
    return get_names_for_role(value, role="author", identifier="authors", default_value=default_value)


get_journal_article_authors = get_authors
get_preprint_article_authors = get_authors
get_book_chapter_authors = get_authors


def get_book_authors(value, default_value=None):
    return get_names_for_role(value, role="author", identifier="authors_or_editors", default_value=default_value)


get_proceedings_article_authors = get_authors


def get_report_authors(value, default_value=None):
    return get_names_for_role(value, role="author", identifier="authors", default_value=default_value)


get_map_authors = get_authors


def get_website_authors(value, default_value=None):
    return get_names_for_role(value, role="author", identifier="authors_or_editors", default_value=default_value)


def get_published_standard_authority(value, default_value=None):
    reference = get_reference_choice(value, {})
    authority = reference.get("authority", default_value)
    return authority


def get_patent_inventors(value, default_value=None):
    return get_names_for_role(value, role="inventor", identifier="inventors", default_value=default_value)


def get_book_editors(value, default_value=None):
    return get_names_for_role(value, role="editor", identifier="authors_or_editors", default_value=default_value)


def get_proceedings_article_editors(value, default_value=None):
    return get_names_for_role(value, role="editor", identifier="editors", default_value=default_value)


def get_report_editors(value, default_value=None):
    return get_names_for_role(value, role="editor", identifier="authors_or_editors", default_value=default_value)


def get_website_editors(value, default_value=None):
    return get_names_for_role(value, role="editor", identifier="authors_or_editors", default_value=default_value)


def get_publisher_name(value, default_value=None):
    reference = get_reference_choice(value, {})
    publisher = reference.get("publisher", {})
    name = publisher.get("name", default_value)
    return name


get_journal_article_publisher_name = get_publisher_name
get_preprint_article_publisher_name = get_publisher_name
get_book_chapter_publisher_name = get_publisher_name
get_book_publisher_name = get_publisher_name
get_proceedings_article_publisher_name = get_publisher_name
get_published_standard_publisher_name = get_publisher_name
get_patent_publisher_name = get_publisher_name
get_report_publisher_name = get_publisher_name
get_map_publisher_name = get_publisher_name
get_website_publisher_name = get_publisher_name


def get_journal_article_journal_name(value, default_value=None):
    reference = get_reference_choice(value, {})
    journal_name = reference.get("journal_name", default_value)
    return journal_name


def get_journal_article_short_journal_name(value, default_value=None):
    reference = get_reference_choice(value, {})
    short_journal_name = reference.get("short_journal_name", default_value)
    return short_journal_name


def get_preprint_article_journal_name(value, default_value=None):
    reference = get_reference_choice(value, {})
    status = reference.get("publication_status", default_value)
    journal_name = status.get("journal_name", default_value)
    return journal_name


def get_preprint_article_repository_name(value, default_value=None):
    reference = get_reference_choice(value, {})
    journal_name = reference.get("repository_name", default_value)
    return journal_name


def get_book_chapter_book_title(value, default_value=None):
    reference = get_reference_choice(value, {})
    book = reference.get("book", {})
    title = book.get("title", default_value)
    return title


def get_proceedings_article_conference_title(value, default_value=None):
    reference = get_reference_choice(value, {})
    title = reference.get("conference_title", default_value)
    return title


def get_book_edition(value, default_value=None):
    reference = get_reference_choice(value, {})
    edition = reference.get("edition", default_value)
    return edition


def get_journal_article_issue(value, default_value=None):
    reference = get_reference_choice(value, {})
    issue = reference.get("issue", default_value)
    return issue


def get_book_isbn(value, default_value=None):
    reference = get_reference_choice(value, {})
    isbn = reference.get("isbn", {})
    isbn = isbn.get("number", default_value)
    return isbn


def get_identifier(value, default_value=None):
    reference = get_reference_choice(value, {})
    identifier = reference.get("identifier", default_value)
    return identifier


get_journal_article_identifier = get_identifier
get_preprint_article_identifier = get_identifier
get_book_chapter_identifier = get_identifier
get_book_identifier = get_identifier
get_proceedings_article_identifier = get_identifier
get_published_standard_identifier = get_identifier
get_patent_identifier = get_identifier
get_report_identifier = get_identifier
get_map_identifier = get_identifier
get_website_identifier = get_identifier


def get_medium(value, default_value=None):
    reference = get_reference_choice(value, {})
    medium = reference.get("medium", default_value)
    return medium


get_journal_article_medium = get_medium
get_preprint_article_medium = get_medium
get_book_chapter_medium = get_medium
get_book_medium = get_medium
get_proceedings_article_medium = get_medium
get_published_standard_medium = get_medium
get_patent_medium = get_medium
get_report_medium = get_medium
get_map_medium = get_medium
get_website_medium = get_medium


def get_series(value, default_value=None):
    reference = get_reference_choice(value, {})
    series = reference.get("series", default_value)
    return series


get_book_series = get_series
get_report_series = get_series
get_map_series = get_series


def get_map_scale(value, default_value=None):
    reference = get_reference_choice(value, {})
    scale = reference.get("scale", default_value)
    return scale


def get_doi(value, default_value=None):
    reference = get_reference_choice(value, {})
    doi = reference.get("doi", default_value)
    return doi


get_journal_article_doi = get_doi
get_preprint_article_doi = get_doi
get_book_chapter_doi = get_doi
get_book_doi = get_doi
get_proceedings_article_doi = get_doi
get_published_standard_doi = get_doi
get_patent_doi = get_doi
get_report_doi = get_doi
get_map_doi = get_doi
get_website_doi = get_doi


def get_url_reference(value, default_value=None):
    reference = get_reference_choice(value, {})
    url = reference.get("url", default_value)
    return url


get_journal_article_url_reference = get_url_reference
get_preprint_article_url_reference = get_url_reference
get_book_chapter_url_reference = get_url_reference
get_book_url_reference = get_url_reference
get_proceedings_article_url_reference = get_url_reference
get_published_standard_url_reference = get_url_reference
get_patent_url_reference = get_url_reference
get_report_url_reference = get_url_reference
get_map_url_reference = get_url_reference
get_website_url_reference = get_url_reference


def journal_article_reference_json(
        title="",
        year="",
        authors=None,
        journal_name="",
        issue=None,
        pages=None,
        doi=None):

    if authors is None:
        authors = {}

    if pages is None:
        pages = {}

    if issue is None:
        issue = {}

    if doi is None:
        doi = {}

    result = {
        "title": title,
        "year": year,
        "authors": authors,
        "journal_name": journal_name,
        "issue": issue,
        "pages": pages,
        "doi": doi
    }

    result = {
        TYPE_FIELD_NAME: JOURNAL_ARTICLE_REFERENCE,
        JOURNAL_ARTICLE_REFERENCE: result
    }

    return result


def preprint_article_reference_json(
        title="",
        year="",
        authors=None,
        publication_status=None,
        repository_name="",
        url_reference=None):

    if authors is None:
        authors = {}

    if publication_status is None:
        publication_status = {}

    if url_reference is None:
        url_reference = {}

    result = {
        "title": title,
        "year": year,
        "authors": authors,
        "publication_status": publication_status,
        "repository_name": repository_name,
        "url": url_reference,
    }

    result = {
        TYPE_FIELD_NAME: PREPRINT_ARTICLE_REFERENCE,
        PREPRINT_ARTICLE_REFERENCE: result
    }

    return result


def book_chapter_reference_json(
        title="",
        year="",
        authors=None,
        pages=None,
        book=None,
        doi=None,
        url_reference=None):

    if authors is None:
        authors = {}

    if pages is None:
        pages = {}

    if book is None:
        book = {}

    if doi is None:
        doi = {}

    if url_reference is None:
        url_reference = {}

    result = {
        "title": title,
        "year": year,
        "authors": authors,
        "pages": pages,
        "book": book,
        "doi": doi,
        "url": url_reference,
    }

    result = {
        TYPE_FIELD_NAME: BOOK_CHAPTER_REFERENCE,
        BOOK_CHAPTER_REFERENCE: result
    }

    return result


def book_reference_json(
        title="",
        year="",
        authors_or_editors=None,
        publisher=None,
        isbn=None,
        medium=None,
        doi=None,
        url_reference=None,
        series=None):

    if authors_or_editors is None:
        authors_or_editors = {}

    if publisher is None:
        publisher = {}

    if isbn is None:
        isbn = {}

    if medium is None:
        medium = {}

    if doi is None:
        doi = {}

    if url_reference is None:
        url_reference = {}

    if series is None:
        series = {}

    result = {
        "title": title,
        "year": year,
        "authors_or_editors": authors_or_editors,
        "publisher": publisher,
        "isbn": isbn,
        "medium": medium,
        "doi": doi,
        "url": url_reference,
        "series": series
    }

    result = {
        TYPE_FIELD_NAME: BOOK_REFERENCE,
        BOOK_REFERENCE: result
    }

    return result


def proceedings_article_reference_json(
        title="",
        year="",
        authors=None,
        pages=None,

        conference_title="",
        editors=None,
        publisher=None,
        doi=None,
        url_reference=None):

    if authors is None:
        authors = {}

    if editors is None:
        editors = {}

    if publisher is None:
        publisher = {}

    if pages is None:
        pages = {}

    if doi is None:
        doi = {}

    if url_reference is None:
        url_reference = {}

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

    result = {
        TYPE_FIELD_NAME: PROCEEDINGS_ARTICLE_REFERENCE,
        PROCEEDINGS_ARTICLE_REFERENCE: result
    }

    return result


def published_standard_reference_json(
        title="",
        year="",
        authority=None,
        identifier="",
        publisher=None,
        url_reference=None):

    if publisher is None:
        publisher = {}

    if authority is None:
        authority = {}

    if url_reference is None:
        url_reference = {}

    result = {
        "title": title,
        "year": year,
        "authority": authority,

        "identifier": identifier,
        "publisher": publisher,

        "url": url_reference,
    }

    result = {
        TYPE_FIELD_NAME: PUBLISHED_STANDARD_REFERENCE,
        PUBLISHED_STANDARD_REFERENCE: result
    }

    return result


def patent_reference_json(
        title="",
        year="",
        inventors=None,
        identifier="",
        url_reference=None):

    if inventors is None:
        inventors = {}

    if url_reference is None:
        url_reference = {}

    result = {
        "title": title,
        "year": year,
        "inventors": inventors,
        "identifier": identifier,
        "url": url_reference,
    }

    result = {
        TYPE_FIELD_NAME: PATENT_REFERENCE,
        PATENT_REFERENCE: result
    }

    return result


def report_reference_json(
        title="",
        year="",
        authors_or_editors=None,
        identifier="",
        publisher=None,
        series=None,
        url_reference=None):

    if authors_or_editors is None:
        authors_or_editors = {}

    if publisher is None:
        publisher = {}

    if series is None:
        series = {}

    if url_reference is None:
        url_reference = {}

    result = {
        "title": title,
        "year": year,
        "authors_or_editors": authors_or_editors,
        "identifier": identifier,
        "publisher": publisher,
        "series": series,
        "url": url_reference,
    }

    result = {
        TYPE_FIELD_NAME: REPORT_REFERENCE,
        REPORT_REFERENCE: result
    }

    return result


def map_reference_json(
        title="",
        year="",
        authors=None,
        scale="",
        identifier="",
        publisher=None,
        series=None,
        url_reference=None):

    if authors is None:
        authors = {}

    if publisher is None:
        publisher = {}

    if series is None:
        series = {}

    if url_reference is None:
        url_reference = {}

    result = {
        "title": title,
        "year": year,
        "authors": authors,
        "scale": scale,
        "identifier": identifier,
        "publisher": publisher,
        "series": series,
        "url": url_reference,
    }

    result = {
        TYPE_FIELD_NAME: MAP_REFERENCE,
        MAP_REFERENCE: result
    }

    return result


def website_reference_json(
        title="",
        year="",
        authors_or_editors=None,
        url_reference=None):

    if authors_or_editors is None:
        authors_or_editors = {}

    if url_reference is None:
        url_reference = {}

    result = {
        "title": title,
        "year": year,
        "authors_or_editors": authors_or_editors,
        "url": url_reference,
    }

    result = {
        TYPE_FIELD_NAME: WEBSITE_REFERENCE,
        WEBSITE_REFERENCE: result
    }

    return result

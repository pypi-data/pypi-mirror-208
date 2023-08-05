from django.apps import apps
from django.db.models import CharField, TextField, PositiveSmallIntegerField, Model
from django.utils.functional import cached_property

from wagtail.search import index


from officekit import models as officekit # noqa

from .apps import get_app_label
from .formatting.markup import *
from .identifiers import *
from .block_auxiliaries import *
from .plain_name_format import *
from .harvard_style import *

__all__ = ['ReferenceIndex']

APP_LABEL = get_app_label()
MODEL_MARKUP_FORMAT = MarkupFormat()


def simplify_format(format_function):
    return lambda x: format_function(x, [(0, [(0, x)])], MODEL_MARKUP_FORMAT)


name_list_plain_format = simplify_format(name_list_plain_style())

name_list_format = simplify_format(name_list_harvard_style(include_role=True))
name_list_no_role_format = simplify_format(name_list_harvard_style(include_role=False))

given_names_and_initials_format = simplify_format(given_names_and_initials_harvard_style())

title_format = simplify_format(title_harvard_style())
isbn_format = simplify_format(isbn_harvard_style())
identifier_format = simplify_format(identifier_harvard_style())
scale_format = simplify_format(scale_harvard_style())
medium_format = simplify_format(medium_harvard_style())
series_format = simplify_format(series_harvard_style(""))
doi_format = simplify_format(doi_harvard_style(""))


class ReferenceIndex(index.Indexed, Model):

    class Meta:
        abstract = True

    @cached_property
    def name_assignment_model_class(self):
        return apps.get_model(APP_LABEL + ".nameinpublication")

    author_names = CharField(default="", blank=True, max_length=512)
    editor_names = CharField(default="", blank=True, max_length=512)
    publisher_name = CharField(default="", blank=True, max_length=512)

    publication_title = TextField(default="", blank=True, max_length=512)
    container_title = TextField(default="", blank=True, max_length=512)
    short_container_title = TextField(default="", blank=True, max_length=512)

    year = PositiveSmallIntegerField(default=None, blank=True, null=True)

    edition = PositiveSmallIntegerField(default=None, blank=True, null=True)
    identifier = CharField(default=None, blank=True, max_length=256, null=True)
    medium = CharField(default=None, blank=True, max_length=256, null=True)
    series = CharField(default=None, blank=True, max_length=512, null=True)
    scale = CharField(default=None, blank=True, max_length=128, null=True)

    isbn = CharField(default=None, blank=True, max_length=48, null=True)
    doi = CharField(default=None, blank=True, max_length=256, null=True)
    url = CharField(default=None, blank=True, max_length=512, null=True)
    url_access_date = CharField(default=None, blank=True, max_length=48, null=True)

    search_fields = [
        index.SearchField('author_names'),
        index.SearchField('editor_names'),
        index.SearchField('publisher_name'),
        index.SearchField('publication_title'),
        index.SearchField('container_title'),
        index.SearchField('short_container_title'),
        index.FilterField('year'),
        index.FilterField('edition'),
        index.SearchField('identifier'),
        index.SearchField('medium'),
        index.SearchField('series'),
        index.SearchField('scale'),
        index.SearchField('isbn'),
        index.SearchField('doi'),
        index.SearchField('url'),
        index.SearchField('url_access_date'),

        index.RelatedFields('tags', [
            index.SearchField('name', partial_match=True, boost=10),
            index.AutocompleteField('name'),
        ]),
    ]

    sync_field_names = [
        "author_names",
        "editor_names",
        "publisher_name",
        "publication_title",
        "container_title",
        "short_container_title",
        "year",
        "edition",
        "identifier",
        "medium",
        "series",
        "scale",
        "isbn",
        "doi",
        "url",
        "url_access_date"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.deferred_name_assignments = []

    def clear_index_fields(self):

        self.deferred_name_assignments = []

        self.author_names = ""
        self.editor_names = ""
        self.publisher_name = ""
        self.publication_title = ""
        self.container_title = ""
        self.short_container_title = ""
        self.year = None
        self.edition = None
        self.identifier = ""
        self.medium = ""
        self.series = ""
        self.scale = ""
        self.isbn = ""
        self.doi = ""
        self.url = ""
        self.url_access_date = ""

    def sync_fields_from_reference_json(self, reference_json):

        self.clear_index_fields()

        ref_type = get_reference_type(reference_json)

        if ref_type is None:
            return

        if ref_type == JOURNAL_ARTICLE_REFERENCE:
            self.sync_fields_with_journal_article(reference_json)
        elif ref_type == PREPRINT_ARTICLE_REFERENCE:
            self.sync_fields_with_preprint_article(reference_json)
        elif ref_type == BOOK_CHAPTER_REFERENCE:
            self.sync_fields_with_book_chapter(reference_json)
        elif ref_type == BOOK_REFERENCE:
            self.sync_fields_with_book(reference_json)
        elif ref_type == PROCEEDINGS_ARTICLE_REFERENCE:
            self.sync_fields_with_proceedings_article(reference_json)
        elif ref_type == PUBLISHED_STANDARD_REFERENCE:
            self.sync_fields_with_published_standard(reference_json)
        elif ref_type == PATENT_REFERENCE:
            self.sync_fields_with_patent(reference_json)
        elif ref_type == REPORT_REFERENCE:
            self.sync_fields_with_report(reference_json)
        elif ref_type == MAP_REFERENCE:
            self.sync_fields_with_map(reference_json)
        elif ref_type == WEBSITE_REFERENCE:
            self.sync_fields_with_website(reference_json)

    def sync_author_names_from(self, value):
        self.author_names, _ = name_list_no_role_format(value)
        self.index_names_from(value, AUTHOR_ROLE)

    def sync_editor_names_from(self, value):
        self.editor_names, _ = name_list_no_role_format(value)
        self.index_names_from(value, EDITOR_ROLE)

    def sync_publisher_name(self, value):
        self.publisher_name, _ = title_format(value)

    def sync_publication_title(self, value):
        self.publication_title, _ = title_format(value)

    def sync_container_title(self, value):
        self.container_title, _ = title_format(value)

    def sync_short_container_title(self, value):
        self.short_container_title, _ = title_format(value)

    def sync_year(self, value):
        self.year = value

    def sync_edition(self, value):
        self.edition = value

    def sync_isbn(self, value):
        self.isbn, _ = isbn_format(value)

    def sync_identifier(self, value):
        self.identifier, _ = identifier_format(value)

    def sync_medium(self, value):
        self.medium, _ = medium_format(value)

    def sync_series(self, value):
        self.series, _ = series_format(value)

    def sync_scale(self, value):
        self.scale, _ = scale_format(value)

    def sync_doi(self, value):
        self.doi, _ = doi_format(value)

    def sync_url_reference(self, value):
        self.url = value.get("url", "")
        self.url_access_date = value.get("access_date", "")

    def sync_fields_with_journal_article(self, reference_json):
        self.sync_author_names_from(get_journal_article_authors(reference_json))
        self.sync_publication_title(get_journal_article_title(reference_json))
        self.sync_container_title(get_journal_article_journal_name(reference_json))
        self.sync_short_container_title(get_journal_article_journal_name(reference_json))
        self.sync_year(get_journal_article_year(reference_json))
        self.sync_doi(get_journal_article_doi(reference_json))

    def sync_fields_with_preprint_article(self, reference_json):
        self.sync_author_names_from(get_preprint_article_authors(reference_json))
        self.sync_publication_title(get_preprint_article_title(reference_json))
        self.sync_container_title(get_preprint_article_journal_name(reference_json))
        self.sync_year(get_preprint_article_year(reference_json))
        self.sync_url_reference(get_preprint_article_url_reference(reference_json))

    def sync_fields_with_book_chapter(self, reference_json):
        self.sync_author_names_from(get_book_chapter_authors(reference_json))
        self.sync_editor_names_from(get_book_editors(get_book(reference_json)))
        self.sync_publication_title(get_book_chapter_title(reference_json))
        self.sync_container_title(get_book_chapter_book_title(reference_json))
        self.sync_year(get_book_chapter_year(reference_json))
        self.sync_doi(get_book_chapter_doi(reference_json))
        self.sync_url_reference(get_book_chapter_url_reference(reference_json))

    def sync_fields_with_book(self, reference_json):
        self.sync_author_names_from(get_book_authors(reference_json))
        self.sync_editor_names_from(get_book_editors(reference_json))
        self.sync_publisher_name(get_book_publisher_name(reference_json))
        self.sync_publication_title(get_book_title(reference_json))
        self.sync_year(get_book_year(reference_json))
        self.sync_edition(get_book_edition(reference_json))
        self.sync_isbn(get_book_isbn(reference_json))
        self.sync_medium(get_book_medium(reference_json))
        self.sync_doi(get_book_doi(reference_json))
        self.sync_url_reference(get_book_url_reference(reference_json))
        self.sync_series(get_book_series(reference_json))

    def sync_fields_with_proceedings_article(self, reference_json):
        self.sync_author_names_from(get_proceedings_article_authors(reference_json))
        self.sync_editor_names_from(get_proceedings_article_editors(reference_json))
        self.sync_publisher_name(get_proceedings_article_publisher_name(reference_json))
        self.sync_publication_title(get_proceedings_article_title(reference_json))
        self.sync_container_title(get_proceedings_article_conference_title(reference_json))
        self.sync_year(get_proceedings_article_year(reference_json))
        self.sync_doi(get_proceedings_article_doi(reference_json))
        self.sync_url_reference(get_proceedings_article_url_reference(reference_json))

    def sync_fields_with_published_standard(self, reference_json):

        value = [
            {"type": "organisation ", "value": get_published_standard_authority(reference_json)}
        ]

        value = {"role": "author", "names": value}

        self.sync_author_names_from(value)
        self.sync_publisher_name(get_published_standard_publisher_name(reference_json))
        self.sync_publication_title(get_published_standard_title(reference_json))
        self.sync_year(get_published_standard_year(reference_json))
        self.sync_identifier(get_published_standard_identifier(reference_json))
        self.sync_url_reference(get_published_standard_url_reference(reference_json))

    def sync_fields_with_patent(self, reference_json):
        self.sync_author_names_from(get_patent_inventors(reference_json))
        self.sync_publication_title(get_patent_title(reference_json))
        self.sync_year(get_patent_year(reference_json))
        self.sync_identifier(get_patent_identifier(reference_json))
        self.sync_url_reference(get_patent_url_reference(reference_json))

    def sync_fields_with_report(self, reference_json):
        self.sync_author_names_from(get_report_authors(reference_json))
        self.sync_editor_names_from(get_report_editors(reference_json))
        self.sync_publisher_name(get_report_publisher_name(reference_json))
        self.sync_publication_title(get_report_title(reference_json))
        self.sync_year(get_report_year(reference_json))
        self.sync_identifier(get_report_identifier(reference_json))
        self.sync_series(get_report_series(reference_json))
        self.sync_url_reference(get_report_url_reference(reference_json))

    def sync_fields_with_map(self, reference_json):
        self.sync_author_names_from(get_map_authors(reference_json))
        self.sync_publisher_name(get_map_publisher_name(reference_json))
        self.sync_publication_title(get_map_title(reference_json))
        self.sync_year(get_map_year(reference_json))
        self.sync_identifier(get_map_identifier(reference_json))
        self.sync_series(get_map_series(reference_json))
        self.sync_scale(get_map_scale(reference_json))
        self.sync_url_reference(get_map_url_reference(reference_json))

    def sync_fields_with_website(self, reference_json):
        self.sync_author_names_from(get_website_authors(reference_json))
        self.sync_editor_names_from(get_website_editors(reference_json))
        self.sync_publication_title(get_website_title(reference_json))
        self.sync_year(get_website_year(reference_json))
        self.sync_url_reference(get_website_url_reference(reference_json))

    def create_name_assignment(self, family_name, given_names_and_initials, person, role):

        assignment = self.name_assignment_model_class(
                            publication_id=self.pk,
                            family_name=family_name,
                            given_names_and_initials=given_names_and_initials,
                            person_id=person.pk if person else None,
                            role=role)

        self.deferred_name_assignments.append(assignment)

    def clean_name_index(self, role):
        filters = {
            'publication_id': self.pk
        }

        if role:
            filters['role'] = role

        self.name_assignment_model_class.objects.filter(**filters).delete()

    def index_names_from(self, value, role):

        names = value.get("names", [])
        names = [name for name in names if name["type"] == "person"]

        for idx, name in enumerate(names):

            name_type = name['type']

            if name_type != 'person':
                continue

            person_name = name['value']

            given_names_and_initials = person_name['given_names_and_initials']
            family_name = person_name['family_name']

            given_names_and_initials = given_names_and_initials.strip()
            family_name = family_name.strip()

            identify_with = person_name.get("identify_with", None)

            person = None

            if identify_with:

                try:
                    person = officekit.Person.objects.get(pk=identify_with)
                except officekit.Person.DoesNotExist:
                    pass
            else:

                people = officekit.Person.objects.all().filter(
                    given_names_and_initials__iexact=given_names_and_initials,
                    family_name__iexact=family_name)

                n = people.count()

                if n == 1:
                    person = people[0]

            if person:

                given_names_and_initials, _ = given_names_and_initials_format(person.given_names_and_initials)
                family_name = person.family_name

                given_names_and_initials = given_names_and_initials.strip()
                family_name = family_name.strip()

            self.create_name_assignment(family_name=family_name, given_names_and_initials=given_names_and_initials,
                                        person=person, role=role)

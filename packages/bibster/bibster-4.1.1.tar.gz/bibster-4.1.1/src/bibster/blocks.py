import datetime
import re

from django import forms
from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property

from wagtail.telepath import register
from wagtail.admin.staticfiles import versioned_static

from wagtail import blocks

from wagtail_switch_block.blocks import SwitchBlock, SwitchBlockAdapter, SwitchValue, TYPE_FIELD_NAME

from querykit.base import *
from querykit.value_types import *
from querykit.value_sources import *
from querykit.forms import PickerFactory, SelectFactory, Choice


from wagtail_content_block.annotations import *
from wagtail_content_admin.blocks import ContentBlock, ContentBlockValue, register_content_block
from wagtail_content_block.dotted_paths import value_at_dotted_path, parse_dotted_path_components

from media_catalogue.blocks import MediaItemChooserBlock, MediaItemChooserBlockValue

from aldine.blocks import BaseContentLayoutBlock
from figurative.blocks import FigureBlock, SlideshowBlock
from officekit.blocks import NameListBlock as DefaultNameListBlock, OrganisationNameBlock

from django_auxiliaries.templatetags.django_auxiliaries_tags import tagged_static

from .identifiers import *

from .apps import get_app_label


__all__ = ['ReferenceBlock', 'ReferenceValue',
           'PublicationMediaBlock', 'PublicationMediaBlockValue',
           'PublicationChooserBlock', 'PublicationChooserBlockValue', 'PublicationsBlock', 'PublicationsBlockValue',
           'PublicationLayoutBlock', 'PublicationListBlock', 'PublicationShowcaseBlock']

APP_LABEL = get_app_label()

TRANSLATION_LABEL = "Translation"
DOI_LABEL = "Digital Object Identifier (DOI)"
URL_LABEL = "Uniform Resource Locator (URL)"
SERIES_LABEL = "Series"


class NameListBlock(DefaultNameListBlock):

    role = blocks.ChoiceBlock(choices=[], default=None, required=False)

    def __init__(self, local_blocks=None, choices=None, default_choice=None, **kwargs):

        if choices is None:
            choices = []

        if local_blocks:
            local_block_dict = dict(local_blocks)
        else:
            local_block_dict = {}

        local_block_dict["role"] = blocks.ChoiceBlock(choices=choices, default=default_choice)

        local_blocks = local_block_dict.items()

        self.constructor_kwargs_ = kwargs

        super().__init__(local_blocks, **kwargs)

        self.constructor_kwargs_["choices"] = choices
        self.constructor_kwargs_["default_choice"] = default_choice

    def deconstruct(self):
        return blocks.Block.deconstruct(self)


class DOIBlock(blocks.StructBlock):
    class Meta:
        icon = 'link'
        default = {}

    identifier = blocks.CharBlock(label="Identifier", default="", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


ISBN_RAW_RE = re.compile(r"[\s-]+", re.UNICODE)


def parse_isbn_value(value):
    digits = []

    for digit in ISBN_RAW_RE.sub("", value):

        try:
            digits.append(int(digit))
        except ValueError:
            return None, "Invalid digit"

    if len(digits) == 10:
        return digits, None
    elif len(digits) == 13:
        return digits, None
    else:
        return None, "Expected 10 or 13 digits."


class ISBNBlock(blocks.StructBlock):
    class Meta:
        icon = 'link'
        default = {}

    number = blocks.CharBlock(label="Number", default="", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class IssueBlock(blocks.StructBlock):
    class Meta:
        icon = 'link'
        default = {}

    volume_number = blocks.IntegerBlock(label="Volume Number", min_value=1, default=1, required=False)
    issue_number_or_name = blocks.CharBlock(label="Issue Number or Name", default="", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class MediumBlock(blocks.StructBlock):
    class Meta:
        icon = 'link'
        default = {}

    description = blocks.CharBlock(label="Description", default="", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class PagesBlock(blocks.StructBlock):
    class Meta:
        icon = 'link'
        default = {}

    first = blocks.CharBlock(label="First Page", default="", required=False)
    last = blocks.CharBlock(label="Last Page", default="", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class PublicationStatus(blocks.StructBlock):
    class Meta:
        default = {}

    journal_name = blocks.CharBlock(label="Journal Name", max_length=255)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class PublisherBlock(blocks.StructBlock):
    class Meta:
        icon = 'link'
        default = {}

    place = blocks.CharBlock(label="Place", default="", required=False)
    name = blocks.CharBlock(label="Name", default="", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class SeriesBlock(blocks.StructBlock):
    class Meta:
        icon = 'link'
        default = {}

    name = blocks.CharBlock(label="Name of Series", default="", required=False)
    identifier = blocks.CharBlock(label="Identifier in Series", default="", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class TranslationBlock(blocks.StructBlock):
    class Meta:
        icon = 'link'
        default = {}

    language = blocks.CharBlock(label="Language", default="", required=False)
    translators = NameListBlock(label="Translator(s)", default="", required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class URLReferenceBlock(blocks.StructBlock):
    class Meta:
        icon = 'link'
        default = {}
        # form_template = 'hdng_web_bibliography/block_forms/url_form.html'

    url = blocks.URLBlock(label="URL", default="", required=False)
    access_date = blocks.DateTimeBlock(label="Access Date", default="", required=False)

    def clean(self, value):
        value["access_date"] = datetime.datetime.utcnow()
        value = super().clean(value)

        return value

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class SourceOptionsBlock(blocks.StreamBlock):
    class Meta:
        icon = 'link'
        default = ''
        required = False
        block_counts = {
            "translation": {'min_num': 0, 'max_num': 1},
            "doi": {'min_num': 0, 'max_num': 1},
            "url": {'min_num': 0, 'max_num': 1},
            "series": {'min_num': 0, 'max_num': 1},
        }

    translation = TranslationBlock(label=TRANSLATION_LABEL)
    doi = DOIBlock(label=DOI_LABEL)
    url = URLReferenceBlock(label=URL_LABEL)
    series = SeriesBlock(label=SERIES_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class ReferencedWorkBlock(blocks.StructBlock):
    class Meta:
        default = {}
        # form_template = 'hdng_web_bibliography/block_forms/source_form.html'

    # options = SourceOptionsBlock(label="Options")

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class JournalArticleBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    authors = NameListBlock(label="Author(s)", default={}, required=False,
                            choices=AUTHOR_ROLE_CHOICES, default_choice=AUTHOR_ROLE)

    journal_name = blocks.CharBlock(label="Journal Name", default="", required=False)
    short_journal_name = blocks.CharBlock(label="Short Journal Name", default="", required=False)
    issue = IssueBlock(label="Issue", default={}, required=False)

    pages = PagesBlock(label="Pages", default={}, required=False)
    identifier = blocks.CharBlock(label="Identifier", default="", required=False)

    # optional:

    doi = DOIBlock(label=DOI_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class PreprintArticleBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    authors = NameListBlock(label="Author(s)", default={}, required=False,
                            choices=AUTHOR_ROLE_CHOICES, default_choice=AUTHOR_ROLE)

    # publication_status = PublicationStatus(label="Publication Status", status_identifier="status",
    # choices=PUBLICATION_STATUS_CHOICES, default_choice=UNKNOWN_PUBLICATION_STATUS, required=False)
    repository_name = blocks.CharBlock(label="Repository Name", default="", required=False)

    # optional:

    url = URLReferenceBlock(label=URL_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class BookBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    authors_or_editors = NameListBlock(label="Author(s) or Editor(s)",
                                       choices=AUTHOR_OR_EDITOR_ROLE_CHOICES, default_choice=AUTHOR_ROLE, default={})

    edition = blocks.IntegerBlock(label="Edition", default=None, required=False)
    publisher = PublisherBlock(label="Publisher", default={}, required=False)
    isbn = ISBNBlock(label="ISBN", default={}, required=False)
    medium = MediumBlock(label="Medium", default={}, required=False)

    # optional:

    doi = DOIBlock(label=DOI_LABEL)
    url = URLReferenceBlock(label=URL_LABEL)
    series = SeriesBlock(label=SERIES_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class BookChapterBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    authors = NameListBlock(label="Author(s)", default={}, required=False,
                            choices=AUTHOR_ROLE_CHOICES, default_choice=AUTHOR_ROLE)

    pages = PagesBlock(label="Pages", default={}, required=False)

    book = BookBlock(label="In Book", default={}, required=False)

    # optional:

    doi = DOIBlock(label=DOI_LABEL)
    url = URLReferenceBlock(label=URL_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class ProceedingsArticleBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    authors = NameListBlock(label="Author(s)", default={}, required=False,
                            choices=AUTHOR_ROLE_CHOICES, default_choice=AUTHOR_ROLE)

    pages = PagesBlock(label="Pages", default={}, required=False)

    conference_title = blocks.CharBlock(label="Conference Title", default="", required=False)
    editors = NameListBlock(label="Editor(s)", required=False, choices=EDITOR_ROLE_CHOICES, default_choice=EDITOR_ROLE)
    publisher = PublisherBlock(label="Publisher", default={}, required=False)

    # optional:

    doi = DOIBlock(label=DOI_LABEL)
    url = URLReferenceBlock(label=URL_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class PublishedStandardBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    authority = OrganisationNameBlock(label="Authority", default={}, required=False)
    identifier = blocks.CharBlock(label="Identifier", default="", required=False)
    publisher = PublisherBlock(label="Publisher", default={}, required=False)

    # optional

    url = URLReferenceBlock(label=URL_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class PatentBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    inventors = NameListBlock(label="Inventor(s)", default={}, required=False,
                              choices=INVENTOR_ROLE_CHOICES, default_choice=INVENTOR_ROLE)
    identifier = blocks.CharBlock(label="Identifier", default="", required=False)

    # optional

    url = URLReferenceBlock(label=URL_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class ReportBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    authors_or_editors = NameListBlock(label="Author(s) or Editor(s)",
                                       choices=AUTHOR_OR_EDITOR_ROLE_CHOICES, default_choice=AUTHOR_ROLE)

    identifier = blocks.CharBlock(label="Identifier", default="", required=False)
    publisher = PublisherBlock(label="Publisher", default={}, required=False)

    # optional

    series = SeriesBlock(label=SERIES_LABEL)
    url = URLReferenceBlock(label=URL_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class MapBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    authors = NameListBlock(label="Author(s)", default={}, required=False,
                            choices=AUTHOR_ROLE_CHOICES, default_choice=AUTHOR_ROLE)

    scale = blocks.CharBlock(label="Scale", default=None, required=False)

    identifier = blocks.CharBlock(label="Identifier", default="", required=False)
    publisher = PublisherBlock(label="Publisher", default={}, required=False)

    # optional

    series = SeriesBlock(label=SERIES_LABEL)
    url = URLReferenceBlock(label=URL_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class WebsiteBlock(ReferencedWorkBlock):
    class Meta:
        default = {}

    title = blocks.CharBlock(label="Title", default="", required=False)
    year = blocks.IntegerBlock(label="Year", default=2019, required=False)
    authors_or_editors = NameListBlock(label="Author(s) or Editor(s)",
                                       choices=AUTHOR_OR_EDITOR_ROLE_CHOICES, default_choice=AUTHOR_ROLE, default={})

    url = URLReferenceBlock(label="URL", default={}, required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


ReferenceValue = SwitchValue


class ReferenceBlock(SwitchBlock):
    class Meta:
        icon = 'link'
        template = APP_LABEL + "/blocks/reference_block.html"
        default = {TYPE_FIELD_NAME: JOURNAL_ARTICLE_REFERENCE,
                   JOURNAL_ARTICLE_REFERENCE: JournalArticleBlock._meta_class.default}

    journal_article = JournalArticleBlock(label=JOURNAL_ARTICLE_LABEL)
    preprint_article = PreprintArticleBlock(label=PREPRINT_ARTICLE_LABEL)
    book_chapter = BookChapterBlock(label=BOOK_CHAPTER_LABEL)
    book = BookBlock(label=BOOK_LABEL)
    proceedings_article = ProceedingsArticleBlock(label=PROCEEDINGS_ARTICLE_LABEL)
    published_standard = PublishedStandardBlock(label=PUBLISHED_STANDARD_LABEL)
    patent = PatentBlock(label=PATENT_LABEL)
    report = ReportBlock(label=REPORT_LABEL)
    map = MapBlock(label=MAP_LABEL)
    website = WebsiteBlock(label=WEBSITE_LABEL)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class ReferenceBlockAdapter(SwitchBlockAdapter):
    # noinspection SpellCheckingInspection
    js_constructor = APP_LABEL + '.ReferenceBlock'

    def js_args(self, block):
        result = super(ReferenceBlockAdapter, self).js_args(block) + [
            reverse(APP_LABEL + ':lookup_reference')
        ]
        return result

    @cached_property
    def media(self):
        # noinspection SpellCheckingInspection
        return forms.Media(js=[
            versioned_static("wagtailadmin/js/telepath/blocks.js"),
            tagged_static('wagtail_switch_block/js/wagtail_switch_block.js'),
            tagged_static(APP_LABEL + '/js/reference_lookup.js'),
            tagged_static(APP_LABEL + '/js/reference_block.js')])


register(ReferenceBlockAdapter(), ReferenceBlock)


PUBLICATION_MEDIA_ANNOTATIONS = ContentAnnotations(groups=[
            ContentAnnotationGroup(
                identifier='caption',
                label='Caption',
                fields=[
                    TextAreaAnnotationField(
                        identifier='text',
                        label='',
                        instance_value_path='content_object.title',
                        attributes={
                                'placeholder': 'Enter caption'
                            }
                    ),

                    TextAnnotationField(
                        identifier='anchor_identifier',
                        label='Anchor Identifier',
                        attributes={
                                'placeholder': ''
                            }
                    )
                ]
            ),

            ContentAnnotationGroup(
                identifier='credits',
                label='Credits',
                fields=[
                    TextAnnotationField(
                        identifier='category',
                        label='',
                        default_value='Image',
                        attributes={
                            'placeholder': ''
                        }
                    ),

                    TextAreaAnnotationField(
                        identifier='names',
                        label='Name(s)',
                        attributes={
                            'placeholder': ''
                        }
                    )
                ]
            ),
            ContentAnnotationGroup(
                identifier='category',
                label='Category',
                fields=[
                    ChoiceAnnotationField(
                        identifier='identifier',
                        label='',
                        attributes={
                            'choices': [
                                ['figure', 'Figure'],
                                ['front_cover', 'Front Cover']
                            ]
                        }
                    )
                ]
            )
        ])


PublicationMediaBlockValue = MediaItemChooserBlockValue


class PublicationMediaBlock(MediaItemChooserBlock):

    class Meta:
        annotations = PUBLICATION_MEDIA_ANNOTATIONS


def configure_chooser_publication_item(item, instance):
    return


def create_publication_query_parameters():

    order_choices = [OrderSpecifier("year_descending", "↓ Year",
                                    PathValueSource(value_type=IntegerType, path='-year')
                                    ),

                     OrderSpecifier("year_ascending", "↑ Year",
                                    PathValueSource(value_type=IntegerType, path='year')
                                    ),

                     OrderSpecifier("title", "↑ Title",
                                    PathValueSource(value_type=TextType, path='publication_title')
                                    )
                     ]

    select_factory = SelectFactory()

    fp_factory = PickerFactory()

    parameters = [
        ResultSliceParameter(
               identifier='page',
               widget_factory=None),

        OrderParameter(
               identifier='sort_by',
               label='Sort By',
               order_specifiers=order_choices,
               widget_factory=select_factory),

        SliceSizeParameter(
               identifier='per_page',
               label='Per Page',
               size_choices=[
                    Choice(25, "25"),
                    Choice(50, "50"),
                    Choice(100, "100"),
                    Choice('all', "All")
               ],
               widget_factory=select_factory),

        Filter(identifier='year',
               value_source=PathValueSource(value_type=IntegerType, path='year'),
               widget_factory=fp_factory),
        Filter(identifier='journal',
               label='Journal',
               value_source=PathValueSource(value_type=TextType, path='short_container_title'),
               widget_factory=fp_factory),
        Filter(identifier='keyword',
               label='Keyword',
               value_source=PathValueSource(value_type=TextType, path='tags.slug', label_path='tags.name'),
               widget_factory=fp_factory),
        Filter(identifier='author',
               label='Author',
               value_source=PathValueSource(value_type=TextType,
                                            path='name_index.family_name',
                                            label_path='name_index.family_name'),
                                            widget_factory=fp_factory),
    ]

    return parameters


def create_publication_query_widgets():

    widgets = [
        "clear", "submit"
    ]

    return widgets


PublicationsBlockValue = ContentBlockValue


class PublicationsBlock(ContentBlock):
    class Meta:
        verbose_item_name = "Publication"
        verbose_item_name_plural = "Publications"

        chooser_url = APP_LABEL + ':chooser'
        configure_function_name = APP_LABEL + '.blocks.configure_chooser_publication_item'
        max_num_choices = None
        chooser_prompts = {
            'add': 'Add Publication',
            'replace': 'Replace Publication'
        }

        chooser_filter = None

        query_field_choices = [
            ('publication_title', 'Title'),
            ('container_title', 'Container Title'),
            ('short_container_title', 'Short Container Title'),
            ('year', 'Year'),
            ('tags__name', 'Tag Name'),
            ('doi', 'DOI'),
            ('isbn', 'ISBN')
        ]
        query_slice_size = 25
        query_parameters = create_publication_query_parameters()
        query_form_widgets = create_publication_query_widgets()
        query_form_classname = settings.BIBSTER_PUBLICATIONS_QUERY_FORM_CLASSNAME

    def __init__(self, **kwargs):
        super().__init__(target_model=APP_LABEL + ".publication", **kwargs)  # noqa


register_content_block(APP_LABEL, "publications", PublicationsBlock, [], {}, item_type=APP_LABEL + ".publication")  # noqa

PublicationChooserBlockValue = ContentBlockValue


class PublicationChooserBlock(PublicationsBlock):
    class Meta:
        query_block_class = None


class PublicationLayoutBlock(BaseContentLayoutBlock):
    class Meta:

        classname = settings.BIBSTER_PUBLICATION_LAYOUT_BLOCK_CLASSNAME
        publication_container_classname = settings.BIBSTER_PUBLICATION_CONTAINER_CLASSNAME
        publication_tags_classname = settings.BIBSTER_PUBLICATION_TAGS_CLASSNAME
        publication_tag_classname = settings.BIBSTER_PUBLICATION_TAG_CLASSNAME
        publication_summary_classname = settings.BIBSTER_PUBLICATION_SUMMARY_CLASSNAME

        supported_item_types = [APP_LABEL + ".publication"]

    def deconstruct(self):
        return blocks.Block.deconstruct(self)


class PublicationListBlock(PublicationLayoutBlock):
    class Meta:
        classname = settings.BIBSTER_PUBLICATION_LIST_BLOCK_CLASSNAME
        content_wrapper_classname = settings.BIBSTER_PUBLICATION_LIST_CONTENT_WRAPPER_CLASSNAME
        template = APP_LABEL + "/blocks/publication_list.html"

    figures = SwitchBlock(local_blocks=[
        ('figures', FigureBlock(user_configurable_content=False)),
        ('slideshow', SlideshowBlock(user_configurable_content=False))],
        default_block_name='slideshow',
        template=APP_LABEL + "/blocks/publication_list_switch.html")


class PublicationShowcaseBlock(PublicationLayoutBlock):
    class Meta:
        template = APP_LABEL + "/blocks/publication_showcase.html"
        match_values = ['front_cover']
        match_path = 'category.identifier'

    figures = SwitchBlock(local_blocks=[
        ('figures', FigureBlock(user_configurable_content=False)),
        ('slideshow', SlideshowBlock(user_configurable_content=False))],
        default_block_name='slideshow',
        template=APP_LABEL + "/blocks/publication_showcase_switch.html")

    def determine_content(self, value, context, request=None):

        content = super().determine_content(value, context, request=request)

        match_path = parse_dotted_path_components(self.meta.match_path)

        result_items, result_annotations = [], []

        for outer_entry in zip(content.items, content.annotations):
            publication, _ = outer_entry

            for inner_entry in publication.media.value:
                media_item, media_annotations = inner_entry

                match_value = value_at_dotted_path(media_annotations, match_path)

                if match_value not in self.meta.match_values:
                    continue

                external_url = publication.url

                if not external_url and publication.doi:

                    doi = publication.doi

                    if doi.startswith("DOI: "):
                        doi = doi[5:]

                    external_url = "https://doi.org/" + doi.strip()

                media_annotations['link'] = {
                    'page': None,
                    'page_fragment': '',
                    'external_url': external_url
                }

                result_items.append(media_item)
                result_annotations.append(media_annotations)

        arguments = {field: content[index] for index, field in enumerate(content._fields)} # noqa

        arguments['items'] = result_items
        arguments['annotations'] = result_annotations

        return self.create_content(**arguments)

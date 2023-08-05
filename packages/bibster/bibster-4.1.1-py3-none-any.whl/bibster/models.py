import json
import os

# Django

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models as django_models, transaction
from django.db.models import (ForeignKey, CharField, TextField)
from django.core.validators import RegexValidator

from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase, Tag

from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.utils import timezone

# Wagtail

from wagtail.models import Orderable
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

# Panels

from wagtail.admin.panels import FieldPanel

from django_auxiliaries.model_fields import AutoDeleteFileField
from wagtail_block_model_field.fields import BlockModelField


from officekit import models as officekit # noqa

from django_auxiliaries.model_fields import MultipleChoiceField

from .mixins import StorageMixin
from .blocks import ReferenceBlock, ReferenceValue, PublicationMediaBlock, PublicationMediaBlockValue
from .auxiliaries import ReferenceIndex

from .formatting.xml_io import inflate_style_from_xml

from .format_auxiliaries import *
from .identifiers import *

from .apps import get_app_label


__all__ = ['Publication', 'PublicationTag', 'NameInPublication']

APP_LABEL = get_app_label()

identifier_validator = RegexValidator("^[A-Za-z_][A-Za-z_0-9]*$",
                                      message=("A valid identifier starts with an alphanumeric letter or underscore " +
                                               "and contains only alphanumeric letters, underscores or digits."),
                                      code="invalid_identifier")


def get_format_upload_path(self, filename):

    # if not default_storage.exists(filename):
    filename = default_storage.get_valid_name(filename)

    # noinspection PyUnresolvedReferences
    filename = filename.encode('ascii', errors='replace').decode('ascii')

    # noinspection PyUnresolvedReferences
    path = os.path.join(self.path, filename)

    if len(path) >= 95:
        chars_to_trim = len(path) - 94
        prefix, extension = os.path.splitext(filename)
        filename = prefix[:-chars_to_trim] + extension
        # noinspection PyUnresolvedReferences
        path = os.path.join(self.path, filename)

    return path


@register_snippet
class ReferenceFormat(StorageMixin, django_models.Model):

    class Meta:
        verbose_name = 'Reference Format'
        verbose_name_plural = 'Reference Formats'
        constraints = [
            django_models.UniqueConstraint(fields=['identifier'],
                                           name='unique_%(app_label)s_%(class)s.identifier')
        ]

    @cached_property
    def format_instance(self):
        self.format_file.seek(0)
        xml_text = self.format_file.read().decode('utf-8')
        result = inflate_style_from_xml(xml_text)
        return result

    storage_root = "reference_formats"

    identifier = django_models.CharField(max_length=128, validators=[identifier_validator])

    format_file = AutoDeleteFileField(blank=True, null=True, upload_to=get_format_upload_path)

    created_at = django_models.DateTimeField(
        verbose_name=_('created at'),
        default=None,
        editable=False)

    created_by_user = django_models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('created by user'),
        null=True,
        blank=True,
        editable=False,
        on_delete=django_models.SET_NULL
    )

    panels = [
        FieldPanel('identifier'),
        FieldPanel('format_file')
    ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)   # noinspection PyUnresolvedReferences

        if not self.id: # noqa

            self.id = None
            self.created_at = timezone.now()

# ReferenceStyleAttachment = create_model_attachment_class(ReferenceStyle)


@register_snippet
class MarkupFormat(django_models.Model):

    class Meta:
        verbose_name = 'Markup Format'
        verbose_name_plural = 'Markup Formats'
        constraints = [
            django_models.UniqueConstraint(fields=['identifier'],
                                           name='unique_%(app_label)s_%(class)s.identifier')
        ]

    @cached_property
    def format_instance(self):
        self.format_file.seek(0)
        xml_text = self.format_file.read().decode('utf-8')
        result = inflate_style_from_xml(xml_text)
        return result

    storage_root = "markup_formats"

    identifier = django_models.CharField(max_length=128, validators=[identifier_validator])

    format_file = AutoDeleteFileField(blank=True, null=True, upload_to=get_format_upload_path)

    created_at = django_models.DateTimeField(
        verbose_name=_('created at'),
        default=None,
        editable=False)

    created_by_user = django_models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('created by user'),
        null=True,
        blank=True,
        editable=False,
        on_delete=django_models.SET_NULL
    )

    panels = [
        FieldPanel('identifier'),
        FieldPanel('markup_file')
    ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)   # noinspection PyUnresolvedReferences

        if not self.id: # noqa

            self.id = None
            self.created_at = timezone.now()


class PublicationTag(TaggedItemBase):
    content_object = ParentalKey(
        APP_LABEL + ".publication",
        on_delete=django_models.CASCADE,
        related_name='tagged_items'
    )


class PublicationQuerySet(django_models.QuerySet):

    def get(self, *args, **kwargs):

        result = super().get(*args, **kwargs)
        return result

    class TagQuery(object):

        def __init__(self, tag):
            self.tag = tag

        def tag(self):
            return self.tag

        def publications(self):

            publication_ids = self.tag.bibster_publicationtag_items.values_list("content_object_id", flat=True)
            publications = Publication.objects.filter(id__in=[publication_ids])
            return publications

    def publications_by_tag(self):

        tag_ids = PublicationTag.objects.distinct().values_list("tag_id", flat=True) # noqa

        values = Tag.objects.filter(id__in=[tag_ids])  # .values_list("name", flat=True) # noqa
        values = sorted(values, key=lambda tag: tag.name, reverse=False)
        values = [self.TagQuery(t) for t in values]
        return values


class BasePublicationManager(django_models.Manager):
    def get_queryset(self):
        return self._queryset_class(self.model)


PublicationManager = BasePublicationManager.from_queryset(PublicationQuerySet)


class Publication(ReferenceIndex, ClusterableModel):

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'

    objects = PublicationManager()

    live = django_models.BooleanField(verbose_name=_('live'), default=True, editable=True)

    tags = ClusterTaggableManager(through=PublicationTag, blank=True)
    reference = BlockModelField(ReferenceBlock(), value_class=ReferenceValue, default={}, blank=True)
    summary = RichTextField(default='', blank=True, editor=APP_LABEL + ".publicationsummary")
    media = BlockModelField(PublicationMediaBlock(required=False), value_class=PublicationMediaBlockValue)

    markup_cache_storage = TextField(default="{}", blank=True)

    @cached_property
    def markup_cache(self):
        result = json.loads(self.markup_cache_storage) # noqa
        return result

    panels = [
        FieldPanel('live'),
        FieldPanel('tags'),
        FieldPanel('reference'),
        FieldPanel('summary'),
        FieldPanel('media')
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.change_count_ = 0
        self.change_level_ = 0

    def __str__(self):
        result, _ = self.format(DEFAULT_STYLE)
        return result

    @cached_property
    def semantic_id(self):

        domain = list(Publication.objects.filter(year=self.year, publication_title__iexact=self.publication_title))
        domain = sorted(domain, key=lambda x: x.id)

        identifier = "{:4d}_".format(self.year) + "_".join(self.publication_title.replace('-', '_').lower().split())

        if len(domain) > 1:
            for idx, publication in enumerate(domain):
                if publication.id == self.id: # noqa
                    identifier += ":{:d}".format(idx)
                    break

        return identifier

    def format(self, style_name, markup_format_name=None, placeholder="", bypass_cache=False):

        result, metadata = format_reference(self.reference_json,
                                            style_name=style_name,
                                            markup_format_name=markup_format_name,
                                            placeholder=placeholder,
                                            markup_cache=self.markup_cache,
                                            bypass_cache=bypass_cache)

        return result, metadata

    @property
    def reference_json(self):
        value = self.reference
        return value.block.get_prep_value(value)

    @reference_json.setter
    def reference_json(self, value):
        current_value = self.reference
        python_value = current_value.block.to_python(value) # noqa
        self.reference = python_value

    def populate_markup_cache(self):
        default_value, _ = self.format(DEFAULT_STYLE, placeholder="")

        for fmt in (PLAIN_MARKUP_FORMAT, HTML_MARKUP_FORMAT):
            self.format(DEFAULT_STYLE, fmt, placeholder=default_value)

    def clear_markup_cache(self):
        self.markup_cache_storage = "{}"
        if "markup_cache" in self.__dict__:
            del self.__dict__["markup_cache"]

    def clear_index_fields(self):
        super(Publication, self).clear_index_fields()

        self.clear_markup_cache()

    def sync_fields_from_reference(self):
        self.sync_fields_from_reference_json(self.reference_json)
        self.populate_markup_cache()

    def save(self, update_fields=None, **kwargs):

        self.sync_fields_from_reference()
        self.markup_cache_storage = json.dumps(self.markup_cache)

        if update_fields is not None:
            update_fields = list(update_fields)

            for name in self.sync_field_names:
                if name in update_fields:
                    continue

                update_fields.append(name)

            if "markup_cache_storage" not in update_fields:
                update_fields.append("markup_cache_storage")

        super().save(update_fields=update_fields, **kwargs)

        self.clean_name_index(role=None)

        for assignment in self.deferred_name_assignments:
            assignment.publication = self
            assignment.save()

        self.deferred_name_assignments = []

    @classmethod
    def create_from_dois(cls, dois):

        from .auto_fill import reference_from_doi

        results = []
        references = reference_from_doi(dois)

        with transaction.atomic():

            for reference in references:

                if not reference:
                    results.append(None)

                publication = Publication()
                publication.reference_json = reference
                publication.save()
                results.append(publication)

        return results


class NameInPublication(Orderable):

    class Meta(Orderable.Meta):
        verbose_name = 'Name in Publication'
        verbose_name_plural = 'Names in Publication'
        constraints = [
            django_models.UniqueConstraint(fields=['publication', 'family_name', 'given_names_and_initials'],
                                           name='unique_%(app_label)s_%(class)s.name_assignment')
        ]

    publication = ParentalKey(Publication, related_name="name_index", on_delete=django_models.CASCADE, blank=False)

    family_name = CharField("Family Name", default="", max_length=192, blank=False)
    given_names_and_initials = CharField("Given Name(s) and Initial(s)", default="", max_length=192, blank=False)

    person = ForeignKey(officekit.Person, related_name="publications", on_delete=django_models.SET_NULL,
                        blank=True, null=True)

    role = MultipleChoiceField(choices=ROLE_CHOICES, default=AUTHOR_ROLE, blank=True, max_length=64)

    panels = [
        FieldPanel('publication'),
        FieldPanel('family_name'),
        FieldPanel('given_names_and_initials'),
        FieldPanel('person'),
        FieldPanel('role'),
    ]

    @classmethod
    def create(cls, publication, personal_name, person, role):

        result = cls(publication=publication, personal_name=personal_name, person=person, role=role)

        return result

    def __str__(self):
        return self.given_names_and_initials + " " + self.family_name + " in "  + self.publication.doi + (" [linked]" if self.person else "") # noqa

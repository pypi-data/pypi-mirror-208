import re
import os

from django.conf import settings


__all__ = ['StorageMixin']

CC_REGEXP = re.compile('([^A-Z_])([A-Z])')


def camel_case_to_snake_case(fragment):
    return CC_REGEXP.sub(r'\1_\2', fragment).lower()


class ClassProperty:

    def __init__(self, cls_get):
        self.cls_get = cls_get

    def __get__(self, instance, cls=None):

        if instance is not None:
            cls = instance.__class__

        if cls is None:
            return self

        return self.cls_get.__func__(cls)


class StorageMixin:

    class Meta:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_ = None

    @classmethod
    def get_storage_root(cls):

        if hasattr(cls._meta, 'verbose_name_plural'):
            default_root = "_".join(cls._meta.verbose_name_plural.split()).lower()
        elif hasattr(cls._meta, 'verbose_name'):
            default_root = "_".join((cls._meta.verbose_name + "s").split()).lower()
        else:
            default_root = camel_case_to_snake_case(cls.__name__)

        setting_name = cls._meta.app_label.upper() + "_" + default_root.upper() + "_STORAGE_ROOT"

        if hasattr(settings, setting_name):
            default_root = settings.setting_name

        return default_root

    storage_root = ClassProperty(cls_get=get_storage_root)

    @property
    def path(self):
        if self.path_ is None:
            self.path_ = self._build_path()

        return self.path_

    # noinspection PyMethodMayBeStatic
    def is_stored_locally(self):
        return False

    def _build_path(self):
        path = os.path.join(self.storage_root, '{:d}'.format(self.id)) # noqa
        return path

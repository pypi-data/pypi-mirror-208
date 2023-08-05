
from wagtail.permission_policies import ModelPermissionPolicy

from .apps import get_app_label

__all__ = ['permission_policy']

APP_LABEL = get_app_label()


permission_policy = ModelPermissionPolicy(
    APP_LABEL + ".publication"
)


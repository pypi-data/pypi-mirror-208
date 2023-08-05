
from wagtail.permission_policies.collections import CollectionOwnershipPermissionPolicy

from .apps import get_app_label

APP_LABEL = get_app_label()

navigation_style_permission_policy = CollectionOwnershipPermissionPolicy(
    APP_LABEL + ".navigationstyle",
    owner_field_name='created_by_user'
)

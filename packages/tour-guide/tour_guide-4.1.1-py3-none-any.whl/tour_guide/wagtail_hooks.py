
from django.utils.safestring import mark_safe

from wagtail import hooks

from .apps import get_app_label
from .anchor_features import feature_registrations as anchor_features
from .anchors import anchor_category_choices_as_json

APP_LABEL = get_app_label()

features_to_register = anchor_features

for register_feature in features_to_register:
    hooks.register('register_rich_text_features', fn=register_feature)


@hooks.register("insert_editor_js")
def editor_js():

    result = mark_safe('<script type="text/{}_anchor_categories">{}</script>'.format(
                APP_LABEL, anchor_category_choices_as_json()))
    return result

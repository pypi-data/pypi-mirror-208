# -*- coding: utf-8 -*-

from draftail_helpers.feature_registry import register_embed_feature

from wagtail.admin.rich_text.converters.html_to_contentstate import AtomicBlockEntityElementHandler, \
                                                                    InlineEntityElementHandler, Entity, KEEP_WHITESPACE
from wagtail.rich_text import EmbedHandler

from draftjs_exporter.dom import DOM

import re

from .anchor_feature_names import *
from .anchors import current_anchor_registry_and_inventory
from .apps import get_app_label

APP_LABEL = get_app_label()

"""

Anchor entity:

    action: ['define', 'link', 'label', 'labelled_link']
    category: 'figure'
    identifier: 'experiment_results'

"""

ACTION_PROPERTY = "action"
CATEGORY_PROPERTY = "category"
IDENTIFIER_PROPERTY = "identifier"
TEXT_PROPERTY = "text"
LEVEL_PROPERTY = "level"
EDITOR_SETTINGS_PROPERTY = "editor_settings"

HTML_ATTR_PREFIX = 'data-anchor-'


def editor_entity_data_to_html_attributes(props):

    attrs = {
        HTML_ATTR_PREFIX + EDITOR_SETTINGS_PROPERTY: props.get(EDITOR_SETTINGS_PROPERTY, ""),
    }

    return attrs


def html_attributes_to_editor_entity_data(attrs):

    props = {
        EDITOR_SETTINGS_PROPERTY: attrs.get(HTML_ATTR_PREFIX + EDITOR_SETTINGS_PROPERTY, "")
    }

    return props


def anchor_editor_entity_data_to_db(props, embed_type):

    attrs = editor_entity_data_to_html_attributes(props)

    attrs.update({
        'embedtype': embed_type,
        HTML_ATTR_PREFIX + ACTION_PROPERTY: props.get(ACTION_PROPERTY, ''),
        HTML_ATTR_PREFIX + CATEGORY_PROPERTY: props.get(CATEGORY_PROPERTY, ''),
        HTML_ATTR_PREFIX + IDENTIFIER_PROPERTY: props.get(IDENTIFIER_PROPERTY, ''),
        HTML_ATTR_PREFIX + TEXT_PROPERTY: props.get(TEXT_PROPERTY, ' '),
        HTML_ATTR_PREFIX + LEVEL_PROPERTY: props.get(LEVEL_PROPERTY, 0),
    })

    result = DOM.create_element("embed", attrs)  # *props['children'])
    return result


def anchor_db_to_editor_entity_data(attrs):

    props = html_attributes_to_editor_entity_data(attrs)

    props.update({
        ACTION_PROPERTY: attrs.get(HTML_ATTR_PREFIX + ACTION_PROPERTY, ''),
        CATEGORY_PROPERTY: attrs.get(HTML_ATTR_PREFIX + CATEGORY_PROPERTY, ''),
        IDENTIFIER_PROPERTY: attrs.get(HTML_ATTR_PREFIX + IDENTIFIER_PROPERTY, ''),
        TEXT_PROPERTY: attrs.get(HTML_ATTR_PREFIX + TEXT_PROPERTY, ' '),
        LEVEL_PROPERTY: attrs.get(HTML_ATTR_PREFIX + LEVEL_PROPERTY, 0),
    })

    return props


WHITESPACE_RE = re.compile("(\\s+)$", re.UNICODE)


def anchor_db_to_frontend_html(attrs):

    registry, inventory = current_anchor_registry_and_inventory()

    if not registry:
        return '[anchor undefined]'

    action = attrs.get(HTML_ATTR_PREFIX + ACTION_PROPERTY, '')
    category = attrs.get(HTML_ATTR_PREFIX + CATEGORY_PROPERTY, '')
    identifier = attrs.get(HTML_ATTR_PREFIX + IDENTIFIER_PROPERTY, '')
    level = attrs.get(HTML_ATTR_PREFIX + LEVEL_PROPERTY, 0)
    inner = attrs.get(HTML_ATTR_PREFIX + TEXT_PROPERTY, ' ')

    try:
        level = int(level)
    except ValueError:
        level = 0

    result = ''

    if action == 'define':
        result = registry.define_anchor(inventory, category, identifier, level)
    elif action == 'link':
        result = registry.link_anchor(inventory, category, identifier, inner) + " "
    elif action == 'label':
        result = registry.label_anchor(inventory, category, identifier) + " "
    elif action == 'labelled_link':
        result = registry.label_and_link_anchor(inventory, category, identifier) + " "

    return result


class InlineAnchorEmbedHandler(EmbedHandler):

    @staticmethod
    def get_model():
        raise NotImplementedError

    def __init__(self, feature_name):
        super().__init__()
        self.identifier = feature_name

    @classmethod
    def expand_db_attributes(cls, attrs):
        return anchor_db_to_frontend_html(attrs)


class InlineAnchorHandler(InlineEntityElementHandler):

    mutability = "IMMUTABLE"

    def __init__(self, entity_type):
        super().__init__(entity_type)
        self.inner_text = ' '

    def get_attribute_data(self, attrs):
        result = anchor_db_to_editor_entity_data(attrs)
        self.inner_text = result.get(TEXT_PROPERTY, self.inner_text)
        return result

    # noinspection SpellCheckingInspection
    def handle_endtag(self, name, state, contentstate):
        state.current_block.text += self.inner_text
        super().handle_endtag(name, state, contentstate)
        state.leading_whitespace = KEEP_WHITESPACE


def register_inline_anchor_define_feature(features):

    register_embed_feature(INLINE_ANCHOR_DEFINE_FEATURE_NAME,
                           INLINE_ANCHOR_DEFINE_ENTITY_TYPE,
                           'Define Anchor',
                           'Define anchor for selected text.',
                           InlineAnchorEmbedHandler(INLINE_ANCHOR_DEFINE_FEATURE_NAME),  # embed_handler
                           lambda props: anchor_editor_entity_data_to_db(props, INLINE_ANCHOR_DEFINE_FEATURE_NAME),  # entity_decorator
                           InlineAnchorHandler(INLINE_ANCHOR_DEFINE_ENTITY_TYPE),  # database_converter
                           features,
                           key_binding=None,
                           js_media_paths=[APP_LABEL + '/js/tour_guide.js'],
                           css_media_paths=[APP_LABEL + '/css/tour_guide.css']
                           )


def register_inline_anchor_link_feature(features):

    register_embed_feature(INLINE_ANCHOR_LINK_FEATURE_NAME,
                           INLINE_ANCHOR_LINK_ENTITY_TYPE,
                           'Link',
                           'Make the selection a reference to an element on this page.',
                           InlineAnchorEmbedHandler(INLINE_ANCHOR_LINK_FEATURE_NAME),  # embed_handler
                           lambda props: anchor_editor_entity_data_to_db(props, INLINE_ANCHOR_LINK_FEATURE_NAME),  # entity_decorator
                           InlineAnchorHandler(INLINE_ANCHOR_LINK_ENTITY_TYPE),  # database_converter
                           features,
                           key_binding=None,
                           js_media_paths=[APP_LABEL + '/js/tour_guide.js'],
                           css_media_paths=[APP_LABEL + '/css/tour_guide.css']
                           )


def register_inline_anchor_labelled_link_feature(features):

    register_embed_feature(INLINE_ANCHOR_LABELLED_LINK_FEATURE_NAME,
                           INLINE_ANCHOR_LABELLED_LINK_ENTITY_TYPE,
                           'Label Link',
                           'A labelled reference to an element on this page.',
                           InlineAnchorEmbedHandler(INLINE_ANCHOR_LABELLED_LINK_FEATURE_NAME),  # embed_handler
                           lambda props: anchor_editor_entity_data_to_db(props, INLINE_ANCHOR_LABELLED_LINK_FEATURE_NAME),  # entity_decorator
                           InlineAnchorHandler(INLINE_ANCHOR_LABELLED_LINK_ENTITY_TYPE),  # database_converter
                           features,
                           key_binding=None,
                           js_media_paths=[APP_LABEL + '/js/tour_guide.js'],
                           css_media_paths=[APP_LABEL + '/css/tour_guide.css']
                           )


feature_registrations = [register_inline_anchor_define_feature,
                         register_inline_anchor_link_feature,
                         register_inline_anchor_labelled_link_feature
                         ]

feature_names = [INLINE_ANCHOR_DEFINE_FEATURE_NAME,
                 INLINE_ANCHOR_LINK_FEATURE_NAME,
                 INLINE_ANCHOR_LABELLED_LINK_FEATURE_NAME
                 ]

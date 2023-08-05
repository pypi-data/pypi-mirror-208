import re
import json
import copy
import secrets
from collections import namedtuple

from django.apps import apps
from django.db import models
from django.utils.safestring import mark_safe
from django.template.defaultfilters import capfirst

from django_auxiliaries.variable_scope import load_variable_scope

from .middleware import AnchorMiddleware
from .apps import get_app_label


__all__ = ['AnchorRegistry', 'Anchor', 'AnchorCategory', 'Token',
           'anchor_category_choices', 'anchor_category_choices_as_json',
           'cast_to_anchor_registry', 'current_anchor_registry_and_inventory',
           'number_format_choices', 'identifier_format_choices']

APP_LABEL = get_app_label()

middleware = AnchorMiddleware(None)


def anchor_category_choices():

    from .models import AnchorCategorySetting

    result = []
    settings = AnchorCategorySetting.objects.all()

    for setting in settings:
        result.append((setting.identifier, setting.name))

    return result


def anchor_category_choices_as_json():

    result = json.dumps(anchor_category_choices())
    return result


"""
def anchor_category_choices_as_dynamic_block_options():

    try:
        from wagtail_dynamic_blocks.schema import Option
    except ModuleNotFoundError:
        return []

    result = [Option(identifier=choice[0], label=choice[1]) for choice in anchor_category_choices()]

    for index, option in enumerate(result):
        option.value = option.identifier

    return result
"""


class NumberSymbol(object):

    @property
    def index(self):
        return self._index

    @property
    def text(self):
        return self._text

    def __init__(self):
        self._index = 0
        self._text = ''

    # noinspection PyMethodMayBeStatic
    def reset(self):
        return NumberSymbol()

    def increment(self, value=1):
        return self


class Base(NumberSymbol):

    @property
    def digits(self):
        return copy.deepcopy(self._digits)

    @property
    def period(self):
        return self._period

    @property
    def lowercase(self):
        return self._lowercase

    def __init__(self, digits=None, period=None, lowercase=False):
        super().__init__()

        if digits is None:
            # noinspection SpellCheckingInspection
            digits = list(zip(*'abcdefghijklmnopqrstuvwxyz'))

        for i in range(1, len(digits) - 1):
            if len(digits[i]) != len(digits[i - 1]):
                raise RuntimeError('Invalid digits specification for Base.')

        self._index = 0
        self._digits = digits
        self._period = period
        self._lowercase = lowercase

    # noinspection PyMethodMayBeStatic
    def reset(self):
        return Base(self._digits, self._period, self._lowercase)

    def increment(self, value=1):
        self._index += value

        value = self._index - 1

        if self._period:
            value = (value % self._period)

        value = value + 1

        self._text = ''

        p = len(self._digits[0])
        plane = 0

        while plane < len(self._digits):
            digits = self._digits[plane]
            self._text = digits[value % p] + self._text
            value //= p

            if value == 0:
                break

        if self._lowercase:
            self._text = self._text.lower()

        return self


DECIMAL = Base(digits=list(zip(*'1234567890')))
LETTER = Base(digits=list(zip(*'ABCDEFGHIJKLMNOPQRSTUVWXYZ')), lowercase=True)
ROMAN_NUMERAL = Base(digits=[['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'],
                             ['', 'X', 'XX', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC'],
                             ['', 'M', 'MM', 'MMM']
                            ], period=3999, lowercase=True)

"""
symbols = [Decimal Letter Numeral]
symbols = [Base(digits=[[i for i in range(10)]])
"""


def increment_order_state(state, level):
    while level > len(state):
        state.append(0)

    if level == len(state):
        state.append(-1)

    if level < len(state) - 1:
        state = state[:level + 1]

    state[level] += 1
    return state


def is_initial_state(state):
    for value in state:
        if value != 0:
            return False

    return True


class NumberFormat(object):

    def __init__(self, symbols=None, templates=None):
        super().__init__()

        if not symbols:
            symbols = [DECIMAL, DECIMAL, DECIMAL]

        if not templates:
            templates = ['{}', '{}', '({})']

        self._symbols = symbols
        self._templates = templates

    def __call__(self, state):

        result = ''

        for index, value in enumerate(state):

            symbol_index = index

            if symbol_index >= len(self._symbols):
                symbol_index = len(self._symbols) - 1

            symbol = self._symbols[symbol_index].reset()
            text = symbol.increment(value).text

            template_index = index

            if template_index >= len(self._templates):
                template_index = len(self._templates) - 1

            template = self._templates[template_index]
            text = template.format(text)
            result += text

        return result


NUMBER_FORMAT_REGISTRY = dict()


class NumberFormatRegistration:

    @property
    def identifier(self):
        return self.app_label + ":" + self.local_identifier

    def __init__(self, app_label, local_identifier, name, format_instance):
        self.app_label = app_label
        self.local_identifier = local_identifier
        self.name = name
        self.format_instance = format_instance

        app = apps.get_app_config(self.app_label)
        self.app_name = app.verbose_name


def register_number_format(app_label, local_identifier, name, format_instance):

    registration = NumberFormatRegistration(app_label=app_label, local_identifier=local_identifier,
                                            name=name, format_instance=format_instance)
    NUMBER_FORMAT_REGISTRY[registration.identifier] = registration
    return registration


def number_format_choices():

    result = [(identifier, number_format.name + " [{}]".format(number_format.app_name.title()))
              for identifier, number_format in NUMBER_FORMAT_REGISTRY.items()]

    return result


DEFAULT_NUMBER_FORMAT = register_number_format(
                            APP_LABEL, "numbers",
                            "Numbers 1, 1.1, 1.2, 2, ...",
                            NumberFormat(templates=['{}', '.{}']))

LETTERS_FORMAT = register_number_format(
                            APP_LABEL, "letters",
                            'Letters a, aa, ab, b, ...',
                            NumberFormat(symbols=[LETTER, LETTER, LETTER]))


class IdentifierFormat(object):

    def __init__(self):
        super().__init__()

    def __call__(self, category, anchor):

        if anchor is None or anchor.order is None:
            return ''

        result = "{}-".format(anchor.category)
        result += ".".join(["{:d}".format(level + 1) for level in anchor.order])
        return result


class LiteralIdentifier(IdentifierFormat):

    def __init__(self, category_prefix=False):
        super().__init__()
        self.__category_prefix = category_prefix

    def __call__(self, category, anchor):

        if anchor is None or anchor.order is None:
            return ''

        result = "{}-".format(anchor.category) if self.__category_prefix else ""
        result += anchor.identifier
        return result


IDENTIFIER_FORMAT_REGISTRY = dict()


class IdentifierFormatRegistration:

    @property
    def identifier(self):
        return self.app_label + ":" + self.local_identifier

    def __init__(self, app_label, local_identifier, name, format_instance):
        self.app_label = app_label
        self.local_identifier = local_identifier
        self.name = name
        self.format_instance = format_instance

        app = apps.get_app_config(self.app_label)
        self.app_name = app.verbose_name


def register_identifier_format(app_label, local_identifier, name, format_instance):

    registration = IdentifierFormatRegistration(app_label=app_label, local_identifier=local_identifier,
                                                name=name, format_instance=format_instance)

    IDENTIFIER_FORMAT_REGISTRY[registration.identifier] = registration
    return registration


def identifier_format_choices():

    result = [(identifier, identifier_format.name + " [{}]".format(identifier_format.app_name.title()))
              for identifier, identifier_format in IDENTIFIER_FORMAT_REGISTRY.items()]

    return result


DEFAULT_IDENTIFIER_FORMAT = register_identifier_format(
                            APP_LABEL, "generic",
                            "Generic [category]-1, [category]-1.1, [category]-1.2, [category]-2, ...",
                            IdentifierFormat())


USE_ANCHOR_IDENTIFIER_FORMAT = register_identifier_format(
                            APP_LABEL, "anchor_identifier",
                            "Anchor Identifier [anchor-id], ...",
                            LiteralIdentifier())


USE_PREFIXED_ANCHOR_IDENTIFIER_FORMAT = register_identifier_format(
                            APP_LABEL, "prefixed_anchor_identifier",
                            "Anchor Identifier [category]-[anchor-id], ...",
                            LiteralIdentifier(True))


class Anchor(object):

    @property
    def category(self):
        return self._category

    @property
    def identifier(self):
        return self._identifier

    @property
    def level(self):
        return self._level

    @property
    def order(self):
        return self._order

    @property
    def label_prefix(self):
        return self._label_prefix

    @property
    def label_prefix_order(self):
        return self._label_prefix_order

    @level.setter
    def level(self, value):
        self._level = value

    @order.setter
    def order(self, value):
        self._order = value

    @label_prefix.setter
    def label_prefix(self, value):
        self._label_prefix = value

    @label_prefix_order.setter
    def label_prefix_order(self, value):
        self._label_prefix_order = value

    def __init__(self, category, identifier, level=0, order=None):
        self._category = category
        self._identifier = identifier
        self._level = level
        self._order = order
        self._label_prefix = None
        self._label_prefix_order = None


class AnchorCategory(object):

    @property
    def identifier(self):
        return self._identifier

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def label_plural(self):
        return self._label_plural

    @label_plural.setter
    def label_plural(self, value):
        self._label_plural = value

    @property
    def label_short(self):
        return self._label_short

    @label_short.setter
    def label_short(self, value):
        self._label_short = value

    @property
    def link_css_class(self):
        return self._link_css_class

    @link_css_class.setter
    def link_css_class(self, value):
        self._link_css_class = value

    @property
    def label_css_class(self):
        return self._label_css_class

    @label_css_class.setter
    def label_css_class(self, value):
        self._label_css_class = value

    @property
    def number_format(self):
        return self._number_format

    @number_format.setter
    def number_format(self, value):
        self._number_format = value
        self._number_format_identifier = value.identifier if value else None

    @property
    def identifier_format(self):
        return self._identifier_format

    @identifier_format.setter
    def identifier_format(self, value):
        self._identifier_format = value
        self._identifier_format_identifier = value.identifier if value else None

    @property
    def sync_from_settings(self):
        return self._sync_from_settings

    def __init__(self, identifier, sync_from_settings=True):
        self._identifier = identifier
        self._sync_from_settings = sync_from_settings
        self._label = capfirst(self._identifier)
        self._label_plural = self._label + 's'
        self._label_short = self._label
        self._link_css_class = ''
        self._label_css_class = ''
        self._number_format_identifier = DEFAULT_NUMBER_FORMAT.identifier
        self._number_format = NUMBER_FORMAT_REGISTRY.get(self._number_format_identifier, DEFAULT_NUMBER_FORMAT).format_instance

        self._identifier_format_identifier = DEFAULT_IDENTIFIER_FORMAT.identifier
        self._identifier_format = IDENTIFIER_FORMAT_REGISTRY.get(self._identifier_format_identifier, DEFAULT_IDENTIFIER_FORMAT).format_instance

    def apply_settings(self):

        from .models import AnchorCategorySetting

        setting = AnchorCategorySetting.objects.get(identifier=self._identifier)

        if setting is None:
            return

        self._label = setting.label
        self._label_plural = setting.label_plural
        self._label_short = setting.label_short
        self._link_css_class = setting.link_css_class
        self._label_css_class = setting.label_css_class
        self._number_format_identifier = setting.number_format
        self._number_format = NUMBER_FORMAT_REGISTRY.get(self._number_format_identifier, DEFAULT_NUMBER_FORMAT).format_instance

        self._identifier_format_identifier = setting.identifier_format
        self._identifier_format = IDENTIFIER_FORMAT_REGISTRY.get(self._identifier_format_identifier, DEFAULT_IDENTIFIER_FORMAT).format_instance

    def create_anchor(self, identifier, level=0):
        anchor = Anchor(self.identifier, identifier, level)
        return anchor

    # noinspection PyMethodMayBeStatic
    def id_for_anchor(self, anchor):

        if anchor is None or anchor.order is None:
            return ''

        return self.identifier_format(self, anchor)

    # noinspection PyMethodMayBeStatic
    def url_for_anchor(self, anchor):

        if anchor is None:
            return ''

        return '#' + self.id_for_anchor(anchor)

    # noinspection PyMethodMayBeStatic
    def label_for_anchor(self, registry, inventory, anchor, label_format):

        if anchor is None or anchor.order is None:
            return ''

        if label_format not in ['label', 'short_label', 'no_prefix_label']:
            label_format = 'label'

        if label_format == 'short_label':
            category_prefix = self.label_short
        elif label_format == 'no_prefix_label':
            category_prefix = ''
        else:
            category_prefix = self.label

        if category_prefix:
            category_prefix += ' '

        if anchor.label_prefix:

            anchor_order = registry.get_anchor_order(inventory, do_create=False)

            if self.identifier in anchor_order:
                prefixes = anchor_order[self.identifier]
            else:
                prefixes = dict()

            if is_initial_state(prefixes.get(anchor.label_prefix, [0])):
                return category_prefix + anchor.label_prefix
            else:
                return category_prefix + anchor.label_prefix + self.number_format(anchor.label_prefix_order)

        return category_prefix + self.number_format(anchor.order)

    # noinspection PyMethodMayBeStatic
    def link_anchor(self, registry, anchor, inner):

        if self.link_css_class:
            attributes = ' class="' + self.link_css_class + '"'
        else:
            attributes = ''

        result = mark_safe('<a href="{}"{}>{}</a>'.format(registry.format_token('link', anchor), attributes, inner))
        return result

    # noinspection PyMethodMayBeStatic
    def label_anchor(self, registry, anchor, label_format):
        if not label_format:
            label_format = 'label'

        return registry.format_token(label_format, anchor)

    # noinspection PyMethodMayBeStatic
    def define_anchor(self, registry, anchor):
        result = registry.format_token('define', anchor)
        return result


Token = namedtuple('Token', ['start_offset', 'end_offset', 'directive', 'category', 'identifier', 'level'])

UNIQUE_ID_CATEGORY = ':unique_id'
COUNT_ANCHOR = ':count'
ANCHOR_ORDER = ':anchor_order'


class AnchorRegistry(models.Model):

    class Meta:
        abstract = True

    @property
    def anchor_categories(self):
        return list(self._anchor_categories.values())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name_in_context = 'anchor_inventory'
        self._anchor_categories = {}
        self._cached_inventory = None

    def reset(self):

        for anchor_category in self.anchor_categories:
            if anchor_category.sync_from_settings:
                anchor_category.apply_settings()

    def lookup_anchor_category(self, category, default=None, create=True):
        anchor_category = self._anchor_categories.get(category, None)

        if anchor_category is None:
            if create:
                anchor_category = AnchorCategory(category)
                anchor_category.apply_settings()
                self._anchor_categories[category] = anchor_category
            else:
                return default

        return anchor_category

    def add_anchor_category(self, category):
        self._anchor_categories[category.identifier] = category

    def remove_anchor_category(self, category):
        if self._anchor_categories[category.identifier] == category:
            del self._anchor_categories[category.identifier]

    def load_anchor_inventory(self, template_context):

        if template_context is not None:

            if self._name_in_context not in template_context:
                template_context[self._name_in_context] = {}

            self._cached_inventory = template_context[self._name_in_context]

        return self._cached_inventory

    # noinspection PyMethodMayBeStatic
    def count_anchors(self, inventory, category):

        if inventory is None:
            return 0

        category_dict = inventory.get(category, None) # noqa

        if category_dict is None:
            return 0

        return len(category_dict)

    def lookup_anchor(self, inventory, category, identifier, default=None, create=True):

        # inventory = self.load_anchor_inventory(template_context)

        if inventory is None:
            return default

        category_dict = inventory.get(category, None) # noqa

        if category_dict is None:
            if not create:
                return default

            category_dict = {}
            inventory[category] = category_dict

        anchor = category_dict.get(identifier, None)

        if anchor is None:
            if not create:
                return default

            anchor_category = self.lookup_anchor_category(category)
            anchor = anchor_category.create_anchor(identifier)
            category_dict[identifier] = anchor

        return anchor

    # noinspection PyMethodMayBeStatic
    def generate_unique_id(self, inventory):

        category_dict = inventory.get(UNIQUE_ID_CATEGORY, None) # noqa

        if category_dict is None:
            category_dict = {}
            inventory[UNIQUE_ID_CATEGORY] = category_dict

        while True:
            token = secrets.token_urlsafe(8)

            if token not in category_dict:
                category_dict[token] = None
                break

        return token

    # noinspection PyMethodMayBeStatic
    def count_category(self, inventory, category):

        category_dict = inventory.get(category, None) # noqa

        if category_dict is None:
            category_dict = {}
            inventory[category] = category_dict

        if COUNT_ANCHOR not in category_dict:
            category_dict[COUNT_ANCHOR] = 0

        result = category_dict[COUNT_ANCHOR] + 1
        category_dict[COUNT_ANCHOR] = result

        return result

    def url_for_anchor(self, inventory, category, identifier):
        anchor_category = self.lookup_anchor_category(category)
        anchor = self.lookup_anchor(inventory, category, identifier, create=False)
        if anchor is None:
            return ''
        result = anchor_category.url_for_anchor(anchor)
        return result

    def link_anchor(self, inventory, category, identifier, inner):
        anchor_category = self.lookup_anchor_category(category)
        anchor = self.lookup_anchor(inventory, category, identifier, create=True)
        result = anchor_category.link_anchor(self, anchor, inner)
        return result

    def label_anchor(self, inventory, category, identifier, label_format=None):
        anchor_category = self.lookup_anchor_category(category)
        anchor = self.lookup_anchor(inventory, category, identifier, create=True)
        result = anchor_category.label_anchor(self, anchor, label_format)
        return result

    def label_and_link_anchor(self, inventory, category, identifier, label_format=None):
        label_token = self.label_anchor(inventory, category, identifier, label_format)
        result = self.link_anchor(inventory, category, identifier, label_token)
        return result

    def define_anchor(self, inventory, category, identifier, level, label_prefix=None):
        anchor_category = self.lookup_anchor_category(category)
        anchor = self.lookup_anchor(inventory, category, identifier, create=True)
        anchor.level = level

        if label_prefix is not None:
            anchor.label_prefix = label_prefix

        result = anchor_category.define_anchor(self, anchor) # noqa
        return result

    # &bsol;def;results;figure;
    TOKEN_RE = re.compile(r'__anchor__:([^;]+);([^;]+);([^;]+);([0-9]+):')

    # noinspection PyMethodMayBeStatic
    def format_token(self, directive, anchor):
        return mark_safe('__anchor__:{};{};{};{:d}:'.format(
                    directive, anchor.category, anchor.identifier, anchor.level))

    # noinspection PyMethodMayBeStatic
    def match_next_token(self, text, pos=0):
        token_match = self.TOKEN_RE.search(text, pos=pos)

        if token_match is None:
            return None

        token = Token(start_offset=token_match.start(0),
                      end_offset=token_match.end(0),
                      directive=token_match.group(1),
                      category=token_match.group(2),
                      identifier=token_match.group(3),
                      level=int(token_match.group(4)))

        return token

    # noinspection PyMethodMayBeStatic
    def get_anchor_order(self, inventory, do_create=True):

        anchor_order = inventory.get(ANCHOR_ORDER, None) # noqa

        if anchor_order is None:

            if not do_create:
                return {}

            anchor_order = {}
            inventory[ANCHOR_ORDER] = anchor_order

        return anchor_order

    def order_anchor(self, inventory, category, identifier, level):

        anchor = self.lookup_anchor(inventory, category, identifier, create=True)
        anchor.level = level

        anchor_order = self.get_anchor_order(inventory)

        if category not in anchor_order:
            prefixes = {}
            anchor_order[category] = prefixes
        else:
            prefixes = anchor_order[category]

        state = self.assign_order_for_prefix(None, level, prefixes)
        anchor.order = list(state)

        if anchor.label_prefix:
            state = self.assign_order_for_prefix(anchor.label_prefix, level, prefixes)
            anchor.label_prefix_order = list(state)

    # noinspection PyMethodMayBeStatic
    def assign_order_for_prefix(self, anchor_prefix, level, prefixes):

        if anchor_prefix not in prefixes:
            state = []
            prefixes[anchor_prefix] = state
        else:
            state = prefixes[anchor_prefix]

        state = increment_order_state(state, level)
        prefixes[anchor_prefix] = state
        return state

    def resolve_token(self, inventory, directive, category, identifier):

        anchor = self.lookup_anchor(inventory, category, identifier, create=False)

        if anchor is None:
            return ''

        anchor_category = self.lookup_anchor_category(category)

        if directive == 'define':
            return anchor_category.id_for_anchor(anchor)
        elif directive == 'link':
            return anchor_category.url_for_anchor(anchor)
        elif directive.endswith('label'):
            return anchor_category.label_for_anchor(self, inventory, anchor, directive)

        return ''

    def serve(self, request):
        response = super().serve(request)  # noqa
        return middleware.process_template_response(request, response)

    def serve_preview(self, request, preview_mode):
        response = super().serve_preview(request, preview_mode)  # noqa
        return middleware.process_template_response(request, response)

    # noinspection PyMethodMayBeStatic
    def order_tokens(self, registry, inventory, tokens):

        for token in tokens:
            if token.directive != 'define':
                continue

            registry.order_anchor(inventory, token.category, token.identifier, token.level)

    # noinspection PyMethodMayBeStatic
    def apply_tokens(self, registry, inventory, tokens, text):

        result = ''
        pos = 0

        for token in tokens:

            if pos < token.start_offset:
                result += text[pos:token.start_offset]

            token_result = registry.resolve_token(inventory,
                                                  token.directive, token.category, token.identifier)

            result += token_result
            pos = token.end_offset

        if pos < len(text):
            result += text[pos:]

        return result

    # noinspection PyMethodMayBeStatic
    def parse_tokens(self, registry, text):

        tokens = []
        pos = 0

        while pos < len(text):

            token = registry.match_next_token(text, pos)

            if token is None:
                break

            tokens.append(token)
            pos = token.end_offset

        return tokens


def cast_to_anchor_registry(obj, default=None):

    if isinstance(obj, AnchorRegistry):
        return obj

    return default


def current_anchor_registry_and_inventory():

    current = load_variable_scope(APP_LABEL)
    return current.anchor_registry, current.anchor_inventory

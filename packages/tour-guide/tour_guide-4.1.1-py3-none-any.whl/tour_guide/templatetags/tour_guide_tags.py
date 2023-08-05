
from django import template
from django.templatetags.static import static

from wagtail.models import Site

from django_auxiliaries.tags import register_simple_block_tag

from ..models import lookup_navigation_style
from ..anchors import current_anchor_registry_and_inventory


from ..apps import get_app_label


APP_LABEL = get_app_label()

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context['request']).root_page


@register.simple_tag(takes_context=True)
def link_url(context, *, link, request=None):

    if not request:
        request = context.get('request', None)

    return link.determine_url(request)


@register.simple_tag(takes_context=True, name="navigation")
def parse_navigation_tag(context, *, style, request=None, page=None, render_location=None, **kwargs):

    navigation_style = lookup_navigation_style(style)

    if navigation_style is None:
        return ''

    if not request:
        request = context.get('request', None)

    if page is None:
        page = context.get('page', None)

    return navigation_style.render(request, page, render_location, context=context.flatten())


@register.simple_tag(name="define_anchor")
def parse_define_anchor_tag(category, identifier, *, level=0, label_prefix=''):

    anchor_registry, inventory = current_anchor_registry_and_inventory()

    if not anchor_registry or (not inventory and not isinstance(inventory, dict)):
        return ""

    category = str(category)
    identifier = str(identifier)
    level = int(level)
    label_prefix = str(label_prefix)

    result = anchor_registry.define_anchor(inventory, category, identifier, level, label_prefix)
    return result


@register_simple_block_tag(register, name="link_anchor", autoescape=False)
def parse_link_anchor_tag(context, nodelist, category, identifier):

    anchor_registry, inventory = current_anchor_registry_and_inventory()

    if not anchor_registry or (not inventory and not isinstance(inventory, dict)):
        return ""

    inner = nodelist.render(context)

    category = str(category)
    identifier = str(identifier)

    result = anchor_registry.link_anchor(inventory, category, identifier, inner)
    return result


@register.simple_tag(name="anchor_url")
def parse_anchor_url_tag(category, identifier):

    anchor_registry, inventory = current_anchor_registry_and_inventory()

    if not anchor_registry or (not inventory and not isinstance(inventory, dict)):
        return ""

    category = str(category)
    identifier = str(identifier)

    result = anchor_registry.url_for_anchor(inventory, category, identifier)
    return result


@register.simple_tag(name="unique_anchor_id")
def parse_unique_anchor_id_tag():

    anchor_registry, inventory = current_anchor_registry_and_inventory()

    if not anchor_registry or (not inventory and not isinstance(inventory, dict)):
        return ""

    result = anchor_registry.generate_unique_id(inventory)
    return result


@register.simple_tag(name="count_category")
def parse_count_category_tag(category):

    anchor_registry, inventory = current_anchor_registry_and_inventory()

    if not anchor_registry or (not inventory and not isinstance(inventory, dict)):
        return ""

    category = str(category)

    result = anchor_registry.count_category(inventory, category)
    return result


@register.simple_tag(name="label_anchor")
def parse_label_anchor_tag(category, identifier, *, label_format=None):

    anchor_registry, inventory = current_anchor_registry_and_inventory()

    if not anchor_registry or (not inventory and not isinstance(inventory, dict)):
        return ""

    category = str(category)
    identifier = str(identifier)

    result = anchor_registry.label_anchor(inventory, category, identifier, label_format)
    return result


def gather_style_sheets():

    urls = [static(APP_LABEL + '/css/dropdown.css'),
            static(APP_LABEL + '/css/dropdown_style.css'),
            static(APP_LABEL + '/css/breadcrumbs.css'),
            static(APP_LABEL + '/css/breadcrumbs_style.css'),
            static(APP_LABEL + '/css/site_map.css'),
            static(APP_LABEL + '/css/site_map_style.css')]

    return urls


def gather_scripts():

    urls = [static(APP_LABEL + '/js/pointer-navigation.js')]

    return urls


SUPPORT_TEMPLATE_SETTING = APP_LABEL + '/tags/support.html'


@register.inclusion_tag(SUPPORT_TEMPLATE_SETTING, name="tour_guide_support")
def tour_guide_support_tag(*, container_element, is_admin_page=False):

    result = {
        'container_element': container_element,
        'is_admin_page': is_admin_page,
        'stylesheets': gather_style_sheets(),
        'scripts': gather_scripts()
    }

    return result

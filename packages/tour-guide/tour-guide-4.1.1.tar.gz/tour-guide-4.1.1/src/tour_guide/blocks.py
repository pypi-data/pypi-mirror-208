# -*- coding: utf-8 -*-

from collections import namedtuple

from django import forms
from django.utils.functional import cached_property

from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from wagtail import blocks
from wagtail.models import Page

from wagtail.telepath import register
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.admin.staticfiles import versioned_static


from django_auxiliaries.variable_scope import load_variable_scope
from csskit.blocks import ComplexCSSUnitValueBlock

from wagtail_switch_block import DynamicSwitchBlock, SwitchBlock, SwitchValue
from wagtail_switch_block.block_registry import BlockRegistry

from wagtail_dynamic_choice.blocks import AlternateSnippetChooserBlock, DynamicMultipleChoiceBlock
from wagtail_richer_text.blocks import RichTextBlock
from wagtail_preference_blocks.targets import PreferenceTarget

from model_porter.support_mixin import ModelPorterSupportMixin
from model_porter.model_porter import WagtailFunctions

from django_auxiliaries.templatetags.django_auxiliaries_tags import tagged_static

from .apps import get_app_label
from .links import DISPLAY_CONTEXTS, LINK_RELATIONSHIPS, RichLink
from .navigation import NavigationNode
from .utilities import root_page_for_request, select_page_children

APP_LABEL = get_app_label()

__all__ = ["RichLinkBlock", "RichLinkBlockValue",
           "NavigationBlock",
           "NavigationBuilderBlock", "NavigationBuilderBlockValue", "NavigationBuilderMixin",
           "register_navigation_builder_block", # noqa
           "navigation_builder_block_choices", # noqa
           "NavigationPresenterBlock", "NavigationPresenterBlockValue", "NavigationPresenterMixin",
           "register_navigation_presenter_block", # noqa
           "navigation_presenter_block_choices", # noqa
           "PagePathBuilderBlock", "PageTreeBuilderBlock",
           "InlineDefinitionBlock", "BeginNavigationLevelBlock", "EndNavigationLevelBlock",
           "TreeTemplatesBlock", "DropdownPresenterBlock", "BreadcrumbsPresenterBlock", "SiteMapPresenterBlock",
           "SITE_NAVIGATION_PREFERENCE_TARGET",
           "BREADCRUMBS_PREFERENCE_TARGET",
           "SITE_MAP_PREFERENCE_TARGET"]


class NavigationBlock(blocks.StructBlock):

    class Meta:
        icon = 'link'
        template = APP_LABEL + '/blocks/navigation_block.html'
        default = {}

    identifier = SwitchBlock(local_blocks=[
        ('alias', AlternateSnippetChooserBlock(APP_LABEL + ".navigationstylealias", use_identifier_as_value=True)),
        ('style', AlternateSnippetChooserBlock(APP_LABEL + ".navigationstyle", use_identifier_as_value=True))
    ])

    # noinspection PyMethodMayBeStatic
    def lookup_navigation_style(self, value):

        from .models import lookup_navigation_style
        return lookup_navigation_style(value['identifier'])

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs


class RichLinkBlockValue(blocks.StructValue):

    @classmethod
    def from_rich_link(cls, block, rich_link):

        items = {
            'rich_text': rich_link.rich_text,
            'display_context': rich_link.display_context,
            'relationships': rich_link.relationships,
            'page': rich_link.page.pk if rich_link.page else None,
            'page_fragment': rich_link.page_fragment,
            'external_url': rich_link.external_url
        }

        result = block.to_python(items)
        return result

    def as_rich_link(self):

        rich_link = RichLink()

        for key, value in self.items():

            if hasattr(rich_link, key):
                setattr(rich_link, key, value)

        return rich_link

    def as_navigation_node(self):

        node = NavigationNode()

        for key, value in self.items():

            if hasattr(node, key):
                setattr(node, key, value)

        return node


class RichLinkBlock(ModelPorterSupportMixin, blocks.StructBlock):
    class Meta:
        icon = 'link'
        template = get_app_label() + '/blocks/rich_link_block.html'
        value_class = RichLinkBlockValue
        form_classname = 'rich-link-block struct-block'
        default = {}
        user_editable_display_context = True
        user_editable_relationships = True

    rich_text = RichTextBlock(label="Text", required=False, editor=APP_LABEL + ".richlinktext")

    page = blocks.PageChooserBlock(label="Page", required=False)

    page_fragment = blocks.CharBlock(label="Page Fragment", required=False,
                                     help_text="Optional identifier of element on page")

    external_url = blocks.URLBlock(label="Destination External URL", required=False)

    display_context = blocks.ChoiceBlock(label="Display Context", default="self", required=False,
                                         choices=DISPLAY_CONTEXTS)

    relationships = blocks.MultipleChoiceBlock(label="Link Relationships", default=[], required=False,
                                               choices=LINK_RELATIONSHIPS)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs

    def get_form_state(self, value):

        value = self.meta.value_class(self, value)

        if not self.meta.user_editable_display_context:
            value.pop('display_context', None)

        if not self.meta.user_editable_relationships:
            value.pop('relationships', None)

        return super().get_form_state(value)

    def clean(self, value):

        if not self.meta.user_editable_display_context:
            value['display_context'] = self.child_blocks['display_context'].get_default()

        if not self.meta.user_editable_relationships:
            value['relationships'] = self.child_blocks['relationships'].get_default()

        return super().clean(value)

    # noinspection PyMethodMayBeStatic
    def from_repository(self, value, context):

        page = value['page']
        page = WagtailFunctions.locate_page_for_path(page)
        value['page'] = page.id

        return value


class RichLinkBlockAdapter(StructBlockAdapter):

    def js_args(self, block):

        svd_child_blocks = block.child_blocks
        block.child_blocks = dict(svd_child_blocks)

        if not block.meta.user_editable_display_context:
            block.child_blocks.pop('display_context', None)

        if not block.meta.user_editable_relationships:
            block.child_blocks.pop('relationships', None)

        result = super().js_args(block)

        block.child_blocks = svd_child_blocks

        return result

    @cached_property
    def media(self):

        return super().media + forms.Media(
            css={
                "all": [tagged_static(APP_LABEL + "/css/tour_guide.css"),
                        tagged_static(APP_LABEL + "/css/tour_guide_extra.css")
                       ]
            },
            js=[
                versioned_static("wagtailadmin/js/draftail.js"),
                tagged_static(APP_LABEL + "/js/tour_guide.js")
            ]
        )


register(RichLinkBlockAdapter(), RichLinkBlock)


class NavigationBuilderBlockRegistry(BlockRegistry):

    # noinspection PyMethodMayBeStatic
    def should_register_block(self, app_label, local_identifier, block_type, block_args, block_kwargs, **kwargs):

        if not issubclass(block_type, NavigationBuilderMixin):
            raise RuntimeError("Registered block type must be a subclass of NavigationBuilderMixin")

        return True

    # noinspection PyMethodMayBeStatic
    def should_include_entry_for_container_block(self, identifier, entry, container_block):
        return True

    # noinspection PyMethodMayBeStatic
    def instantiate_block(self, identifier, entry, container_block):

        block_kwargs = dict(entry.block_kwargs)

        block = entry.block_type(*entry.block_args, **block_kwargs)
        block.set_name(identifier)

        return block


NAVIGATION_BUILDER_BLOCK_REGISTRY = NavigationBuilderBlockRegistry()
NAVIGATION_BUILDER_BLOCK_REGISTRY.define_procedures_in_caller_module("navigation_builder")


class NavigationBuilderMixin:

    def build_navigation(self, configuration, page, request, context=None):
        return None


NavigationBuilderBlockValue = SwitchValue


class NavigationBuilderBlock(DynamicSwitchBlock):

    class Meta:
        builder_blocks_function_name = APP_LABEL + ".blocks.navigation_builder_block_choices"
        choice_label = "Select Navigation Builder"

    def __init__(self, *args, **kwargs):

        builder_blocks_function_name = kwargs.pop("builder_blocks_function_name",
                                                  self._meta_class.builder_blocks_function_name) # noqa

        super().__init__(*args,
                         builder_blocks_function_name=builder_blocks_function_name,
                         child_blocks_function_name=builder_blocks_function_name,
                         **kwargs)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs

    def build_navigation(self, configuration, page, request, context=None):

        builder_block = self.child_blocks[configuration.type]
        return builder_block.build_navigation(configuration.value, page, request, context)


class NavigationPresenterBlockRegistry(BlockRegistry):

    # noinspection PyMethodMayBeStatic
    def should_register_block(self, app_label, local_identifier, block_type, block_args, block_kwargs, **kwargs):
        if not issubclass(block_type, NavigationPresenterMixin):
            raise RuntimeError("Registered block type must be a subclass of NavigationPresenterMixin")

        return True

    # noinspection PyMethodMayBeStatic
    def should_include_entry_for_container_block(self, identifier, entry, container_block):
        return True

    # noinspection PyMethodMayBeStatic
    def instantiate_block(self, identifier, entry, container_block):
        block_kwargs = dict(entry.block_kwargs)

        block = entry.block_type(*entry.block_args, **block_kwargs)
        block.set_name(identifier)

        return block


NAVIGATION_PRESENTATION_BLOCK_REGISTRY = NavigationPresenterBlockRegistry()
NAVIGATION_PRESENTATION_BLOCK_REGISTRY.define_procedures_in_caller_module("navigation_presenter")


class NavigationPresenterMixin:

    def render_navigation(self, configuration, root_node, render_location, request, context=None):
        return None


NavigationPresenterBlockValue = SwitchValue


class NavigationPresenterBlock(NavigationPresenterMixin, DynamicSwitchBlock):

    class Meta:
        presenter_blocks_function_name = APP_LABEL + ".blocks.navigation_presenter_block_choices"
        choice_label = "Select Navigation Presenter"

    def __init__(self, *args, **kwargs):

        presenter_blocks_function_name = kwargs.pop("presenter_blocks_function_name",
                                                    self._meta_class.presenter_blocks_function_name) # noqa

        super().__init__(*args,
                         presenter_blocks_function_name=presenter_blocks_function_name,
                         child_blocks_function_name=presenter_blocks_function_name,
                         **kwargs)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs

    def render_navigation(self, configuration, root_node, render_location, request, context=None):

        presenter_block = self.child_blocks[configuration.type]
        return presenter_block.render_navigation(configuration.value, root_node, render_location, request, context)


class PagePathBuilderBlock(NavigationBuilderMixin, blocks.StaticBlock):

    def build_navigation(self, configuration, page, request, context=None):

        node = None
        queryset = Page.objects.ancestor_of(page, inclusive=True).filter(depth__gt=1)

        for page in reversed(queryset):
            parent = NavigationNode.for_page(page, is_active=True)

            if node:
                parent.children.append(node)

            node = parent

        tmp_node = node
        depth = 0

        while tmp_node:
            tmp_node.depth = depth

            depth += 1

            if tmp_node.children:
                tmp_node = tmp_node.children[0]
            else:
                tmp_node = None

        return node


register_navigation_builder_block(APP_LABEL, "page_path", PagePathBuilderBlock, [], {}) # noqa


class PageTreeBuilderBlock(NavigationBuilderMixin, blocks.StructBlock):

    navigation_categories = DynamicMultipleChoiceBlock(
        choices_function_name=APP_LABEL + ".categories.navigation_category_choices"
    )

    def build_navigation(self, configuration, page, request, context=None):
        """
        Traverse all pages starting with the root page, gathering navigation links along the way
        :param page:
        :param request:
        :return: a navigation root node
        """

        navigation_categories = configuration.get('navigation_categories', [])
        root_page = root_page_for_request(request)
        active_page = page
        navigation = None

        stack = list([(root_page, 0, None, 0, None)])
        path = []

        while stack:

            page, child_index, children, index_in_parent, node = stack[-1] # noqa

            if children is None:
                # First visit
                children = select_page_children(page, navigation_categories)

                is_active = (active_page.url_path.startswith(page.url_path) if page and active_page else False)

                node = NavigationNode.for_page(page,
                                               is_active=is_active,
                                               depth=len(path),
                                               order=index_in_parent,
                                               path=list(path))

                if len(stack) > 1:
                    stack[-2][-1].children.append(node)
                else:
                    navigation = node

            if child_index >= len(children):
                # Last visit

                stack.pop()
                path.pop() if path else None

                continue

            stack[-1] = page, child_index + 1, children, index_in_parent, node

            state = children[child_index], 0, None, child_index, None
            stack.append(state)

            path.append(child_index)

        return navigation

register_navigation_builder_block(APP_LABEL, "page_tree", PageTreeBuilderBlock, [], {}) # noqa


class BeginNavigationLevelBlock(blocks.StaticBlock):

    class Meta:
        verbose_name = "Navigation Level Start"
        verbose_name_plural = "Navigation Level Starts"


class EndNavigationLevelBlock(blocks.StaticBlock):

    class Meta:
        verbose_name = "Navigation Level End"
        verbose_name_plural = "Navigation Level Ends"


InlineDefinitionBlockValue = blocks.StreamValue


class InlineDefinitionBlock(ModelPorterSupportMixin, NavigationBuilderMixin, blocks.StreamBlock):

    class Meta:
        label = "Navigation Definition"

    link = RichLinkBlock(label="Link", required=False,
                         user_editable_display_context=False,
                         user_editable_relationships=False)

    begin = BeginNavigationLevelBlock(label="Begin Level", required=False)
    end = EndNavigationLevelBlock(label="End Level", required=False)

    def deconstruct(self):
        return blocks.Block.deconstruct(self)

    # noinspection PyMethodMayBeStatic
    def from_repository(self, value, context):
        result = []

        for stream_item in value:

            block_type = stream_item["type"]
            value = stream_item["value"]

            item_block_def = self.child_blocks.get(block_type, None)

            if item_block_def is None:
                continue

            if isinstance(item_block_def, ModelPorterSupportMixin):
                value = item_block_def.from_repository(value, context)

            result.append({"type": block_type, "value": value})

        return result

    def build_navigation(self, configuration, page, request, context=None):

        path = [0]
        stack = [[]]

        for navigation_block in configuration:

            if navigation_block.block_type == 'begin':
                path.append(0)
                stack.append(stack[-1][-1].children)

            elif navigation_block.block_type == 'end':
                path.pop()
                stack.pop()

            elif navigation_block.block_type == 'link':

                node = navigation_block.value.as_navigation_node()
                node.depth = len(path)
                node.order = path[-1]
                node.path = list(path[1:])

                path[-1] = path[-1] + 1
                stack[-1].append(node)

        if len(stack[0]) != 1:

            root_page = WagtailFunctions.locate_page_for_path("/")
            navigation = NavigationNode(is_active=True, depth=0, order=0, path="/", page=root_page, rich_text="Home")
            navigation.children = stack[0]
        else:
            navigation = stack[0][0]

        return navigation


register_navigation_builder_block(APP_LABEL, "inline_definition", InlineDefinitionBlock, [], {}) # noqa


class TreeTemplatesBlock(NavigationPresenterMixin, blocks.StructBlock):

    class Meta:
        wrapper_template = APP_LABEL + '/blocks/navigation_wrapper.html'
        container_template = APP_LABEL + '/blocks/navigation_container.html'
        choices_template = APP_LABEL + '/blocks/navigation_choices.html'
        option_template = APP_LABEL + '/blocks/navigation_option.html'

        container_classname = ""

    NodeContext = namedtuple("NodeContext", ["navigation_id",
                                             "node",
                                             "node_url",
                                             "is_root",
                                             "render_location",
                                             "indentation",
                                             "options"])

    render_root = blocks.BooleanBlock(required=False, default=True)

    def deconstruct(self):
        return blocks.Block.deconstruct(self)

    # noinspection PyMethodMayBeStatic
    def create_node_context(self, navigation_id, request, node, render_location, indentation, options):

        node_url = node.determine_url(request)

        context = self.NodeContext(navigation_id=navigation_id,
                                   node=node, node_url=node_url, is_root=node and node.depth == 0,
                                   render_location=render_location, indentation=indentation,
                                   options=options)

        return context

    def contribute_to_options(self, configuration, root_node, render_location, request, options):
        pass

    # noinspection PyMethodMayBeStatic
    def render_element_template(self, template, node_context, did_enter, request):

        if not template:
            return ''

        context = node_context._asdict()  # noqa
        context["did_enter"] = did_enter
        context["did_exit"] = not did_enter

        output = render_to_string(template, context=context, request=request)
        return output

    # noinspection PyMethodMayBeStatic
    def render_wrapper(self, node_context, did_enter, request):

        template = node_context.options['wrapper_template']
        output = self.render_element_template(template, node_context, did_enter, request)
        return output

    # noinspection PyMethodMayBeStatic
    def render_container(self, node_context, did_enter, request):

        template = node_context.options['container_template']
        output = self.render_element_template(template, node_context, did_enter, request)
        return output

    # noinspection PyMethodMayBeStatic
    def render_choices(self, node_context, did_enter, request):

        template = node_context.options['choices_template']
        output = self.render_element_template(template, node_context, did_enter, request)
        return output

    # noinspection PyMethodMayBeStatic
    def render_option(self, node_context, did_enter, request):

        template = node_context.options['option_template']
        output = self.render_element_template(template, node_context, did_enter, request)
        return output

    def render_navigation(self, configuration, root_node, render_location, request, context=None):

        result = ''
        indent = 2
        indentation = ''

        scope = load_variable_scope(APP_LABEL, navigation_index=0)
        scope.navigation_index += 1
        navigation_id = 'navigation-{:d}'.format(scope.navigation_index)

        options = {key: getattr(self.meta, key) for key in dir(self.meta) if not key.startswith('_')}
        options.update(configuration)

        if context:
            options.update(context)

        self.contribute_to_options(configuration, root_node, render_location, request, options)

        render_root_option = options.get('render_root', self.child_blocks['render_root'].get_default())

        context_stack = []

        def visit(node, stack, enter):
            nonlocal result
            nonlocal indentation

            if enter:

                node_context = self.create_node_context(
                                    navigation_id, request, node, render_location, indentation, options)

                context_stack.append(node_context)

                result += self.render_container(node_context, enter, request)

                if node_context.is_root is False or render_root_option:
                    result += self.render_option(node_context, enter, request)

                if node.children:
                    result += self.render_choices(node_context, enter, request)

                indentation += ' ' * indent
            else:

                node_context = context_stack.pop()

                indentation = indentation[:-indent]

                if node.children:
                    result += self.render_choices(node_context, enter, request)

                result += self.render_option(node_context, enter, request)
                result += self.render_container(node_context, enter, request)

        wrapper_context = self.create_node_context(
                            navigation_id, request, root_node, render_location, indentation, options)

        result = self.render_wrapper(wrapper_context, True, request) + result

        root_node.traverse(visit)

        result = result + self.render_wrapper(wrapper_context, False, request)

        result = mark_safe(result)
        return result


class DropdownPresenterBlock(TreeTemplatesBlock):

    class Meta:
        js_pointer_initiator = APP_LABEL + ".PointerNavigation"
        js_touch_initiator = "adede.ui_components.HUD"
        classname = "dropdown"

        wrapper_template = APP_LABEL + '/blocks/dropdown/navigation_wrapper.html'
        container_template = APP_LABEL + '/blocks/dropdown/navigation_container.html'
        choices_template = APP_LABEL + '/blocks/dropdown/navigation_choices.html'
        option_template = APP_LABEL + '/blocks/dropdown/navigation_option.html'

    placement = blocks.ChoiceBlock(choices=[('placement-top-left', 'Top Left'),
                                            ('placement-top-right', 'Top Right'),
                                            ('placement-bottom-left', 'Bottom Left'),
                                            ('placement-bottom-right', 'Bottom Right')],

                                   required=True)

    margin = ComplexCSSUnitValueBlock()

    autohide = blocks.BooleanBlock(required=False, default=False)


register_navigation_presenter_block(APP_LABEL, "dropdown", DropdownPresenterBlock, [], {}) # noqa


class BreadcrumbsPresenterBlock(TreeTemplatesBlock):

    class Meta:
        classname = "breadcrumbs"

        wrapper_template = APP_LABEL + '/blocks/breadcrumbs/navigation_wrapper.html'
        container_template = APP_LABEL + '/blocks/breadcrumbs/navigation_container.html'
        choices_template = APP_LABEL + '/blocks/breadcrumbs/navigation_choices.html'
        option_template = APP_LABEL + '/blocks/breadcrumbs/navigation_option.html'

register_navigation_presenter_block(APP_LABEL, "breadcrumbs", BreadcrumbsPresenterBlock, [], {}) # noqa


class SiteMapPresenterBlock(TreeTemplatesBlock):

    class Meta:
        classname = "site_map"

        wrapper_template = APP_LABEL + '/blocks/site_map/navigation_wrapper.html'
        container_template = APP_LABEL + '/blocks/site_map/navigation_container.html'
        choices_template = APP_LABEL + '/blocks/site_map/navigation_choices.html'
        option_template = APP_LABEL + '/blocks/site_map/navigation_option.html'

register_navigation_presenter_block(APP_LABEL, "site_map", SiteMapPresenterBlock, [], {}) # noqa


SITE_NAVIGATION_PREFERENCE_TARGET = PreferenceTarget(APP_LABEL, 'site_navigation', 'Site Navigation')
BREADCRUMBS_PREFERENCE_TARGET = PreferenceTarget(APP_LABEL, 'breadcrumbs', 'Breadcrumbs Navigation')
SITE_MAP_PREFERENCE_TARGET = PreferenceTarget(APP_LABEL, 'site_map', 'Site Map Navigation')

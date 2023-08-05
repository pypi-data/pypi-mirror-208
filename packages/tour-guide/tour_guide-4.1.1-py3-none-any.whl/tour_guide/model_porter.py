from urllib.parse import urlparse

from model_porter.config import ModelPorterConfig
from model_porter.model_porter import WagtailFunctions

from media_catalogue.model_porter import media_chooser_value

from .blocks import RichLink, RichLinkBlock, RichLinkBlockValue

DEFAULT_RICH_LINK_BLOCK = RichLinkBlock()


def define_rich_link(*, specifier, context):

    link = RichLink()

    if not isinstance(specifier, str):

        # Try dict
        link.rich_text = specifier.get("rich_text", None)
        link.display_context = specifier.get("display_context", None)
        link.relationships = specifier.get("relationships", [])
        media_item = specifier.get("media_item", None)

        if media_item:
            media_item, _ = media_chooser_value(items=[media_item], context=context)[0]

        if media_item:
            link.media_item = media_item

        link.external_url = specifier.get("external_url", None)
        link.page_fragment = specifier.get("page_fragment", None)

        page = specifier.get("page", None)
        parts = urlparse(page)

        if parts.scheme:
            page = context.get_instance(page)
        else:
            page = WagtailFunctions.locate_page_for_path(page)

        link.page = page

    elif isinstance(specifier, str):

        # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>

        parts = urlparse(specifier)

        if parts.scheme or parts.netloc or not parts.path:
            link.external_url = specifier
        else:
            page = WagtailFunctions.locate_page_for_path(parts.path)

            if page is not None:
                link.page = page
                link.page_fragment = parts.fragment
            else:
                link.external_url = specifier

    return link


def define_rich_link_block(*, specifier, context):
    link = define_rich_link(specifier=specifier, context=context)
    return RichLinkBlockValue.from_rich_link(DEFAULT_RICH_LINK_BLOCK, link)


def create_or_update_navigation_style(*, model=None, identifier, context):
    # model argument is not used which allows this method to be used for
    # regular attributes instead of only as a create method.

    if model is None:
        from .models import NavigationStyle
        model = NavigationStyle

    try:
        instance = model.objects.get(identifier=identifier)
    except model.DoesNotExist:
        instance = model()

    return instance


class TourGuideConfig(ModelPorterConfig):

    def __init__(self, app_label, module):
        super(TourGuideConfig, self).__init__(app_label, module)
        self.register_function_action(define_rich_link, context_argument='context')
        self.register_function_action(define_rich_link_block, context_argument='context')
        self.register_function_action(create_or_update_navigation_style, context_argument='context')

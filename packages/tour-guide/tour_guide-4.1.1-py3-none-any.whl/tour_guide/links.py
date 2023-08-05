from urllib.parse import quote

from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


__all__ = ['DISPLAY_CONTEXTS', 'LINK_RELATIONSHIPS', 'BaseLink', 'RichLink']


DISPLAY_CONTEXTS = [

    ("self", _("Same browsing context")),
    ("blank", _("New browsing context")),
    ("parent", _("Parent browsing context")),
    ("top", _("Top-level browsing context")),
]

LINK_RELATIONSHIPS = [

    ("alternate", _("Alternative")),
    ("author", _("Author")),
    ("bookmark", _("Bookmark")),
    ("external", _("External")),
    ("noopener", _("Deny access to current document from destination")), # noqa
    ("noreferrer", _("No reference to current document via Referer HTTP header")) # noqa
]


@deconstructible
class BaseLink:

    @property
    def rich_text(self):
        """
        A stylised, textual description of the link that appears in the context the link is embedded in.
        :return: A :py:class:`str` or :py:class:`wagtail.rich_text.RichText` instance.
        """

        return self.__rich_text

    @rich_text.setter
    def rich_text(self, value):
        self.__rich_text = value

    @property
    def display_context(self):
        """
        The display context for this link, one of {'self', 'blank', 'parent', 'top'}
        """
        return self.__display_context

    @display_context.setter
    def display_context(self, value):
        self.__display_context = value

    @property
    def display_context_as_html(self):
        """
        The HTML identifier corresponding to the :py:attr:`.display_context`.
        """
        return "_" + self.display_context

    @property
    def relationships(self):
        """
        A list of zero or more link relationships: {'alternate', 'author', 'bookmark', 'external', 'noopener', 'noreferrer'}
        """
        return self.__relationships[:]

    @relationships.setter
    def relationships(self, value):

        if value is None:
            value = []

        if len(value) == 1 and len(value[0]) == 0:
            value = []

        self.__relationships = list(value)

    @property
    def relationships_as_html(self):
        """
        A string suitable for embedding in HTML.
        """
        return " ".join(self.relationships)

    @property
    def media_item(self):
        return self.__media_item

    @media_item.setter
    def media_item(self, value):
        self.__media_item = value

    def __init__(self, *, rich_text=None, display_context=None, relationships=None, media_item=None):
        super().__init__()

        if not rich_text:
            rich_text = ''

        if display_context is None:
            display_context = 'self'

        if relationships is None:
            relationships = []

        self.__rich_text = rich_text
        self.__display_context = display_context
        self.__relationships = list(relationships) if relationships else []
        self.__media_item = media_item

    # noinspection PyMethodMayBeStatic
    def determine_url(self, request=None, current_site=None):
        return '#'


@deconstructible
class RichLink(BaseLink):

    @property
    def page(self):
        return self.__page

    @page.setter
    def page(self, value):
        self.__page = value

    @property
    def page_fragment(self):
        return self.__page_fragment

    @page_fragment.setter
    def page_fragment(self, value):
        self.__page_fragment = value

    @property
    def external_url(self):
        return self.__external_url

    @external_url.setter
    def external_url(self, value):
        self.__external_url = value

    def __init__(self, *, page=None, page_fragment="", external_url=None, **kwargs):

        super().__init__(**kwargs)

        self.__page = page
        self.__page_fragment = page_fragment
        self.__external_url = external_url

    def determine_url(self, request=None, current_site=None):

        if self.page:

            from .models import NavigationTarget

            page = self.page.specific
            result = None

            if isinstance(page, NavigationTarget):
                rich_link = page.rich_link

                if rich_link:
                    result = rich_link.as_rich_link().determine_url(request=request, current_site=current_site)

            else:
                result = page.get_url(request=request, current_site=current_site) # noqa

            if result is None:
                # page is not routable
                return "#"

            if self.page_fragment:
                result += '#' + quote(self.page_fragment) # noqa

            return result

        if self.page_fragment:
            return '#' + quote(self.page_fragment) # noqa

        return self.external_url

    @classmethod
    def for_page(cls, page, page_fragment=None, **kwargs):

        kwargs["page"] = page
        kwargs["page_fragment"] = page_fragment
        kwargs["rich_text"] = page.title

        result = cls(**kwargs)
        return result

    @classmethod
    def for_external_url(cls, external_url, **kwargs):

        kwargs["external_url"] = external_url

        result = cls(**kwargs)
        return result

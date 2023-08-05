# -*- coding: utf-8 -*-

from collections.abc import Sequence

from django.utils.translation import get_language_from_request

from wagtail.models import Site

from .apps import get_app_label

__all__ = ['root_page_for_request', 'select_page_children']

APP_LABEL = get_app_label()


def root_page_for_request(request):

    site = Site.find_for_request(request)

    if site is None:
        site = Site.objects.select_related("root_page").get(is_default_site=True)

    language_code = get_language_from_request(request, check_path=True)

    page = site.root_page

    for translation in page.get_translations().live():

        if translation.locale.language_code == language_code:
            page = translation
            break

    return page


def get_page_categories(page):

    result = {"menu"} if page.show_in_menus else set()

    if hasattr(page, "navigation_categories"):
        navigation_categories = page.navigation_categories

        if isinstance(navigation_categories, Sequence) and not isinstance(navigation_categories, str):
            for category in navigation_categories:
                result.add(category)

    return result


def select_page_children(page, navigation_categories):
    result = [child for child in page.get_children().live()
              if not get_page_categories(child.specific).isdisjoint(navigation_categories)]
    return result

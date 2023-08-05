from django.apps import apps
from .apps import get_app_label

__all__ = ['NavigationCategory', 'navigation_category_choices']

APP_LABEL = get_app_label()


class NavigationCategory:

    __REGISTRY = {}

    @property
    def identifier(self):
        return self.app_label + ":" + self.local_identifier

    def __init__(self, app_label, local_identifier, name):

        self.app_label = app_label
        self.local_identifier = local_identifier
        self.name = name

        app = apps.get_app_config(self.app_label)
        self.app_name = app.verbose_name
        self.__class__.__REGISTRY[self.identifier] = self

    @classmethod
    def all(cls):
        return list(cls.__REGISTRY.values())


MENU_NAVIGATION_CATEGORY = NavigationCategory(APP_LABEL, 'menu', 'Menu Navigation')
SITE_MAP_NAVIGATION_CATEGORY = NavigationCategory(APP_LABEL, 'site_map', 'Site Map Navigation')


def navigation_category_choices():

    return [(category.identifier, category.name) for category in NavigationCategory.all()]


"""
def navigation_category_options():

    from wagtail_dynamic_blocks.schema.controls import Option

    return [Option(identifier=choice[0], label=choice[1], value=choice[0]) for choice in navigation_category_choices()]
"""
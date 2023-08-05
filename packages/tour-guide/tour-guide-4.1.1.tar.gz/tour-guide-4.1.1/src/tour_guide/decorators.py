from wagtail.admin.panels import FieldPanel

from .model_fields import NavigationCategoriesField

__all__ = 'chooses_navigation_categories'


def chooses_navigation_categories(cls):
    navigation_categories = NavigationCategoriesField(verbose_name="Navigation Categories")
    navigation_categories.contribute_to_class(cls, name="navigation_categories")

    panel = FieldPanel('navigation_categories')

    if 'content_panels' not in cls.__dict__:
        cls.content_panels = cls.content_panels + []

    cls.content_panels.extend([panel])

    return cls



from wagtail_dynamic_choice.model_fields import DynamicMultipleChoiceField

from .apps import get_app_label

__all__ = ['NavigationCategoriesField']

APP_LABEL = get_app_label()


class NavigationCategoriesField(DynamicMultipleChoiceField):

    def __init__(self, default=None, blank=True, **kwargs):

        self.default_argument = default

        if default is None:
            from .categories import navigation_category_choices

            choices = navigation_category_choices()

            def default():
                if choices:
                    return [choices[0][0]]
                else:
                    return []

        if 'max_length' not in kwargs:
            kwargs['max_length'] = 128

        if 'choices_function_name' not in kwargs:
            kwargs['choices_function_name'] = APP_LABEL + ".categories.navigation_category_choices"

        super().__init__(default=default, blank=blank, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        kwargs.pop('default', None)

        if self.default_argument:
            kwargs['default'] = self.default_argument

        return name, path, args, kwargs

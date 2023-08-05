import os

from django.http import Http404
import django.db.models as django_models

from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from django.utils import timezone


from wagtail.models import Page
from wagtail.snippets.models import register_snippet

# Panels

from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel

from django_auxiliaries.validators import python_identifier_validator
from wagtail_block_model_field.fields import BlockModelField
from wagtail_dynamic_choice.model_fields import DynamicChoiceField

from model_porter.support_mixin import ModelPorterSupportMixin

from .model_porter import define_rich_link_block

from .anchors import number_format_choices
from .blocks import RichLinkBlock, RichLinkBlockValue, NavigationBuilderBlock, NavigationBuilderBlockValue, \
                    NavigationPresenterBlock, NavigationPresenterBlockValue


from .decorators import chooses_navigation_categories

from .validators import validate_identifier
from .apps import get_app_label

__all__ = ['NavigationTarget', 'NavigationStyle', 'NavigationStyleAlias', 'lookup_navigation_style',
           'AnchorCategorySetting']

APP_LABEL = get_app_label()


def remove_title_field(content_panels):
    result = [p for p in content_panels if p.field_name != 'title']
    return result


@chooses_navigation_categories
class NavigationTarget(ModelPorterSupportMixin, Page):

    class Meta:
        verbose_name = 'Navigation Target'
        verbose_name_plural = 'Navigation Targets'

    rich_link = BlockModelField(
        RichLinkBlock(label="Rich Link"),
        RichLinkBlockValue
    )

    content_panels = Page.content_panels + [
        FieldPanel('rich_link', heading="Rich Link")
    ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def route(self, request, path_components):

        if not path_components:
            # Navigation placeholders are non-routeable! # noqa
            raise Http404

        return super().route(request, path_components)

    def get_url_parts(self, request=None):
        return None

    def from_repository(self, value, context):

        rich_link = value.get("rich_link", None)

        if rich_link:
            rich_link = define_rich_link_block(specifier=rich_link, context=context)
            value["rich_link"] = rich_link

        return value


def get_schema_upload_path(self, filename):

    # if not default_storage.exists(filename):
    filename = default_storage.get_valid_name(filename)

    # noinspection PyUnresolvedReferences
    filename = filename.encode('ascii', errors='replace').decode('ascii')

    # noinspection PyUnresolvedReferences
    path = os.path.join(self.path, filename)

    if len(path) >= 95:
        chars_to_trim = len(path) - 94
        prefix, extension = os.path.splitext(filename)
        filename = prefix[:-chars_to_trim] + extension
        # noinspection PyUnresolvedReferences
        path = os.path.join(self.path, filename)

    return path


@register_snippet
class NavigationStyle(django_models.Model):

    # base_form_class = NavigationStyleForm

    class Meta:
        verbose_name = 'Navigation Style'
        verbose_name_plural = 'Navigation Styles'
        constraints = [
            django_models.UniqueConstraint(fields=['identifier'],
                                           name='unique_%(app_label)s_%(class)s.identifier')
        ]

    identifier = django_models.CharField(max_length=128, validators=[python_identifier_validator])
    name = django_models.CharField(max_length=128)

    builder = BlockModelField(NavigationBuilderBlock(), value_class=NavigationBuilderBlockValue)
    presenter = BlockModelField(NavigationPresenterBlock(), value_class=NavigationPresenterBlockValue)

    created_at = django_models.DateTimeField(
        verbose_name=_('created at'),
        default=None,
        editable=False)

    created_by_user = django_models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('created by user'),
        null=True,
        blank=True,
        editable=False,
        on_delete=django_models.SET_NULL
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)   # noinspection PyUnresolvedReferences

        if not self.id: # noqa

            self.id = None
            self.created_at = timezone.now()

    def __str__(self):
        return '{}: {}'.format(self.identifier, self.name)

    def render(self, request, page, render_location, context=None):

        builder_block = self.__class__.builder.field.block_def # noqa
        presenter_block = self.__class__.presenter.field.block_def # noqa

        navigation = builder_block.build_navigation(self.builder, page, request)

        result = presenter_block.render_navigation(self.presenter, navigation, render_location, request, context)
        return result

    panels = [

        MultiFieldPanel([

            FieldPanel('identifier'),
            FieldPanel('name'),

        ], "Description"),

        FieldPanel('builder'),
        FieldPanel('presenter')
    ]


def navigation_style_choices():
    return [(style.identifier, style.name) for style in NavigationStyle.objects.all()]


@register_snippet
class NavigationStyleAlias(django_models.Model):

    class Meta:
        verbose_name = "Navigation Alias"
        verbose_name_plural = "Navigation Aliases"

        constraints = [
            django_models.UniqueConstraint(fields=['identifier'], name='unique_%(app_label)s_%(class)s.identifier')
        ]

    identifier = django_models.CharField(max_length=128, default='', validators=[python_identifier_validator])
    style = django_models.ForeignKey('NavigationStyle', related_name="aliases", on_delete=django_models.SET_NULL,
                                     blank=True, null=True)

    panels = [
        FieldRowPanel([
            FieldPanel('identifier'),
            FieldPanel('style')
        ])
    ]

    def __str__(self):
        return "{} -> {}".format(self.identifier, self.style.name if self.style else "[undefined]")


def lookup_navigation_style(identifier):

    navigation_style = None

    try:
        alias = NavigationStyleAlias.objects.get(identifier=identifier)
        navigation_style = alias.style

    except NavigationStyleAlias.DoesNotExist:
        pass

    if navigation_style is None:
        try:
            navigation_style = NavigationStyle.objects.get(identifier=identifier)
        except NavigationStyle.DoesNotExist:
            pass

    return navigation_style


@register_snippet
class AnchorCategorySetting(django_models.Model):

    class Meta:
        verbose_name = 'Anchor Category'
        verbose_name_plural = 'Anchor Categories'
        constraints = [
            django_models.UniqueConstraint(fields=['identifier'], name='unique_%(app_label)s_%(class)s.identifier'),
            django_models.UniqueConstraint(fields=['name'], name='unique_%(app_label)s_%(class)s.name')
        ]

    name = django_models.CharField(max_length=128, unique=True, blank=False, null=False)
    identifier = django_models.CharField(max_length=128, unique=True, blank=False, null=False, validators=[validate_identifier])
    label = django_models.CharField(max_length=128, blank=True, default='Figure')
    label_plural = django_models.CharField(max_length=128, blank=True, default='Figures')
    label_short = django_models.CharField(max_length=128, blank=True, default='Fig')

    link_css_class = django_models.CharField(max_length=128, blank=True, default='')
    label_css_class = django_models.CharField(max_length=128, blank=True, default='')

    number_format = DynamicChoiceField(max_length=128,
                                       choices_function_name=APP_LABEL + ".anchors.number_format_choices",
                                       default='numbers')

    identifier_format = DynamicChoiceField(max_length=128,
                                           choices_function_name=APP_LABEL + ".anchors.identifier_format_choices",
                                           default='generic')

    panels = [
        FieldPanel('name'),
        FieldPanel('identifier'),
        FieldPanel('label'),
        FieldPanel('label_plural'),
        FieldPanel('label_short'),
        FieldPanel('link_css_class'),
        FieldPanel('label_css_class'),
        FieldPanel('number_format'),
        FieldPanel('identifier_format')
    ]

    def __str__(self):

        number_format = [number_format for identifier, number_format in number_format_choices()
                         if identifier == self.number_format]

        if not number_format:
            number_format = 'none'
        else:
            number_format = number_format[0]
            number_format = number_format.format(singular=self.label, plural=self.label_plural)

        result = self.name + "/" + self.identifier + ": " + number_format # noqa
        return result

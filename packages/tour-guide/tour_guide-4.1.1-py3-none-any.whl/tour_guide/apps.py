# -*- coding: utf-8 -*-

import sys
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS
from django.apps import AppConfig
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def is_running_without_database():
    engine = settings.DATABASES[DEFAULT_DB_ALIAS]['ENGINE']
    return engine == 'django.db.backends.dummy'


class TourGuideConfig(AppConfig):
    name = 'tour_guide'
    label = 'tour_guide'
    verbose_name = _("Tour Guide")
    default_auto_field = 'django.db.models.BigAutoField'

    def import_models(self):

        from django_auxiliaries.variable_scope import register_variable_scope, Copy, EnvironmentVariable
        from .anchors import cast_to_anchor_registry

        register_variable_scope(self.label,
                                navigation_index=0,
                                anchor_inventory=Copy({}),
                                anchor_registry=EnvironmentVariable('page', None, copy_default=False,
                                                                    modifier=cast_to_anchor_registry))

        super().import_models()

    def ready(self):

        if is_running_without_database() or "makemigrations" in sys.argv or "migrate" in sys.argv:
            return


def get_app_label():
    return TourGuideConfig.label


def reverse_app_url(identifier):
    return reverse(f'{TourGuideConfig.label}:{identifier}')


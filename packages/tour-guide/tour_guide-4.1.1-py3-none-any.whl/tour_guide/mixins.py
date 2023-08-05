# -*- coding: utf-8 -*-

import logging
import os

from django.db.models import DEFERRED
from django.core.files.storage import default_storage as DEFAULT_STORAGE # noqa
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from django.contrib.contenttypes.models import ContentType

from PIL import Image as PILImage

from .apps import get_app_label

__all__ = ['ChangeScope', 'ChangeScopeMixin']


APP_LABEL = get_app_label()


class ChangeScope(object):

    def __init__(self, navigation_style):
        self.navigation_style = navigation_style

    def __enter__(self):

        self.navigation_style.change_level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.navigation_style.change_level -= 1

        if self.navigation_style.change_count != 0 and self.navigation_style.change_level == 0:
            self.navigation_style.change_count = 0
            self.navigation_style.assemble()


class ChangeScopeMixin:

    class Meta:
        abstract = True

    @property
    def change_level(self):
        return self.change_level_

    @change_level.setter
    def change_level(self, value):
        self.change_level_ = value

    @property
    def change_count(self):
        return self.change_count_

    @change_count.setter
    def change_count(self, value):
        self.change_count_ = value

    @property
    def change_scope(self):
        return ChangeScope(self)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.change_level_ = 0
        self.change_count_ = 0

    def did_change(self):

        if self.change_level_ == 0:
            self.change_count_ = 0
            self.assemble()
        else:
            self.change_count_ += 1

    def assemble(self):
        pass


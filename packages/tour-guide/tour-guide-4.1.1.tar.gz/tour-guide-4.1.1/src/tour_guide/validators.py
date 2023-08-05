import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

__all__ = ['validate_identifier']


def validate_identifier(value):

    if re.search(r"(^[^A-Za-z0-9_]|\s)", value):

        raise ValidationError(
            _("Identifiers must start with a letter, a digit or underscore and cannot contain whitespace characters: {:}").format(value)
        )

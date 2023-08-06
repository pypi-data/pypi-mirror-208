from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_capitalized(value):
    if not value[0].isupper():
        err_msg = _("%(value)s should start with an uppercase letter")
        raise ValidationError(err_msg, params={"value": value})


def validate_and_vs_ampersand(value):
    if "&" in value:
        err_msg = _("%(value)s should use 'and' instead of '&'")
        raise ValidationError(err_msg, params={"value": value})

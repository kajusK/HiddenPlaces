"""Helper utilities and decorators."""

import re

from flask import flash
from flask_babel import _
from wtforms import ValidationError


#def flash_errors(form, category="danger"):
#    """Flash all errors for a form."""
#    for field, errors in form.errors.items():
#        for error in errors:
#            flash(error, category)


def password_rules(length=6, upper=1, lower=None, numeric=1, special=None,
                   message=None):
    """ Password rules validator """
    if not message:
        message = _(f"Password must have at least {length} characters")
        rules = []
        if lower:
            rules.append(_(f"{lower} small letters"))
        if upper:
            rules.append(_(f"{upper} capital letters"))
        if numeric:
            rules.append(_(f"{numeric} numbers"))
        if special:
            rules.append(_(f"{special} special characters"))

        if len(rules):
            message += " and " + " and ".join(rules)

    def _password_rules(form, field):
        count_upper = len(re.findall(r'[A-Z]', field.data))
        count_lower = len(re.findall(r'[a-z]', field.data))
        count_numeric = len(re.findall(r'[0-9]', field.data))
        count_special = len(re.findall(r'[^0-9A-Za-z]', field.data))
        if upper and count_upper < upper:
            raise ValidationError(message)
        if lower and count_lower < lower:
            raise ValidationError(message)
        if numeric and count_numeric < numeric:
            raise ValidationError(message)
        if special and count_special < special:
            raise ValidationError(message)

    return _password_rules


# todo - custom decorators - admin_required.... custom routes override @public and @private, private replaces login required and route
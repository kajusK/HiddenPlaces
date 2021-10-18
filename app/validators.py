"""Custom validator functions for wtforms."""
import re
import os
from flask import current_app as app
from typing import Optional, Callable, Any
from flask_babel import _
from wtforms import ValidationError


def image_file(message: Optional[str] = None) -> Callable[[Any, Any], None]:
    """Generates validation function for image files.

    Args:
        message : Message to set in the ValidationError exception.

    Returns:
        A function to be used as a validator in wtforms.

    Raises:
        ValidationError: If the image doesn't have expected extension
    """
    if not message:
        message = _("Not a supported image format")

    def _image_file(form, field):
        if not field.data:
            return

        extension = os.path.splitext(field.data.filename)[1][1:].lower()
        if extension not in app.config['IMAGE_EXTENSIONS']:
            raise ValidationError(message)

    return _image_file


def password_rules(length: int = 6,
                   upper: Optional[int] = 1,
                   lower: Optional[int] = None,
                   numeric: Optional[int] = 1,
                   special: Optional[int] = None,
                   message: Optional[str] = None) -> Callable[[Any, Any],
                                                              None]:
    """Generates validation function for password format.

    Args:
        length: Minimum length of the password.
        upper: Minimum amount of uppercase characters.
        lower: Minimum amount of lowercase characters.
        numeric: Minimum amount of numberic characters.
        special : Minimum amount of special characters
            (ones not matching previous types).
        message : Message to set in the ValidationError exception.

    Returns
    -------
        A function to be used as a validator in wtforms.

    Raises
    ------
    ValidationError
        If the password being validated doesn't match the rules.
    """
    # pylint: disable=unused-argument,too-many-arguments

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

        if rules:
            message += _(" and ") + _(" and ").join(rules)

    def _password_rules(form, field):
        count_upper = len(re.findall(r'[A-Z]', field.data))
        count_lower = len(re.findall(r'[a-z]', field.data))
        count_numeric = len(re.findall(r'[0-9]', field.data))
        count_special = len(re.findall(r'[^0-9A-Za-z]', field.data))
        if len(field.data) < length:
            raise ValidationError(message)
        if upper and count_upper < upper:
            raise ValidationError(message)
        if lower and count_lower < lower:
            raise ValidationError(message)
        if numeric and count_numeric < numeric:
            raise ValidationError(message)
        if special and count_special < special:
            raise ValidationError(message)

    return _password_rules

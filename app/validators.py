"""Custom validator functions for wtforms."""
import re
import os
from datetime import datetime
from typing import Optional, Callable, Any
from flask import current_app as app
from flask_babel import _
from wtforms import ValidationError

from app.utils import LatLon


def _validate_extension(field, allowed=None, not_allowed=None,
                        message: Optional[str] = None):
    """Validates file field uploaded extension

    Supports single and multiple files selection.

    Args:
        field: Field to be validated
        allowed: List of allowed extensions, cannot be set if not_allowed used
        non_allowed: List of not allowed extensions
        message : Message to set in the ValidationError exception.

    Raises:
        ValidationError: If the file doesn't have expected extension
    """
    if not message:
        message = _("Not an allowed file format")

    if not field.data:
        return

    data = field.data
    if not isinstance(field.data, list):
        data = [field.data]

    for item in data:
        extension = os.path.splitext(item.filename)[1][1:].lower()
        if allowed and extension not in allowed:
            raise ValidationError(message)
        if not_allowed and extension in not_allowed:
            raise ValidationError(message)


def image_file(message: Optional[str] = None) -> Callable[[Any, Any], None]:
    """Generates validation function for uploaded image files.

    Args:
        message : Message to set in the ValidationError exception.
    """
    if not message:
        message = _("Not a supported image type")

    def _image_file(form, field):
        # pylint: disable=unused-argument
        _validate_extension(field, allowed=app.config['IMAGE_EXTENSIONS'],
                            message=message)

    return _image_file


def allowed_file(message: Optional[str] = None) -> Callable[[Any, Any], None]:
    """Generates validation function for uploaded files.

    Args:
        message : Message to set in the ValidationError exception.
    """
    if not message:
        message = _("Files of this type are not allowed")

    def _allowed_file(form, field):
        # pylint: disable=unused-argument
        _validate_extension(field,
                            not_allowed=app.config['DISABLED_EXTENSIONS'],
                            message=message)
    return _allowed_file


def latitude(message: Optional[str] = None) -> Callable[[Any, Any], None]:
    """Generates validation function for latitude string

    Args:
        message : Message to set in the ValidationError exception.
    """
    if not message:
        message = _("Invalid latitude format")

    def _latitude(form, field):
        # pylint: disable=unused-argument
        try:
            field.data = LatLon.from_str(field.data)
        except ValueError as e:
            raise ValidationError(message) from e
        if not field.data.is_latitude:
            raise ValidationError(message)
    return _latitude


def longitude(message: Optional[str] = None) -> Callable[[Any, Any], None]:
    """Generates validation function for longitude string

    Args:
        message : Message to set in the ValidationError exception.
    """
    if not message:
        message = _("Invalid longitude format")

    def _longitude(form, field):
        # pylint: disable=unused-argument
        try:
            field.data = LatLon.from_str(field.data)
        except ValueError as e:
            raise ValidationError(message) from e
        if not field.data.is_longitude:
            raise ValidationError(message)
    return _longitude


def date_in_past(message: Optional[str] = None) -> Callable[[Any, Any], None]:
    """Generates validation function to check the date field is in past

    Args:
        message : Message to set in the ValidationError exception.
    """
    if not message:
        message = _("Date cannot be in the future")

    def _date_in_past(form, field):
        # pylint: disable=unused-argument
        if field.data > datetime.utcnow().date():
            raise ValidationError(message)
    return _date_in_past


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

"""Custom decorators for flask routes."""
from functools import wraps
from flask import abort
from flask_login import current_user
from flask_babel import _

from app.user.constants import UserRole


def public(function):
    """Marks the route as public (doesn't require login)."""
    function.is_public = True
    return function


def admin(function):
    """Allows only users with admin role to access this route."""
    @wraps(function)
    def _admin(*args, **kwargs):
        if current_user.role.value > UserRole.ADMIN.value:
            return abort(503,
                         _("You don't have sufficient access permissions"))
        return function(*args, **kwargs)
    return _admin


def moderator(function):
    """Allows only users with moderator or admin role to access this route."""
    @wraps(function)
    def _moderator(*args, **kwargs):
        """Allows only users with admin role to access this route."""
        if current_user.role.value > UserRole.MODERATOR.value:
            return abort(503,
                         _("You don't have sufficient access permissions"))
        return function(*args, **kwargs)
    return _moderator

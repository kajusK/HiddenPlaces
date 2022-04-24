"""Custom decorators for flask routes."""
from functools import wraps
from flask import abort
from flask_login import current_user
from app.models.user import UserRole


def public(function):
    """Marks the route as public (doesn't require login)."""
    function.is_public = True
    return function


def admin(function):
    """Allows only users with admin role to access this route."""
    function.auth_admin = True

    @wraps(function)
    def _admin(*args, **kwargs):
        if current_user.role > UserRole.ADMIN:
            abort(403)
        return function(*args, **kwargs)

    return _admin


def moderator(function):
    """Allows only users with moderator or admin role to access this route."""
    function.auth_moderator = True

    @wraps(function)
    def _moderator(*args, **kwargs):
        """Allows only users with admin role to access this route."""
        if current_user.role > UserRole.MODERATOR:
            abort(403)
        return function(*args, **kwargs)

    return _moderator

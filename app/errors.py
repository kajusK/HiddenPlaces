""" Flask error handlers."""
from flask import render_template, request
from flask import current_app as app
from flask_login import current_user

from app.database import db
from app.admin.models import EventLog
from app.admin.events import UnauthorizedEvent


def error_403(e: Exception):
    """Shows error page for user with insufficient priviledges.

    Args:
        error: An error string
    Returns:
        A page content and error code.
    """
    app.logger.error(f'403: {request.path} by {current_user.email}: %s', e)
    EventLog.log(current_user, UnauthorizedEvent(request.path))
    db.session.commit()
    return render_template('403.html'), 403


def error_404(e: Exception):
    """Shows error page for Not found error.

    Args:
        error: An error string
    Returns:
        A page content and error code.
    """
    app.logger.error(f'404: {request.path}: %s', e)
    return render_template('404.html'), 404


def error_500(e: Exception):
    """Shows error page for Internal server error.

    Args:
        error: An error string.
    Returns:
        A page content and error code.
    """
    app.logger.error('Server Error: %s', e)
    return render_template('500.html'), 500


def unhandled_exception(e: Exception):
    """Shows error page ro Unhandled exception.

    Args:
        e: An exception that was raised.
    Returns:
        A page content and error code.
    """
    app.logger.exception('Unhandled Exception: %s', e)
    return render_template('500.html'), 500

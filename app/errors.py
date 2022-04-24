""" Flask error handlers."""
from flask import render_template, request
from flask import current_app as app
from flask_login import current_user

from app.database import db
from app.models.event import EventLog, UnauthorizedEvent


def error_403(error: Exception):
    """Shows error page for user with insufficient priviledges.

    Args:
        error: An exception that was raised.
    Returns:
        A page content and error code.
    """
    app.logger.error(f'403: {request.path} by {current_user.email}:'
                     f'{str(error)}')
    EventLog.log(current_user, UnauthorizedEvent(request.path))
    db.session.commit()
    return render_template('403.html'), 403


def error_404(error: Exception):
    """Shows error page for Not found error.

    Args:
        error: An exception that was raised.
    Returns:
        A page content and error code.
    """
    app.logger.error(f'404: {request.path}: {str(error)}')
    return render_template('404.html'), 404


def error_500(error: Exception):
    """Shows error page for Internal server error.

    Args:
        error: An exception that was raised.
    Returns:
        A page content and error code.
    """
    app.logger.error(f'500: {request.path}: {str(error)}')
    return render_template('500.html'), 500


def unhandled_exception(error: Exception):
    """Shows error page for Unhandled exception.

    Args:
        error: An exception that was raised.
    Returns:
        A page content and error code.
    """
    app.logger.exception(f'Unhandled Exception: {request.path}: {str(error)}')
    return render_template('500.html'), 500

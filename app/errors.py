from flask import render_template, request
from flask import current_app as app


def error_404(error):
    app.logger.error(f'404: {request.path}')
    return render_template('404.html'), 404


def error_500(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('500.html'), 500


def unhandled_exception(e):
    app.logger.error(f'Unhandled Exception: {e}')
    return render_template('500.html'), 500

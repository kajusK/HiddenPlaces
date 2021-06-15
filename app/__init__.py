import logging
from flask import Flask, request, redirect, url_for, flash
from app.extensions import db, login_manager, bcrypt, babel
from app import errors, user, public
from app.user.models import User
from flask import current_app as app


def create_app(config_object='app.settings', config_override={}):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    for key, value in config_override.items():
        app.config[key] = value

    # Configure logging
    handler = logging.FileHandler(app.config['LOGGING_LOCATION'])
    handler.setLevel(app.config['LOGGING_LEVEL'])
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    babel.init_app(app)

    # register routes
    app.register_blueprint(user.routes.blueprint)
    app.register_blueprint(public.routes.blueprint)

    # register error handlers
    app.register_error_handler(404, errors.error_404)
    app.register_error_handler(500, errors.error_500)
    app.register_error_handler(Exception, errors.unhandled_exception)

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    flash("Not authorized to access this page, please log-in")
    return redirect(url_for('user.login', next=request.path))


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(
        app.config['SUPPORTED_LANGUAGES'].keys())


@babel.timezoneselector
def get_timezone():
    # TODO get timezone from user settings
    return None
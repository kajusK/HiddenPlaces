"""Initialize the Flask web application."""
import logging
from typing import Dict, Any, Optional
from flask import Flask, request, redirect, url_for, flash, current_app,\
    session, g
from flask_login import current_user

import app.user.routes as user
import app.location.routes as location
import app.admin.routes as admin
import app.page.routes as page
import app.message.routes as message
import app.upload.routes as upload
from app import errors
from app.commands import user_cli, translate_cli
from app.utils.utils import Url
from app.user.models import User, Invitation, LoginLog
from app.user.constants import InvitationState
from app.location.models import Bookmarks, Location
from app.admin.models import EventLog
from app.message.models import Thread
from app.extensions import db, migrate, login_manager, bcrypt, babel, misaka,\
    mail, moment


def create_app(config_object: str = 'app.config.Config') -> Flask:
    """Flask application factory.

    Initializes flask appliacation and return it.
    Args:
        config_object: Path to application settings.
        config_override: Overwrite specific config items.
    Returns:
        Initialized Flask application object
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Configure logging
    handler = logging.FileHandler(app.config['LOGGING_LOCATION'])
    handler.setLevel(app.config['LOGGING_LEVEL'])
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    babel.init_app(app)
    misaka.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # register routes
    app.register_blueprint(user.blueprint)
    app.register_blueprint(location.blueprint)
    app.register_blueprint(upload.blueprint)
    app.register_blueprint(admin.blueprint)
    app.register_blueprint(page.blueprint)
    app.register_blueprint(message.blueprint)

    # register error handlers
    app.register_error_handler(403, errors.error_403)
    app.register_error_handler(404, errors.error_404)
    app.register_error_handler(500, errors.error_500)
    if not app.config['DEBUG']:
        app.register_error_handler(Exception, errors.unhandled_exception)

    # register custom flask commands
    app.cli.add_command(user_cli)
    app.cli.add_command(translate_cli)

    # modify jinja2 environment
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    # Disable caching limit, improves performance
    app.jinja_env.cache = {}
    # add jinja2 global variables and functions
    register_template_context(app)

    # register functions to be called before each request
    register_before_requests(app)

    return app


def register_template_context(app: Flask) -> None:
    """Registers additional global Jinja2 functions and variables."""
    @app.context_processor
    def jinja_endpoints():
        """Registers endpoints relation helpers."""
        return dict(Url=Url)

    @app.context_processor
    def jinja_user_bookmarks():
        """Registers list of user bookmarks."""
        bookmarks = []
        if current_user.is_authenticated:
            bookmarks = Bookmarks.get_by_user(current_user).all()
        return dict(user_bookmarks=bookmarks)

    @app.context_processor
    def jinja_alerts_count():
        """Registers count of various alerts events."""
        msg = 0
        invite = 0
        loc = 0
        login = 0
        event = 0
        if current_user.is_authenticated:
            msg = Thread.get_unreaded(current_user).count()
            invite = Invitation.get_by_state(InvitationState.WAITING).count()
            loc = Location.get_since(
                current_user.location_check_ts).count()
            login = LoginLog.get_since(current_user.login_check_ts).count()
            event = EventLog.get_since(current_user.event_check_ts).count()
        return dict(msg_alerts=msg, invite_alerts=invite,
                    location_alerts=loc, login_alerts=login,
                    event_alerts=event)


def register_before_requests(app: Flask) -> None:
    """Sets before request callback

    Args:
        app: Flask application object to register callbacks to
    """

    def is_public() -> bool:
        """Checks if the endpoint accesses is publicly accessible."""
        public = request.endpoint and getattr(
            app.view_functions[request.endpoint], 'is_public', False)
        static = request.path.startswith('/static/')
        return public or static

    @app.before_request
    def require_login_everywhere():
        """Requires user to be logged in

        Require logged-in user to access every endpoint with exception of
        static files and pages explicitly marked as public
        """
        if is_public() or current_user.is_authenticated:
            return None
        return unauthorized()

    @app.before_request
    def update_last_seen() -> None:
        """Updates last seen field of currently logged in user

        Keeps track of user actions on the page - stores last user access
        """
        if not is_public() and current_user.is_authenticated:
            current_user.update_last_seen()
            db.session.commit()

    @app.before_request
    def set_locale() -> None:
        """Sets current locale for usage from templates/javascript."""
        g.locale = str(get_locale())


@login_manager.user_loader
def load_user(user_id: int):
    """Loads current user from database

    Used by flask login manager to obtain current user information

    Args:
        user_id: ID of the user to fetch data for.
    Returns:
        User object or None if not found
    """
    return User.get_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    """Handles unauthorized access (user not logged in)."""
    flash("Not authorized to access this page, please log-in", "danger")
    return redirect(url_for('user.login', next=request.path))


@babel.localeselector
def get_locale() -> Optional[str]:
    """Chooses a locale for babel package from client's accept language."""
    return request.accept_languages.best_match(
        current_app.config['SUPPORTED_LANGUAGES'].keys())


@babel.timezoneselector
def get_timezone():
    """Selects timezone for babel package."""
    # TODO get timezone from user settings
    return None

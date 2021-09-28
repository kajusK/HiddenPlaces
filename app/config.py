"""Default application configuration

User specific configuration is done via environment variables, this file
contains all the default configuration options. If you need multiple
configurations, create subclasses of the default config class and pass it
as a parameter to application factory.
"""
import logging
import os


class Config:
    """Default app configuration.

    To create a custom configuration, take this class as a parent and pass
    the new class to app factory. Most important variables are taken
    from environmental variables, these can be e.g. kept in .env file.
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'sqlite:///db.sqlite')

    # Used as seed for signatures, tokens and csrf key generators
    # It's best to generate a longer random string for this
    # KEEP IT SECRET!
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key')

    # Show a SQL commands while in development mode
    SQLALCHEMY_ECHO = os.environ.get('FLASK_ENV') == 'development'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOGGING_FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
    LOGGING_LOCATION = 'app.log'
    LOGGING_LEVEL = logging.INFO

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'cs': 'Čeština'
    }
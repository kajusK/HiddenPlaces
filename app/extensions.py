""" Flask extensions initialization code. """
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_babel import Babel
from flask_misaka import Misaka
from flask_mail import Mail


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
babel = Babel()
# markdown parser
misaka = Misaka()
mail = Mail()

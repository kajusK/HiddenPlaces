"""Modes for user module."""
import hashlib
from typing import Optional
from datetime import datetime
from flask import request
from flask_login import UserMixin

from app.database import DBItem, db
from app.extensions import bcrypt
from app.utils import GeoIp, get_visitor_ip, random_string
from app.user.constants import LoginResult, MAX_FIRST_NAME_LEN, \
    MAX_LAST_NAME_LEN, MAX_EMAIL_LEN, MAX_ABOUT_LEN, MAX_REASON_LEN
from app.user.constants import UserRole, InvitationState


class User(DBItem, UserMixin):
    """User description and handling."""
    password = db.Column(db.LargeBinary(128), nullable=False)
    first_name = db.Column(db.String(MAX_FIRST_NAME_LEN), nullable=False)
    last_name = db.Column(db.String(MAX_LAST_NAME_LEN), nullable=False)
    email = db.Column(db.String(MAX_EMAIL_LEN), index=True, unique=True,
                      nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    active = db.Column(db.Boolean(), default=True)
    about = db.Column(db.String(MAX_ABOUT_LEN), default="")
    role = db.Column(db.Enum(UserRole), default=UserRole.NEWBIE)

    def __init__(self, password: str = None, **kwargs):
        """Initializes the User object

        If the password is set in here, it will hash it before storing
        """
        super().__init__(**kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password: str) -> None:
        """Hashes the plaintext password

        Args:
            password: Plaintext password to be hashed
        """
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks if the password matches the stored hash.

        Args:
            password: Plaintext password to be checked
        """
        return bool(bcrypt.check_password_hash(self.password, password))

    def update_last_seen(self) -> None:
        """Updates last seen record to current time. """
        self.last_seen = datetime.utcnow()

    def is_banned(self) -> bool:
        """Checks if the user is currently banned."""
        # TODO - handle ban timed out and change the active flag
        # Also force user to be logged out when banned
        return not self.active

    def get_ban(self):
        """Gets latest ban entry if any"""
        return Ban.query.filter_by(user=self).order_by(
            db.desc(Ban.until)).first()


class Ban(DBItem):
    """Ban record model"""
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship("User", foreign_keys=creator_id)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", foreign_keys=user_id)
    reason = db.Column(db.String(MAX_REASON_LEN), nullable=False)
    until = db.Column(db.DateTime(), nullable=False)
    permanent = db.Column(db.Boolean(), default=False)


class Invitation(DBItem):
    """New user invitation model."""
    email = db.Column(db.String(MAX_EMAIL_LEN), nullable=False)
    name = db.Column(db.String(MAX_FIRST_NAME_LEN+MAX_LAST_NAME_LEN+1),
                     nullable=False)
    # code required in the register request
    key = db.Column(db.String(32), nullable=False, index=True)

    reason = db.Column(db.String(MAX_REASON_LEN), nullable=False)
    created = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime(), nullable=False)
    state = db.Column(db.Enum(InvitationState), nullable=False,
                      default=InvitationState.WAITING)

    invited_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                              nullable=False)
    approved_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    invited_by = db.relationship("User", foreign_keys=invited_by_id)
    approved_by = db.relationship("User", foreign_keys=approved_by_id)
    user = db.relationship("User", foreign_keys=user_id)

    def __init__(self, **kwargs) -> None:
        """Initializes the Invitation model.

        If hash is not set and name and email are present, calculate the key
        """
        super().__init__(**kwargs)
        if 'key' not in kwargs:
            self.key = hashlib.md5(random_string(32).encode()).hexdigest()

    def is_valid(self) -> bool:
        """Checks if the invitation is approved and valid for registration. """
        if self.state != InvitationState.APPROVED:
            return False
        if datetime.utcnow() > self.valid_until:
            return False
        if self.user:
            return False
        return True


class LoginLog(DBItem):
    """Table for login attempts logging."""
    email = db.Column(db.String(MAX_EMAIL_LEN), nullable=False)
    result = db.Column(db.Enum(LoginResult), nullable=False, index=True)
    ip = db.Column(db.String(46), nullable=False)
    # In case of success, also logs user that logged in
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    system = db.Column(db.String(64))
    browser = db.Column(db.String(64))
    country = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)

    @classmethod
    def create_log(cls, email: str, result: LoginResult,
                   user: Optional[User] = None):
        """Create a new login attempt entry

        Args:
            email: Email used for login attempt
            result: Resulting of the login operation
            user: Use that was logged in (if succeeded)
        """
        # pylint: disable=too-many-function-args
        user_id = user.id if user else None
        ip = get_visitor_ip()
        country = GeoIp(ip).country if ip else None
        os = request.user_agent.platform
        browser = request.user_agent.browser
        if browser is not None and request.user_agent.version is not None:
            browser += ' ' + request.user_agent.version

        return cls.create(
            email=email,
            result=result,
            ip=ip,
            user_id=user_id,
            system=os,
            browser=browser,
            country=country)

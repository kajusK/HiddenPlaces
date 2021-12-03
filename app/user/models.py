"""Modes for user module."""
from typing import Optional
from time import time
from datetime import datetime, timedelta
import jwt
from sqlalchemy import or_
from sqlalchemy.orm import Query, backref
from flask import request, current_app as app
from flask_login import UserMixin

from app.database import DBItem, db
from app.extensions import bcrypt
from app.utils.geolocation import GeoIp
from app.utils.utils import get_visitor_ip
from app.user import constants
from app.user.constants import LoginResult, UserRole, InvitationState


class User(DBItem, UserMixin):
    """User description and handling."""
    password = db.Column(db.LargeBinary(128), nullable=False)
    first_name = db.Column(db.String(constants.MAX_FIRST_NAME_LEN),
                           nullable=False)
    last_name = db.Column(db.String(constants.MAX_LAST_NAME_LEN),
                          nullable=False)
    email = db.Column(db.String(constants.MAX_EMAIL_LEN), index=True,
                      unique=True, nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    about = db.Column(db.String(constants.MAX_ABOUT_LEN), default='')
    photo_path = db.Column(db.String(64))
    role = db.Column(db.Enum(UserRole), default=UserRole.NEWBIE,
                     nullable=False)

    # Time when the corresponding table was last checked
    event_check_ts = db.Column(db.DateTime(), default=datetime.utcnow,
                               nullable=False)
    location_check_ts = db.Column(db.DateTime(), default=datetime.utcnow,
                                  nullable=False)
    login_check_ts = db.Column(db.DateTime(), default=datetime.utcnow,
                               nullable=False)

    @classmethod
    def get(cls) -> Query:
        """Gets all users query ordered by created date"""
        return cls.query.order_by(cls.created.desc())

    @classmethod
    def get_admins(cls) -> Query:
        """Gets admin users query."""
        return cls.get().filter(or_(
            cls.role == UserRole.ADMIN, cls.role == UserRole.ROOT))

    @classmethod
    def get_moderators(cls) -> Query:
        """Gets moderator users query."""
        return cls.get().filter_by(role=UserRole.MODERATOR)

    @classmethod
    def get_banned(cls) -> Query:
        """Gets banned users."""
        return cls.get().join(Ban, (cls.id == Ban.user_id)).filter(
            Ban.until > datetime.utcnow())

    @classmethod
    def get_by_email(cls, email: str):
        """Gets user by email address.

        Args:
            email: Email of the user
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def check_reset_token(cls, token: str):
        """Checks if the reset password token is valid

        Args:
            token: JWT reset password token
        Returns:
            User: Corresponding user which requested the password reset
            None: Token is invalid
        """
        try:
            user_id = jwt.decode(token, app.config['SECRET_KEY'],
                                 algorithms=['HS256'])['user_id']
        except (KeyError, jwt.exceptions.InvalidTokenError):
            return None

        user = cls.get_by_id(user_id)
        if not user:
            return None
        return user

    @property
    def banned(self) -> bool:
        """Checks if the user is currently banned."""
        return self.get_ban() is not None

    def __init__(self, *args, password: str = None, **kwargs):
        """Initializes the User object

        If the password is set in here, it will be hashed it before storing
        """
        super().__init__(*args, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

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

    def get_ban(self):
        """Gets active ban entry if any"""
        return Ban.query.filter_by(user=self).filter(
            Ban.until > datetime.utcnow()).order_by(Ban.until.desc()).first()

    def get_reset_token(self, expire_minutes: int = 60) -> str:
        """Generates url token for password_reset

        Args:
            expire_minutes: Amount of minutes in which the token expires
        """
        return jwt.encode(
            {'user_id': self.id, 'exp': time() + expire_minutes*60},
            app.config['SECRET_KEY'], algorithm='HS256')


class Ban(DBItem):
    """Ban record model"""
    reason = db.Column(db.String(constants.MAX_REASON_LEN), nullable=False)
    until = db.Column(db.DateTime(), nullable=False)
    permanent = db.Column(db.Boolean(), default=False, nullable=False)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                           nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)

    creator = db.relationship('User', foreign_keys=creator_id)
    user = db.relationship('User', foreign_keys=user_id)


class Invitation(DBItem):
    """New user invitation model."""
    email = db.Column(db.String(constants.MAX_EMAIL_LEN), nullable=False)
    name = db.Column(db.String(constants.MAX_FIRST_NAME_LEN +
                               constants.MAX_LAST_NAME_LEN+1),
                     nullable=False)

    reason = db.Column(db.String(constants.MAX_REASON_LEN), nullable=False)
    created = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    state = db.Column(db.Enum(InvitationState), nullable=False,
                      default=InvitationState.WAITING)

    invited_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                              nullable=False)
    approved_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    invited_by = db.relationship('User', foreign_keys=invited_by_id,
                                 backref='invited')
    approved_by = db.relationship('User', foreign_keys=approved_by_id)
    user = db.relationship('User', foreign_keys=user_id,
                           backref=backref('invitation', uselist=False))

    @classmethod
    def get(cls) -> Query:
        """Gets the Invitations query ordered by created date."""
        return cls.query.order_by(cls.created.desc())

    @classmethod
    def get_by_state(cls, state: InvitationState) -> Query:
        """Gets the Invitations query by the state.

        Args:
            state: State to filter for
        """
        return cls.get().filter_by(state=state)

    @classmethod
    def get_by_email(cls, email: str):
        """Gets invitation by invite email.

        Args:
            email: Email show in invitation
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def check_token(cls, token: str):
        """Checks if the token matches valid invitation

        Args:
            token: JWT invitation token tied to this invitation
        Returns:
            Invitation: Corresponding invitation
            None: Token is invalid
        """
        try:
            invite_id = jwt.decode(token, app.config['SECRET_KEY'],
                                   algorithms=['HS256'])['invite_id']
        except (KeyError, jwt.exceptions.InvalidTokenError):
            return None

        invitation = cls.get_by_id(invite_id)
        if not invitation:
            return None

        if invitation.state != InvitationState.APPROVED or invitation.user:
            return None
        return invitation

    def get_token(self, expire_days: int = 30) -> str:
        """Generates url token for invitation link.

        Args:
            expire_days: Amount of days in which the token expires
        """
        return jwt.encode(
            {'invite_id': self.id, 'exp': time() + expire_days*24*3600},
            app.config['SECRET_KEY'], algorithm='HS256')


class LoginLog(DBItem):
    """Table for login attempts logging."""
    email = db.Column(db.String(constants.MAX_EMAIL_LEN), nullable=False)
    result = db.Column(db.Enum(LoginResult), nullable=False, index=True)
    ip = db.Column(db.String(46), nullable=False)
    # In case of success, also logs user that logged in
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    system = db.Column(db.String(64))
    browser = db.Column(db.String(64))
    country = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow,
                          nullable=False)

    @classmethod
    def get(cls) -> Query:
        """Gets the Login logs query ordere by timestamp."""
        return cls.query.order_by(cls.timestamp.desc())

    @classmethod
    def get_failed(cls) -> Query:
        """Gets failed login attempts."""
        return cls.get().filter(cls.result != LoginResult.SUCCESS)

    @classmethod
    def get_unique(cls) -> Query:
        """Gets unique IP login attempts."""
        return cls.get().distinct(cls.ip)

    @classmethod
    def get_last_day(cls) -> Query:
        """Get attempts from last 24 hours."""
        return cls.get().filter(
            cls.timestamp >= datetime.utcnow() - timedelta(days=1))

    @classmethod
    def get_last_month(cls) -> Query:
        """Get attempts from last 30 days."""
        return cls.get().filter(
            cls.timestamp >= datetime.utcnow() - timedelta(days=30))

    @classmethod
    def get_since(cls, since: datetime) -> Query:
        """Query logs added since date

        Args:
            since: Start date to filter from
        """
        return cls.get().filter(cls.timestamp > since)

    @classmethod
    def create(cls, email: str, result: LoginResult,
               user: Optional[User] = None):
        """Create a new login attempt entry

        Args:
            email: Email used for login attempt
            result: Resulting of the login operation
            user: Use that was logged in (if succeeded)
        """
        # pylint: disable=arguments-differ
        user_id = user.id if user else None
        ip = get_visitor_ip()
        country = GeoIp(ip).country if ip else None
        os = request.user_agent.platform
        browser = request.user_agent.browser
        if browser is not None and request.user_agent.version is not None:
            browser += ' ' + request.user_agent.version

        return super().create(
            email=email,
            result=result,
            ip=ip,
            user_id=user_id,
            system=os,
            browser=browser,
            country=country)

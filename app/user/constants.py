""" Constants for user module. """
from enum import Enum
from app.utils import OrderedEnum

# Lengths of the various DB strings
MAX_FIRST_NAME_LEN = 20
MAX_LAST_NAME_LEN = 64
MAX_EMAIL_LEN = 128
MAX_ABOUT_LEN = 10000
MAX_REASON_LEN = 1024


class LoginResult(Enum):
    """Error codes for user tried to login event. """
    SUCCESS = 0
    NOT_ACTIVE = 1
    BANNED = 2
    INVALID_PASSWORD = 3
    INVALID_EMAIL = 4


class InvitationState(Enum):
    """State of the invitation record. """
    WAITING = 0
    APPROVED = 1
    REGISTERED = 2
    TIMED_OUT = 3
    DENIED = 4


class UserRole(OrderedEnum):
    """Available user roles. """
    ROOT = 0
    ADMIN = 1
    MODERATOR = 2
    CONTRIBUTOR = 3
    USER = 4
    NEWBIE = 5
    GUEST = 6

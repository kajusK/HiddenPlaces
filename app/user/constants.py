""" Constants for user module. """
from flask_babel import lazy_gettext as _
from app.utils.enums import StringEnum


# Lengths of the various DB strings
MAX_FIRST_NAME_LEN = 20
MAX_LAST_NAME_LEN = 64
MAX_EMAIL_LEN = 128
MAX_ABOUT_LEN = 10000
MAX_REASON_LEN = 1024


class LoginResult(StringEnum):
    """Error codes for user tried to login event. """
    SUCCESS = _("Success")
    NOT_ACTIVE = _("Not active")
    BANNED = _("Banned")
    INVALID_PASSWORD = _("Invalid password")
    INVALID_EMAIL = _("Invalid email")


class InvitationState(StringEnum):
    """State of the invitation record. """
    WAITING = _("Waiting for approval")
    APPROVED = _("Approved")
    REGISTERED = _("Registered")
    TIMED_OUT = _("Timed out")
    DENIED = _("Denied")


class UserRole(StringEnum):
    """Available user roles. """
    ROOT = _("Root")
    ADMIN = _("Admin")
    MODERATOR = _("Moderator")
    CONTRIBUTOR = _("Contributor")
    USER = _("User")
    NEWBIE = _("Newbie")

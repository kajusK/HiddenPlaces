""" Constants for user module. """
from flask_babel import _
from app.utils.enums import StringEnum


# Lengths of the various DB strings
MAX_FIRST_NAME_LEN = 20
MAX_LAST_NAME_LEN = 64
MAX_EMAIL_LEN = 128
MAX_ABOUT_LEN = 10000
MAX_REASON_LEN = 1024


class LoginResult(StringEnum):
    """Error codes for user tried to login event. """
    SUCCESS = 0, _("Success")
    NOT_ACTIVE = 1, _("Not active")
    BANNED = 2, _("Banned")
    INVALID_PASSWORD = 3, _("Invalid password")
    INVALID_EMAIL = 4, _("Invalid email")


class InvitationState(StringEnum):
    """State of the invitation record. """
    WAITING = 0, _("Waiting for approval")
    APPROVED = 1, _("Approved")
    REGISTERED = 2, _("Registered")
    TIMED_OUT = 3, _("Timed out")
    DENIED = 4,  _("Denied")


class UserRole(StringEnum):
    """Available user roles. """
    ROOT = 0, _("Root")
    ADMIN = 1, _("Admin")
    MODERATOR = 2, _("Moderator")
    CONTRIBUTOR = 3, _("Contributor")
    USER = 4, _("User")
    NEWBIE = 5, _("Newbie")

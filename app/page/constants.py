"""Constants for page module."""
from flask_babel import _

from app.utils.enums import StringEnum


class PageType(StringEnum):
    """Type of the saved location."""
    ABOUT = 1, _("About")
    RULES = 2, _("Rules")
    SUPPORT = 3, _("Support us")

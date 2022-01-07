"""Constants for page module."""
from flask_babel import lazy_gettext as _

from app.utils.enums import StringEnum


class PageType(StringEnum):
    """Type of the saved location."""
    ABOUT = _("About")
    RULES = _("Rules")
    SUPPORT = _("Support us")

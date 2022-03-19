"""Constants for locaiton module."""
from enum import Enum, auto
from flask_babel import lazy_gettext as _

from app.utils.enums import StringEnum

# DB strings lengths
MAX_NAME_LEN = 32
MAX_DESCRIPTION_LEN = 2048
MAX_SHORT_DESC_LEN = 256
MAX_URL_LEN = 256
MAX_COMMENT_LEN = 2048


class LocationType(Enum):
    """Type of the saved location."""
    UNDERGROUND = auto()
    URBEX = auto()
    HIKING = auto()
    ALL = auto()


class Country(StringEnum):
    """Countries list."""
    OTHER = _("Other")
    CZECHIA = _("Czechia")
    SLOVAKIA = _("Slovakia")
    POLAND = _("Poland")
    GERMANY = _("Germany")
    AUSTRIA = _("Austria")

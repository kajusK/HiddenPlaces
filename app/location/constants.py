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
    ALL = auto()


class Country(StringEnum):
    """Countries list."""
    OTHER = 0, _("Other")
    CZECHIA = 1, _("Czechia")
    SLOVAKIA = 2, _("Slovakia")
    POLAND = 3, _("Poland")
    GERMANY = 4, _("Germany")
    AUSTRIA = 5, _("Austria")

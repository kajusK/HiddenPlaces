"""Models for urbex locations."""
from flask_babel import lazy_gettext as _

from app.database import DBItem, db, IntEnum
from app.utils.enums import StringEnum


class UrbexType(StringEnum):
    """Urbex location type."""
    OTHER = _("Other")
    # Generic type for whole mine
    HOUSE = _("House")
    MANSION = _("Mansion")
    RECREATION = _("Recreation center")
    ARMY = _("Army object")
    FACTORY = _("Factory")
    TECHNOLOGY = _("Technology")
    CHATEAU = _("Château")


class UrbexState(StringEnum):
    """Urbex location state."""
    UNKNOWN = _("Unknown")
    LIKE_USED = _("Like being used")
    FURNISHED = _("Furnished")
    CLEANED_OUT = _("Cleaned out")
    FALLING_APART = _("Falling apart")
    DEMOLISHED = _("Demolished")
    UNDER_RESTORE = _("Under restoration")
    RESTORED = _("Restored")
    MUSEUM = _("Museum")


class UrbexAccessibility(StringEnum):
    """Urbex location accessibility."""
    INACCESSIBLE = _("Inaccessible")
    GUIDED_TOURS = _("Guided tours")
    GUARDED = _("Guarded")
    MONITORED = _("Monitored")
    FREELY_ACCESSIBLE = _("Freely accessible")


class Urbex(DBItem):
    """Table of underground location metadata."""
    type = db.Column(IntEnum(UrbexType), nullable=False)
    state = db.Column(IntEnum(UrbexState), nullable=False)
    accessibility = db.Column(IntEnum(UrbexAccessibility))
    abandoned_year = db.Column(db.Integer())

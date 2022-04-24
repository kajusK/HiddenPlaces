"""Models for hiking locations."""
from flask_babel import lazy_gettext as _

from app.database import DBItem, db, IntEnum
from app.utils.enums import StringEnum


class HikingType(StringEnum):
    """Hiking location type."""
    OTHER = _("Other")
    NATURAL_SWIMMING = _("Natural swimming")
    SLEEPING_PLACE = _("Sleeping place")
    CAMP = _("Camp")
    SHED = _("Shed")


class HikingFeature(StringEnum):
    """Hiking features."""
    WATER = _("Water")
    POTABLE_WATER = _("Potable water")
    FIREPLACE = _("Fireplace")
    FURNACE = _("Furnace")
    SEATS = _("Seats")
    WEATHER_SHELTER = _("Weather shelter")


class Hiking(DBItem):
    """Table of hiking location metadata."""
    type = db.Column(IntEnum(HikingType), nullable=False)
    features = db.relationship("HikingFeatures", lazy='selectin',
                               cascade='all,delete-orphan')


class HikingFeatures(DBItem):
    """Table of features of a hiking location."""
    type = db.Column(IntEnum(HikingFeature), nullable=False)
    hiking_id = db.Column(db.Integer(), db.ForeignKey('hiking.id'),
                          nullable=False)

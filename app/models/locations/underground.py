"""Models for underground locations."""
from flask_babel import lazy_gettext as _

from app.database import DBItem, db, IntEnum
from app.utils.enums import StringEnum


MAX_TOOLS_LEN = 32


class UndergroundType(StringEnum):
    """Underground location type."""
    OTHER = _("Other")
    # Generic type for whole mine
    MINE = _("Mine")
    SHAFT = _("Shaft")
    ADIT = _("Adit")
    PINGE = _("Pinge")
    QUARRY = _("Quarry")
    SHELTER = _("Shelter")
    MILITARY_UNDERGROUND = _("Military underground")
    URBAN_UNDERGROUND = _("Urban underground")
    MILL_RACE = _("Mill race")
    DRAINAGE = _("Drainage")
    TUNNEL = _("Railway tunnel")


class UndergroundState(StringEnum):
    """Underground location state."""
    UNKNOWN = _("Unknown")
    WORKING = _("Working")
    MUSEUM = _("Museum")
    PRESERVED = _("Preserved")
    NOT_BAD = _("Not bad")
    BAD = _("Bad")
    DEMOLISHED = _("Demolished")


class UndergroundAccessibility(StringEnum):
    """Underground location accessibility."""
    INACCESSIBLE = _("Inaccessible")
    WORKING = _("Working")
    GUIDED_TOURS = _("Guided tours")
    GUARDED = _("Guarded")
    LOCKED = _("Locked")
    FREELY_ACCESSIBLE = _("Freely accessible")
    DIGGING_REQUIRED = _("Digging required")


class MaterialType(StringEnum):
    """Mined material types."""
    OTHER = _("Other")
    COAL = _("Coal")
    LIGNITE = _("Lignite")
    URANIUM = _("Uranium")
    FIRE_CLAY = _("Fire clay")
    KAOLINITE = _("Kaolinite")
    SAND = _("Sand")
    GRAPHITE = _("Graphite")
    IRON = _("Iron")
    GOLD = _("Gold")
    COPPER = _("Copper")
    SILVER = _("Silver")
    TIN = _("Tin")
    SLATE = _("Slate")
    BARYTE = _("Baryte")
    FLUORITE = _("Fluorite")
    FELDSPAR = _("Feldspar")


class Underground(DBItem):
    """Table of underground location metadata."""
    type = db.Column(IntEnum(UndergroundType), nullable=False)
    state = db.Column(IntEnum(UndergroundState), nullable=False)
    accessibility = db.Column(IntEnum(UndergroundAccessibility))
    tools = db.Column(db.String(MAX_TOOLS_LEN))

    length = db.Column(db.Integer())
    geofond_id = db.Column(db.Integer())
    abandoned_year = db.Column(db.Integer())

    materials = db.relationship("Material", lazy='selectin',
                                cascade='all,delete-orphan')


class Material(DBItem):
    """Table of materials mined in given location."""
    type = db.Column(IntEnum(MaterialType), nullable=False)
    underground_id = db.Column(db.Integer(), db.ForeignKey('underground.id'),
                               nullable=False)

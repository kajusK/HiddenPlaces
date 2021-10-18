""" Constants for locaiton module. """
from flask_babel import _
from app.utils import StringEnum

# DB strings lengths
MAX_LOCATION_LEN = 64
MAX_DESCRIPTION_LEN = 2048
MAX_NAME_LEN = 32
MAX_SHORT_DESC_LEN = 256
MAX_URL_LEN = 256
MAX_COMMENT_LEN = 2048


class LocationType(StringEnum):
    """Location types."""
    OTHER = 0, _("Other")
    # Generic type for whole mine
    MINE = 1, _("Mine")
    SHAFT = 2, _("Shaft")
    ADIT = 3, _("Adit")
    PINGE = 4, _("Pinge")
    QUARRY = 5, _("Quarry")
    SHELTER = 6, _("Shelter")
    MILITARY_UNDERGROUND = 7, _("Military underground")
    URBAN_UNDERGROUND = 8, _("Urban underground")
    MILL_RACE = 9, _("Mill race")
    DRAINAGE = 10, _("Drainage")
    BUILDINGS = 11, _("Buildings")


class LocationState(StringEnum):
    """Location states."""
    OTHER = 0, _("Other")
    WORKING = 1, _("Working")
    PRESERVED = 2, _("Preserved")
    NOT_BAD = 3, _("Not bad")
    BAD = 4, _("Bad")
    DEMOLISHED = 4, _("Demolished")
    UNKNOWN = 5, _("Unknown")


class MaterialType(StringEnum):
    """Mined material types."""
    OTHER = 0, _("Other")
    COAL = 1, _("Coal")
    LIGNITE = 2, _("Lignite")
    URANIUM = 3, _("Uranium")
    FIRE_CLAY = 4, _("Fire clay")
    KAOLINITE = 5, _("Kaolinite")
    SAND = 6, _("Sand")
    GRAPHITE = 7, _("Graphite")
    IRON = 8, _("Iron")
    GOLD = 9, _("Gold")
    COPPER = 10, _("Copper")
    SILVER = 11, _("Silver")
    TIN = 12, _("Tin")
    SLATE = 13, _("Slate")
    BARYTE = 14, _("Baryte")
    FLUORITE = 15, _("Fluorite")
    FELDSPAR = 16, _("Feldspar")


class Accessibility(StringEnum):
    """Location accessibility."""
    OTHER = 0, _("Other")
    WORKING = 1, _("Working")
    GUIDED_TOURS = 2, _("Guided tours")
    GUARDED = 3, _("Guarded")
    FREELY_ACCESSIBLE = 4, _("Freely accessible")
    LOCKED = 5, _("Locked")
    DIGGING_REQUIRED = 6, _("Digging required")
    DESTROYED = 7, _("Destroyed")


class Country(StringEnum):
    """Countries list."""
    OTHER = 0, _("Other")
    CZECHIA = 1, _("Czechia")
    SLOVAKIA = 2, _("Slovakia")
    POLAND = 3, _("Poland")
    GERMANY = 4, _("Germany")
    AUSTRIA = 5, _("Austria")


class POIType(StringEnum):
    """POI types."""
    OTHER = 0, _("Other")
    SHAFT = 1, _("Shaft")
    ADIT = 2, _("Adit")
    ENTRANCE = 3, _("Entrance")
    PARKING = 4, _("Parking")
    CAMPING = 5, _("Camping")
    BUILDING = 6, _("Building")

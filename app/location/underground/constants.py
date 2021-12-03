"""Constants for underground locations."""
from flask_babel import _
from app.utils.enums import StringEnum


MAX_TOOLS_LEN = 32


class UndergroundType(StringEnum):
    """Underground location type."""
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
    TUNNEL = 11, _("Railway tunnel")


class UndergroundState(StringEnum):
    """Underground location state."""
    UNKNOWN = 0, _("Unknown")
    WORKING = 1, _("Working")
    MUSEUM = 2, _("Museum")
    PRESERVED = 3, _("Preserved")
    NOT_BAD = 4, _("Not bad")
    BAD = 5, _("Bad")
    DEMOLISHED = 6, _("Demolished")


class UndergroundAccessibility(StringEnum):
    """Underground location accessibility."""
    INACCESSIBLE = 0, _("Inaccessible")
    WORKING = 1, _("Working")
    GUIDED_TOURS = 2, _("Guided tours")
    GUARDED = 3, _("Guarded")
    LOCKED = 4, _("Locked")
    FREELY_ACCESSIBLE = 4, _("Freely accessible")
    DIGGING_REQUIRED = 5, _("Digging required")


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

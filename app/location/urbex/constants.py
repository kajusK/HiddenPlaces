"""Constants for underground locations."""
from flask_babel import _
from app.utils import StringEnum


class UrbexType(StringEnum):
    """Urbex location type."""
    OTHER = 0, _("Other")
    # Generic type for whole mine
    HOUSE = 1, _("House")
    MANSION = 2, _("Mansion")
    RECREATION = 3, _("Recreation center")
    ARMY = 4, _("Army object")
    FACTORY = 5, _("Factory")
    TECHNOLOGY = 6, _("Technology")


class UrbexState(StringEnum):
    """Urbex location state."""
    UNKNOWN = 0, _("Unknown")
    LIKE_USED = 1, _("Like being used")
    FURNISHED = 2, _("Furnished")
    CLEANED_OUT = 3, _("Cleaned out")
    FALLING_APART = 4, _("Falling apart")
    DEMOLISHED = 5, _("Demolished")
    UNDER_RESTORE = 6, _("Under restoration")
    RESTORED = 7, _("Restored")
    MUSEUM = 8, _("Museum")


class UrbexAccessibility(StringEnum):
    """Urbex location accessibility."""
    INACCESSIBLE = 0, _("Inaccessible")
    GUIDED_TOURS = 1, _("Guided tours")
    GUARDED = 2, _("Guarded")
    MONITORED = 3, _("Monitored")
    FREELY_ACCESSIBLE = 4, _("Freely accessible")

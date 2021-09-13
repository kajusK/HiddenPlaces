from enum import Enum


class LocationState(Enum):
    DEMOLISHED = 0
    PUBLIC_VISITS = 1
    INACCESSIBLE = 2
    GUARDED = 3
    EMPTY = 4
    FURNISHED = 5
    DANGEROUS = 6


class LocationType(Enum):
    MINE = 0
    BUILDING = 1
    TOWER = 2
    CHIMNEY = 3
    CAMPING = 4


class LocationImportance(Enum):
    PUBLIC = 0
    GENERALLY_KNOWN = 1


class AttachementType(Enum):
    PHOTO = 0
    MAP = 1
    DOCUMENT = 2


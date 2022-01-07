"""Models for urbex locations."""
from app.database import DBItem, db, IntEnum
from app.location.urbex import constants


class Urbex(DBItem):
    """Table of underground location metadata."""
    type = db.Column(IntEnum(constants.UrbexType), nullable=False)
    state = db.Column(IntEnum(constants.UrbexState), nullable=False)
    accessibility = db.Column(IntEnum(constants.UrbexAccessibility))
    abandoned_year = db.Column(db.Integer())

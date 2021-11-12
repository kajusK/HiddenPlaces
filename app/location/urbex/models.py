"""Models for urbex locations."""
from app.database import DBItem, db
from app.location.urbex import constants


class Urbex(DBItem):
    """Table of underground location metadata."""
    type = db.Column(db.Enum(constants.UrbexType), nullable=False)
    state = db.Column(db.Enum(constants.UrbexState), nullable=False)
    accessibility = db.Column(db.Enum(constants.UrbexAccessibility))
    abandoned_year = db.Column(db.Integer())

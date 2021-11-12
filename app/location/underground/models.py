"""Models for underground locations."""
from app.database import DBItem, db
from app.location.underground import constants


class Underground(DBItem):
    """Table of underground location metadata."""
    type = db.Column(db.Enum(constants.UndergroundType), nullable=False)
    state = db.Column(db.Enum(constants.UndergroundState), nullable=False)
    accessibility = db.Column(db.Enum(constants.UndergroundAccessibility))
    tools = db.Column(db.String(constants.MAX_TOOLS_LEN))

    length = db.Column(db.Integer())
    geofond_id = db.Column(db.Integer())
    abandoned_year = db.Column(db.Integer())

    materials = db.relationship("Material", lazy='selectin',
                                cascade='all,delete-orphan')


class Material(DBItem):
    """Table of materials mined in given location."""
    type = db.Column(db.Enum(constants.MaterialType), nullable=False)
    underground_id = db.Column(db.Integer(), db.ForeignKey('underground.id'),
                               nullable=False)

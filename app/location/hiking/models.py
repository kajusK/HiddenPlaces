"""Models for hiking locations."""
from app.database import DBItem, db, IntEnum
from app.location.hiking import constants


class Hiking(DBItem):
    """Table of hiking location metadata."""
    type = db.Column(IntEnum(constants.HikingType), nullable=False)
    features = db.relationship("HikingFeatures", lazy='selectin',
                               cascade='all,delete-orphan')


class HikingFeatures(DBItem):
    """Table of features of a hiking location."""
    type = db.Column(IntEnum(constants.HikingFeature), nullable=False)
    hiking_id = db.Column(db.Integer(), db.ForeignKey('hiking.id'),
                          nullable=False)

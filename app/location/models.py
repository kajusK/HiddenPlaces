"""Models for locations module."""
import os
import uuid
from flask import current_app as app
from datetime import datetime
from werkzeug.utils import secure_filename

from app.database import DBItem, db, Latitude, Longitude, UUID
from app.location.constants import LocationType, LocationState, MaterialType, \
    Accessibility, Country, POIType
from app.location import constants
from app.upload.constants import UploadType

bookmark_association = db.Table(
    'bookmark_association',
    db.Column('bookmark_id', db.ForeignKey('bookmarks.id')),
    db.Column('location_id', db.ForeignKey('location.id'))
)


class Location(DBItem):
    """Table of locations."""
    uuid = db.Column(UUID(), default=uuid.uuid4)

    name = db.Column(db.String(constants.MAX_LOCATION_LEN), nullable=False)
    description = db.Column(db.String(constants.MAX_DESCRIPTION_LEN))
    about = db.Column(db.Text())

    created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    modified = db.Column(db.DateTime(), default=datetime.utcnow,
                         nullable=False)
    latitude = db.Column(Latitude(), nullable=False, index=True)
    longitude = db.Column(Longitude(), nullable=False, index=True)
    published = db.Column(db.Boolean(), nullable=False, index=True)

    country = db.Column(db.Enum(Country))
    type = db.Column(db.Enum(LocationType))
    state = db.Column(db.Enum(LocationState))
    accessibility = db.Column(db.Enum(Accessibility))

    length = db.Column(db.Integer())
    geofond_id = db.Column(db.Integer())
    abandoned_year = db.Column(db.Integer())

    parent_id = db.Column(db.Integer(), db.ForeignKey('location.id'))
    owner_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                         nullable=False, index=True)
    photo_id = db.Column(db.Integer(), db.ForeignKey('upload.id'))

    parent = db.relationship('Location', back_populates='children',
                             foreign_keys=parent_id)
    children = db.relationship('Location', back_populates='parent',
                               remote_side='Location.id')
    owner = db.relationship('User')
    photo = db.relationship('Upload', post_update=True, foreign_keys=photo_id)
    links = db.relationship('Link', back_populates='location', lazy='selectin', cascade='all,delete-orphan')
    uploads = db.relationship('Upload', primaryjoin="Location.uuid==foreign(Upload.object_uuid)")
    visits = db.relationship('Visit', back_populates='location', cascade='all,delete-orphan')
    materials = db.relationship("Material", back_populates='location',
                                lazy='selectin', cascade='all,delete-orphan')

    @classmethod
    def get_by_owner(cls, owner):
        return cls.query.filter_by(owner=owner).all()

    @classmethod
    def get_visited(cls, person):
        # TODO
        return cls.query.filter_by(owner=person).all()

    def has_documents(self):
        docs = filter(lambda x: x.type not in (
            UploadType.PHOTO, UploadType.HISTORICAL_PHOTO), self.uploads)
        return len(list(docs)) != 0


class Material(DBItem):
    """Table of materials mined in given location."""
    type = db.Column(db.Enum(MaterialType))
    location_id = db.Column(db.Integer(), db.ForeignKey('location.id'),
                            nullable=False)
    location = db.relationship("Location", back_populates='materials')


class Link(DBItem):
    """Table of links related to the location."""
    name = db.Column(db.String(constants.MAX_NAME_LEN), nullable=False)
    url = db.Column(db.String(constants.MAX_URL_LEN), nullable=False)

    created_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    location_id = db.Column(db.Integer(), db.ForeignKey('location.id'),
                            nullable=False)

    created_by = db.relationship('User')
    location = db.relationship('Location', back_populates='links')


class Visit(DBItem):
    """Table of users visits."""
    uuid = db.Column(UUID(), default=uuid.uuid4, nullable=False)

    visited_on = db.Column(db.Date(), default=datetime.utcnow, nullable=False)
    comment = db.Column(db.String(constants.MAX_COMMENT_LEN), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    location_id = db.Column(db.Integer(), db.ForeignKey('location.id'),
                            nullable=False)

    photos = db.relationship('Upload', primaryjoin="Visit.uuid==foreign(Upload.object_uuid)")
    user = db.relationship('User')
    location = db.relationship("Location", back_populates='visits')

    @classmethod
    def get_by_user(cls, user):
        return cls.query.filter_by(user=user).all()


class Bookmarks(DBItem):
    name = db.Column(db.String(constants.MAX_NAME_LEN), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    locations = db.relationship('Location', secondary=bookmark_association)

    @classmethod
    def get_by_user(cls, user):
        return cls.query.filter_by(user=user).all()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).all()

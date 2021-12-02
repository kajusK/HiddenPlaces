"""Models for locations module."""
import uuid
from datetime import datetime
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Query

from app.database import DBItem, db, Latitude, Longitude, UUID
from app.location.constants import Country, LocationType
from app.location import constants
from app.upload.constants import UploadType
from app.user.models import User


bookmark_association = db.Table(
    'bookmark_association',
    db.Column('bookmark_id', db.ForeignKey('bookmarks.id')),
    db.Column('location_id', db.ForeignKey('location.id'))
)


class Location(DBItem):
    """Location description."""
    __table_args__ = (
        CheckConstraint(
            'NOT(urbex_id IS NOT NULL AND underground_id IS NOT NULL)'),
    )

    uuid = db.Column(UUID(), default=uuid.uuid4, unique=True)

    name = db.Column(db.String(constants.MAX_NAME_LEN), nullable=False)
    description = db.Column(db.String(constants.MAX_DESCRIPTION_LEN))
    about = db.Column(db.Text())

    created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    modified = db.Column(db.DateTime(), default=datetime.utcnow,
                         nullable=False)
    latitude = db.Column(Latitude(), nullable=False)
    longitude = db.Column(Longitude(), nullable=False)
    published = db.Column(db.Boolean(), nullable=False)
    country = db.Column(db.Enum(Country), nullable=False)

    parent_id = db.Column(db.Integer(), db.ForeignKey('location.id'))
    owner_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                         nullable=False, index=True)
    photo_id = db.Column(db.Integer(), db.ForeignKey('upload.id'))

    # only one should be non-null
    urbex_id = db.Column(db.Integer(), db.ForeignKey('urbex.id'), unique=True)
    underground_id = db.Column(db.Integer(), db.ForeignKey('underground.id'),
                               unique=True)

    parent = db.relationship('Location', back_populates='children',
                             foreign_keys=parent_id)
    children = db.relationship('Location', back_populates='parent',
                               remote_side='Location.id')

    underground = db.relationship('Underground')
    urbex = db.relationship('Urbex')

    owner = db.relationship('User')
    photo = db.relationship('Upload', post_update=True, foreign_keys=photo_id)
    links = db.relationship('Link', lazy='selectin',
                            cascade='all,delete-orphan')
    uploads = db.relationship(
        'Upload', primaryjoin="Location.uuid==foreign(Upload.object_uuid)",
        cascade='all,delete-orphan')
    visits = db.relationship('Visit', back_populates='location',
                             cascade='all,delete-orphan')

    @classmethod
    def _filter(cls, query, loc_type: LocationType) -> Query:
        """Filter query based on location type.

        Args:
            query: SQL Query to be filtered
            loc_type: Location type to filter for
        Returns:
            Filtered query
        """
        if loc_type == LocationType.ALL:
            return query
        if loc_type == LocationType.UNDERGROUND:
            return query.filter(cls.underground_id.isnot(None))
        return query.filter(cls.urbex_id.isnot(None))

    @classmethod
    def get(cls, loc_type: LocationType) -> Query:
        """Query for locations

        Args:
            loc_type: Type of the location to query for

        Returns:
            Location query
        """
        query = cls.query.order_by(cls.modified.desc())
        return cls._filter(query, loc_type)

    @classmethod
    def get_unpublished(cls, loc_type: LocationType) -> Query:
        """Query for locations that are not published

        Args:
            loc_type: Type of the location to query for

        Returns:
            Location query
        """
        return cls.get(loc_type).filter_by(published=False)

    @classmethod
    def get_since(cls, since: datetime) -> Query:
        """Query locations added since date

        Args:
            since: Start date to filter locations from

        Returns:
            Location query
        """
        return cls.get(LocationType.ALL).filter(cls.created > since)

    @classmethod
    def get_by_owner(cls, loc_type: LocationType, owner: User) -> Query:
        """Query for locations owned by  user

        Args:
            loc_type: Type of the location to query for
            owner: Owner of the location record

        Returns:
            Locations owned by user query
        """
        return cls.get(loc_type).filter_by(owner=owner)

    @classmethod
    def get_visits(cls, loc_type: LocationType, user: User) -> Query:
        """Query for users visits

        Args:
            loc_type: Type of the location to query for
            user: User to get visits for
        """
        query = cls.query.join(Visit).filter_by(user=user).order_by(
            Visit.visited_on.desc())
        return cls._filter(query, loc_type)

    @classmethod
    def get_unique_visits(cls, loc_type: LocationType, user: User) -> Query:
        """Query for users unique visits

        Args:
            loc_type: Type of the location to query for
            user: User to get visits for
        """
        return cls.get_visits(loc_type, user).distinct()

    @classmethod
    def search(cls, string) -> Query:
        """Search for string in location names

        Args:
            string: String to search for

        Returns:
            Locations query corresponding to search string
        """
        return cls.query.filter(cls.name.like(f'%{string}%'))

    def has_documents(self) -> bool:
        """Checks if the location has any documents to show."""
        docs = filter(lambda x: x.type not in (
            UploadType.PHOTO, UploadType.HISTORICAL_PHOTO), self.uploads)
        return len(list(docs)) != 0

    def has_photos(self) -> bool:
        """Checks if the location has any photos to show."""
        images = filter(lambda x: x.type in (
            UploadType.PHOTO, UploadType.HISTORICAL_PHOTO)
            and x != self.photo, self.uploads)
        return len(list(images)) != 0


class Link(DBItem):
    """Table of links related to the location."""
    name = db.Column(db.String(constants.MAX_NAME_LEN), nullable=False)
    url = db.Column(db.String(constants.MAX_URL_LEN), nullable=False)

    created_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                              nullable=False)
    location_id = db.Column(db.Integer(), db.ForeignKey('location.id'),
                            nullable=False)

    created_by = db.relationship('User')


class Visit(DBItem):
    """Table of visits logs."""
    uuid = db.Column(UUID(), default=uuid.uuid4, nullable=False, unique=True)

    visited_on = db.Column(db.Date(), default=datetime.utcnow, nullable=False)
    comment = db.Column(db.String(constants.MAX_COMMENT_LEN), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    location_id = db.Column(db.Integer(), db.ForeignKey('location.id'),
                            nullable=False)

    photos = db.relationship(
        'Upload', primaryjoin="Visit.uuid==foreign(Upload.object_uuid)",
        cascade='all,delete-orphan', overlaps='uploads')
    user = db.relationship('User')
    location = db.relationship("Location", back_populates='visits')


class Bookmarks(DBItem):
    """Bookmarks lists table."""
    __table_args__ = (
        db.UniqueConstraint('name', 'user_id', name='unique_user_record'),
    )
    name = db.Column(db.String(constants.MAX_NAME_LEN), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    locations = db.relationship('Location', secondary=bookmark_association,
                                lazy="dynamic")

    @classmethod
    def get_by_user(cls, user: User) -> Query:
        """Gets list of bookmarks for given user.

        Args:
            user: User to get bookmarks for
        """
        return cls.query.filter_by(user=user)

    @classmethod
    def get_by_name(cls, user: User, name: str):
        """Gets bookmark list by it's name.

        Args:
            user: User to get bookmarks for
            name: Name of the bookmarks list
        """
        return cls.get_by_user(user).filter_by(name=name).first()

    @classmethod
    def name_exists(cls, user: User, name: str) -> bool:
        """Checks if bookmark list with given name exists.

        Args:
            user: User to check bookmarks for
            name: Bookmark list name to look for
        """
        if cls.query.filter_by(user=user, name=name).count() != 0:
            return True
        return False

"""Models for locations module."""
import uuid
from enum import Enum, auto
from datetime import datetime
from flask_babel import lazy_gettext as _
from sqlalchemy import CheckConstraint, or_
from sqlalchemy.orm import Query

from app.database import DBItem, db, Latitude, Longitude, UUID, IntEnum
from app.utils.enums import StringEnum
from app.models.upload import UploadType
from app.models.user import User


# DB strings lengths
MAX_NAME_LEN = 32
MAX_DESCRIPTION_LEN = 2048
MAX_SHORT_DESC_LEN = 256
MAX_URL_LEN = 256
MAX_COMMENT_LEN = 2048


bookmark_association = db.Table(
    'bookmark_association',
    db.Column('bookmark_id', db.ForeignKey('bookmarks.id')),
    db.Column('location_id', db.ForeignKey('location.id'))
)


category_association = db.Table(
    'category_association',
    db.Column('category_id', db.ForeignKey('category.id')),
    db.Column('location_id', db.ForeignKey('location.id'))
)


class LocationType(Enum):
    """Type of the saved location."""
    UNDERGROUND = auto()
    URBEX = auto()
    HIKING = auto()
    ALL = auto()


class Country(StringEnum):
    """Countries list."""
    OTHER = _("Other")
    CZECHIA = _("Czechia")
    SLOVAKIA = _("Slovakia")
    POLAND = _("Poland")
    GERMANY = _("Germany")
    AUSTRIA = _("Austria")


class Location(DBItem):
    """Location description."""
    __table_args__ = (
        CheckConstraint(
            'NOT(urbex_id IS NOT NULL ' +
            'AND underground_id IS NOT NULL ' +
            'AND hiking_id is not NULL)'),
    )

    uuid = db.Column(UUID(), default=uuid.uuid4, unique=True)

    name = db.Column(db.String(MAX_NAME_LEN), nullable=False)
    description = db.Column(db.String(MAX_DESCRIPTION_LEN))
    about = db.Column(db.Text())

    created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    modified = db.Column(db.DateTime(), default=datetime.utcnow,
                         nullable=False)
    latitude = db.Column(Latitude(), nullable=False)
    longitude = db.Column(Longitude(), nullable=False)
    published = db.Column(db.Boolean(), nullable=False)
    country = db.Column(IntEnum(Country), nullable=False)

    parent_id = db.Column(db.Integer(), db.ForeignKey('location.id'))
    owner_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                         nullable=False, index=True)
    photo_id = db.Column(db.Integer(), db.ForeignKey('upload.id'))

    # only one should be non-null
    urbex_id = db.Column(db.Integer(), db.ForeignKey('urbex.id'), unique=True)
    underground_id = db.Column(db.Integer(), db.ForeignKey('underground.id'),
                               unique=True)
    hiking_id = db.Column(db.Integer(), db.ForeignKey('hiking.id'),
                          unique=True)

    underground = db.relationship('Underground')
    urbex = db.relationship('Urbex')
    hiking = db.relationship('Hiking')

    owner = db.relationship('User')
    photo = db.relationship('Upload', post_update=True, foreign_keys=photo_id)
    links = db.relationship('Link', lazy='selectin',
                            cascade='all,delete-orphan')
    pois = db.relationship('POI', lazy='selectin', cascade='all,delete-orphan')
    uploads = db.relationship(
        'Upload', primaryjoin='Location.uuid==foreign(Upload.object_uuid)',
        cascade='all,delete-orphan')
    visits = db.relationship('Visit', back_populates='location',
                             cascade='all,delete-orphan')
    categories = db.relationship('Category', secondary=category_association,
                                 lazy='dynamic', back_populates='locations')

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
        elif loc_type == LocationType.UNDERGROUND:
            return query.filter(cls.underground_id.isnot(None))
        elif loc_type == LocationType.URBEX:
            return query.filter(cls.urbex_id.isnot(None))
        elif loc_type == LocationType.HIKING:
            return query.filter(cls.hiking_id.isnot(None))

        raise ValueError(f'Invalid location type: {loc_type}')

    @classmethod
    def filter_private(cls, query: Query, user: User) -> Query:
        """Filters out the private locations from query

        Args:
            query: SQL query to be filtered
            user: User viewing the data (his private locations will be shown)
        Returns:
            Filtered query
        """
        return query.filter(or_(cls.published, cls.owner == user))

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


class Category(DBItem):
    """Location categories table."""
    name = db.Column(db.String(MAX_NAME_LEN), nullable=False)
    uuid = db.Column(UUID(), default=uuid.uuid4, unique=True)
    description = db.Column(db.String(MAX_DESCRIPTION_LEN))
    about = db.Column(db.Text())

    created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    modified = db.Column(db.DateTime(), default=datetime.utcnow,
                         nullable=False)

    owner_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                         nullable=False, index=True)
    photo_id = db.Column(db.Integer(), db.ForeignKey('upload.id'))

    owner = db.relationship('User')
    photo = db.relationship('Upload', post_update=True, foreign_keys=photo_id)
    uploads = db.relationship(
        'Upload', primaryjoin='Category.uuid==foreign(Upload.object_uuid)',
        cascade='all,delete-orphan')
    locations = db.relationship('Location', secondary=category_association,
                                lazy='dynamic', back_populates='categories')

    @classmethod
    def get(cls) -> Query:
        """Query for categories

        Returns:
            Category query
        """
        return cls.query.order_by(cls.name.asc())

    @classmethod
    def choices(cls):
        """Get list of choices for wtforms (id, name)."""
        choices = [('', _('Categories'))]
        return choices + [(c.id, c.name) for c in cls.get().all()]

    @classmethod
    def coerce(cls, item):
        """Coerce method for wtforms.

        Args:
            item: Either class item or id to be coerced or '' for None
        Return:
            category
        Raises:
            ValueError: item not corresponding to any existing item
        """
        if isinstance(item, str) and item == '':
            return None

        if isinstance(item, Category):
            return item
        return cls.get_by_id(item)

    def has_documents(self) -> bool:
        """Checks if the category has any documents to show."""
        docs = filter(lambda x: x.type not in (
            UploadType.PHOTO, UploadType.HISTORICAL_PHOTO), self.uploads)
        return len(list(docs)) != 0

    def has_photos(self) -> bool:
        """Checks if the category has any photos to show."""
        images = filter(lambda x: x.type in (
            UploadType.PHOTO, UploadType.HISTORICAL_PHOTO)
            and x != self.photo, self.uploads)
        return len(list(images)) != 0


class Link(DBItem):
    """Table of links related to the location."""
    name = db.Column(db.String(MAX_NAME_LEN), nullable=False)
    url = db.Column(db.String(MAX_URL_LEN), nullable=False)

    created_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                              nullable=False)
    location_id = db.Column(db.Integer(), db.ForeignKey('location.id'),
                            nullable=False)

    created_by = db.relationship('User')


class POI(DBItem):
    """Table of points of interest"""
    name = db.Column(db.String(MAX_NAME_LEN), nullable=False)
    latitude = db.Column(Latitude(), nullable=False)
    longitude = db.Column(Longitude(), nullable=False)
    description = db.Column(db.String(MAX_SHORT_DESC_LEN))

    created_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                              nullable=False)
    location_id = db.Column(db.Integer(), db.ForeignKey('location.id'),
                            nullable=False)

    created_by = db.relationship('User')


class Visit(DBItem):
    """Table of visits logs."""
    uuid = db.Column(UUID(), default=uuid.uuid4, nullable=False, unique=True)

    visited_on = db.Column(db.Date(), default=datetime.utcnow, nullable=False)
    comment = db.Column(db.String(MAX_COMMENT_LEN), nullable=False)
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
    name = db.Column(db.String(MAX_NAME_LEN), nullable=False)
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

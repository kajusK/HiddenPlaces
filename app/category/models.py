"""Models for locations module."""
import uuid
from datetime import datetime
from sqlalchemy.orm import Query
from flask_babel import lazy_gettext as _
from app.database import DBItem, db, UUID
from app.location import constants


category_association = db.Table(
    'category_association',
    db.Column('category_id', db.ForeignKey('category.id')),
    db.Column('location_id', db.ForeignKey('location.id'))
)


class Category(DBItem):
    """Location categories table."""
    name = db.Column(db.String(constants.MAX_NAME_LEN), nullable=False)
    uuid = db.Column(UUID(), default=uuid.uuid4, unique=True)
    description = db.Column(db.String(constants.MAX_DESCRIPTION_LEN))
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
        'Upload', primaryjoin="Category.uuid==foreign(Upload.object_uuid)",
        cascade='all,delete-orphan')
    locations = db.relationship('Location', secondary=category_association,
                                lazy="dynamic")

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

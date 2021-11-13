"""Models for page module."""
from app.database import DBItem, db
from app.page.constants import PageType


class Page(DBItem):
    """Pages content"""
    text = db.Column(db.Text(), nullable=False)

    @classmethod
    def get(cls, page_type: PageType):
        """Gets the page."""
        return cls.get_by_id(page_type.value)

    @classmethod
    # pylint: disable=arguments-differ
    def create(cls, page_type: PageType, *args, **kwargs):
        """Creates the page."""
        return super().create(id=page_type.value, *args, **kwargs)

"""Page models."""
from flask_babel import lazy_gettext as _

from app.database import DBItem, db
from app.utils.enums import StringEnum


class PageType(StringEnum):
    """Type of the saved location."""
    ABOUT = _("About")
    RULES = _("Rules")
    SUPPORT = _("Support us")


class Page(DBItem):
    """Pages content"""
    text = db.Column(db.Text(), nullable=False)

    @classmethod
    def get(cls, page_type: PageType):
        """Gets the page."""
        return cls.get_by_id(page_type.value)

    @classmethod
    # pylint: disable=arguments-differ
    # type:ignore
    def create(cls, page_type: PageType, *args, **kwargs):
        """Creates the page."""
        return super().create(id=page_type.value, *args, **kwargs)

""" Constants for uploads module. """
from flask_babel import lazy_gettext as _
from app.utils.enums import StringEnum

# DB strings lengths
MAX_NAME_LEN = 32
MAX_DESCRIPTION_LEN = 1024
MAX_PATH_LEN = 256


class UploadType(StringEnum):
    """Upload file types."""
    OTHER = 0, _("Other")
    PHOTO = 1, _("Photo")
    HISTORICAL_PHOTO = 2, _("Historical photo")
    MAP = 3, _("Map")
    ARTICLE = 4, _("Article")
    BOOK = 5, _("Book")
    DOCUMENT = 6, _("Document")

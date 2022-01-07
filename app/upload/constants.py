""" Constants for uploads module. """
from flask_babel import lazy_gettext as _
from app.utils.enums import StringEnum

# DB strings lengths
MAX_NAME_LEN = 32
MAX_DESCRIPTION_LEN = 1024
MAX_PATH_LEN = 256


class UploadType(StringEnum):
    """Upload file types."""
    OTHER = _("Other")
    PHOTO = _("Photo")
    HISTORICAL_PHOTO = _("Historical photo")
    MAP = _("Map")
    ARTICLE = _("Article")
    BOOK = _("Book")
    DOCUMENT = _("Document")

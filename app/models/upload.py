"""Upload models."""
import os
import uuid
from typing import Optional
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app as app
from flask_babel import lazy_gettext as _

from app.database import DBItem, db, UUID, IntEnum
from app.utils.enums import StringEnum
from app.utils.image import Img


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


class Upload(DBItem):
    """Uploads model.

    The uploaded file is stored in a selected folder with in a UUID.extension
    format. This way the filename conflicts are reduced.
    """
    name = db.Column(db.String(MAX_NAME_LEN), nullable=False)
    description = db.Column(db.String(MAX_DESCRIPTION_LEN))
    type = db.Column(IntEnum(UploadType), nullable=False)
    path = db.Column(db.String(MAX_PATH_LEN), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    # Object UUID that is related to this file
    object_uuid = db.Column(UUID, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                              nullable=False)
    created_by = db.relationship('User')

    def _delete_file(self):
        """Deletes files related to this object."""
        delete_file(self.path)
        delete_file(self.thumbnail)

    def _make_thumbnail(self):
        """Creates thumbnail."""
        dest = get_full_path(self.thumbnail)
        img = Img(get_full_path(self.path))
        img.thumbnail(dest, app.config['THUMBNAIL_SIZE_PX'])

    def _save_file(self, file: FileStorage, subfolder: str):
        """Stores file to uploads dir, resize if needed

        Args:
            file: Uploaded file handle
            subfolder: Subfolder under uploads dir to write to
        """
        is_img = self.type in (UploadType.PHOTO, UploadType.HISTORICAL_PHOTO)
        self.path = save_uploaded_file(file, subfolder, str(uuid.uuid4()),
                                       is_img)
        if is_img:
            self._make_thumbnail()

    def delete(self):
        """Deletes file from drive and database."""
        self._delete_file()
        super().delete()

    def replace(self, file: FileStorage):
        """Replaces the file related to this upload with a new one.

        Args:
            file: Uploaded file handle
        """
        self._delete_file()
        subfolder = os.path.dirname(self.path)
        self._save_file(file, subfolder)

    @classmethod
    def create(cls, file: FileStorage, subfolder: str,  # type: ignore
               *args, **kwargs):
        """Create a new DB record and stores uploaded file to selected folder

        Args:
            file: Uploaded file handle
            subfolder: Folder relative to uploads folder to save data to
        """
        # pylint: disable=arguments-differ
        obj = super().create(path='', *args, **kwargs)
        obj._save_file(file, subfolder)
        return obj

    @classmethod
    def get(cls, upload_type: UploadType):
        """Gets query for all uploads of givent type

        Args:
            upload_type: Type to query for
        """
        return cls.query.filter(cls.type == upload_type)

    @property
    def thumbnail(self):
        """Returns relative path to thumbnail"""
        img_dir, name = os.path.split(self.path)
        return os.path.join(img_dir, 'thumbnail', name)


def get_full_path(path: str) -> str:
    """Gets full path to an uploaded file.

    Args:
        path: Relative path to file (from uploads folder)
    Returns:
        Full path to file
    """
    directory = os.path.join(app.instance_path, app.config['UPLOAD_DIR'])
    return os.path.join(directory, path)


def delete_file(path: Optional[str]):
    """Removes file from the uploads dir (if exists)

    Args:
        path: Relative path to file
    """
    if not path:
        return
    filename = get_full_path(path)
    if os.path.exists(filename):
        os.unlink(filename)


def save_uploaded_file(file, subfolder: str, filename: str,
                       reduce: bool = False) -> str:
    """Saves uploaded file to filesystem directly without DB entry.

    Args:
        file: Opened file handle
        subfolder: Folder under uploads directory to store file to
        filename: Name to save the file as. File extension is added if not set
        reduce: Assume file is image, reduce it's size before saving
    Returns:
        str: Path to the file under upload dir
    """
    filename = secure_filename(filename)

    extension = os.path.splitext(file.filename)[1]
    given_extension = os.path.splitext(filename)[1]
    if extension != given_extension:
        filename += extension

    directory = get_full_path(subfolder)
    if not os.path.exists(directory):
        os.makedirs(directory)

    full_path = os.path.join(directory, filename)
    if reduce:
        img = Img(file)
        img.thumbnail(full_path, app.config['IMAGE_MAX_SIZE_PX'])
    else:
        file.save(full_path)
    return os.path.join(subfolder, filename)

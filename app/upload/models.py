"""Models for uploads module."""
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app as app
from PIL import Image

from app.database import DBItem, db, UUID
from app.upload import constants
from app.upload.constants import UploadType


class Upload(DBItem):
    """Uploads model.

    The uploaded file is stored in a selected folder with in a UUID.extension
    format. This way the filename conflicts are reduced.
    """
    name = db.Column(db.String(constants.MAX_NAME_LEN), nullable=False)
    description = db.Column(db.String(constants.MAX_DESCRIPTION_LEN))
    type = db.Column(db.Enum(UploadType), nullable=False)
    path = db.Column(db.String(constants.MAX_PATH_LEN), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    # Object UUID that is related to this file
    object_uuid = db.Column(UUID, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                              nullable=False)
    created_by = db.relationship('User')

    @property
    def _base_dir(self) -> str:
        """Gets base directory for uploaded files"""
        return os.path.join(app.instance_path, app.config['UPLOAD_DIR'])

    def _delete_file(self):
        """Deletes files related to this object."""
        base = self._base_dir
        filename = os.path.join(base, self.path)
        thumbnail = os.path.join(base, self.thumbnail)

        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(thumbnail):
            os.remove(thumbnail)

    def _make_thumbnail(self):
        """Creates thumbnail from the image."""
        base = self._base_dir
        image_path = os.path.join(base, self.path)
        thumbnail_path = os.path.join(base, self.thumbnail)
        thumbnail_dir = os.path.dirname(thumbnail_path)

        if not os.path.exists(thumbnail_dir):
            os.mkdir(thumbnail_dir)

        size = (app.config['THUMBNAIL_SIZE_PX'],
                app.config['THUMBNAIL_SIZE_PX'])
        image = Image.open(image_path)
        image.thumbnail(size)
        image.save(thumbnail_path)

    def _reduce_resolution(self):
        """Reduces resolution of the image file to save space"""
        image_path = os.path.join(self._base_dir, self.path)
        size = (app.config['IMAGE_MAX_SIZE_PX'],
                app.config['IMAGE_MAX_SIZE_PX'])

        image = Image.open(image_path)
        image.thumbnail(size)
        image.save(image_path)

    def delete(self):
        """Deletes file from drive and database."""
        self._delete_file()
        super().delete()

    def replace(self, file):
        """Replaces the file related to this upload with a new one.

        Args:
            file: Opened file handler to be saved
        """
        self._delete_file()
        subfolder = os.path.dirname(self.path)
        self.path = save_uploaded_file(file, subfolder, str(uuid.uuid4()))
        if self.type == UploadType.PHOTO:
            self._reduce_resolution()
            self._make_thumbnail()

    @classmethod
    def create(cls, file, subfolder, *args, **kwargs):
        """Create a new DB record and stores uploaded file to selected folder

        Args:
            file: Opened file handler to be saved
            subfolder: Folder relative to uploads folder to save data to
        """
        # pylint: disable=arguments-differ
        obj = super().create(path='', *args, **kwargs)
        obj.path = save_uploaded_file(file, subfolder, str(uuid.uuid4()))
        if obj.type == UploadType.PHOTO:
            obj._reduce_resolution()
            obj._make_thumbnail()
        return obj

    @property
    def thumbnail(self):
        """Returns relative path to thumbnail"""
        img_dir, name = os.path.split(self.path)
        return os.path.join(img_dir, 'thumbnail', name)


def save_uploaded_file(file, subfolder: str, filename: str) -> str:
    """Save uploaded file to filesystem directly without DB entry.

    Args:
        file: Opened file handle
        subfolder: Folder under uploads directory to store file to
        filename: Name to save the file as. File extension is added if not set
    Returns:
        str: Path to the file under upload dir
    """
    filename = secure_filename(filename)

    extension = os.path.splitext(file.filename)[1]
    given_extension = os.path.splitext(filename)[1]
    if extension != given_extension:
        filename += extension

    base_dir = os.path.join(app.instance_path, app.config['UPLOAD_DIR'])
    directory = os.path.join(base_dir, subfolder)
    if not os.path.exists(directory):
        os.makedirs(directory)

    file.save(os.path.join(directory, filename))
    return os.path.join(subfolder, filename)

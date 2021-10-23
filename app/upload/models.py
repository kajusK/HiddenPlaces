"""Models for uploads module."""
import os
import uuid
from datetime import datetime
from werkzeug.utils import safe_join, secure_filename
from flask import current_app as app

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
    path = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    # Object UUID that is related to this file
    object_uuid = db.Column(UUID, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                              nullable=False)
    created_by = db.relationship("User")

    def delete(self):
        """Deletes file from drive and database."""
        base_dir = os.path.join(app.instance_path, app.config['UPLOAD_DIR'])
        filename = safe_join(base_dir, self.path)
        if os.path.exists(filename):
            os.remove(filename)
        super().delete()

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
        return obj


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
    directory = safe_join(base_dir, subfolder)
    if not os.path.exists(directory):
        os.makedirs(directory)

    file.save(safe_join(directory, filename))
    return safe_join(subfolder, filename)

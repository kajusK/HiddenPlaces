"""Routes for uploaded files."""
import os
from flask import Blueprint, send_from_directory, send_file, safe_join
from flask import current_app as app

blueprint = Blueprint('upload', __name__, url_prefix='/upload')


@blueprint.route('/<path:path>')
def get(path: str):
    """ Gets uploaded file from local storage.

    Args:
        path: Path to file, relative to upload directory
    """
    base_dir = os.path.join(app.instance_path, app.config['UPLOAD_DIR'])
    return send_from_directory(base_dir, path, conditional=True)

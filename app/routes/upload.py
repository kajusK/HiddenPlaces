"""Routes for uploaded files."""
import os
from typing import Tuple
from uuid import UUID
from flask import Blueprint, send_from_directory, abort, flash, \
    render_template, request
from flask import current_app as app
from flask_login import current_user
from flask_babel import _

from app.database import db
from app.utils.utils import redirect_return
from app.models.location import Location, Category
from app.forms.upload import PhotoForm, PhotoEditForm, DocumentForm, \
     DocumentEditForm
from app.models.upload import Upload, UploadType


blueprint = Blueprint('upload', __name__, url_prefix='/upload')


def _get_path_and_uuid(object_type: str,
                       object_id: int) -> Tuple[str, UUID]:
    """Gets subfolder corresponding to type object uuid

    Args:
        object_type: Type of the object (location, category)
        object_id: Id of the given object
    """
    if object_type == 'location':
        obj = Location.get_by_id(object_id)
        subfolder = f'location/{object_id}'
    elif object_type == 'category':
        obj = Category.get_by_id(object_id)
        subfolder = f'category/{object_id}'
    else:
        abort(404)

    if not obj:
        abort(404)
    return (subfolder, obj.uuid)


@blueprint.route('/<path:path>')
def get(path: str):
    """ Gets uploaded file from local storage.

    Args:
        path: Path to file, relative to upload directory
    """
    base_dir = os.path.join(app.instance_path, app.config['UPLOAD_DIR'])
    return send_from_directory(base_dir, path, conditional=True)


@blueprint.route('/photo/add/<string:object_type>/<int:object_id>',
                 methods=['GET', 'POST'])
def photo_add(object_type: str, object_id: int):
    """Renders form for uploading a new photo

    Args:
        object_type: Type of the object the upload belongs to (location,...)
        object_id: ID of the object the upload belongs to
    """
    subfolder, uuid = _get_path_and_uuid(object_type, object_id)

    form = PhotoForm()
    if form.validate_on_submit():
        Upload.create(
            file=form.file.data,
            subfolder=subfolder + '/photos',
            name=form.name.data,
            description=form.description.data,
            created=form.taken_on.data,
            type=UploadType.PHOTO,
            created_by=current_user,
            object_uuid=uuid,
        )
        db.session.commit()
        flash(_("New photo added"), 'success')
        return redirect_return()

    return render_template('upload/photo.html', form=form)


@blueprint.route('/photo/edit/<int:photo_id>', methods=['GET', 'POST'])
def photo_edit(photo_id: int):
    """Renders form for editing existing photo

    Args:
        photo_id: ID of the photo to be edited
    """
    photo = Upload.get_by_id(photo_id)
    if not photo or photo.type != UploadType.PHOTO:
        abort(404)

    form = PhotoEditForm()
    if request.method == 'GET':
        form.name.data = photo.name
        form.description.data = photo.description
        form.taken_on.data = photo.created
    elif form.validate_on_submit():
        photo.name = form.name.data
        photo.description = form.description.data
        photo.created = form.taken_on.data
        db.session.commit()
        return redirect_return()

    return render_template('upload/photo.html', form=form)


@blueprint.route('/document/add/<string:object_type>/<int:object_id>',
                 methods=['GET', 'POST'])
def document_add(object_type: str, object_id: int):
    """Renders form for adding a new document

    Args:
        object_type: Type of the object the upload belongs to
        object_id: ID of the object the upload belongs to
    """
    subfolder, uuid = _get_path_and_uuid(object_type, object_id)

    form = DocumentForm()
    if form.validate_on_submit():
        Upload.create(
            file=form.file.data,
            subfolder=subfolder+'/files',
            name=form.name.data,
            description=form.description.data,
            type=form.type.data,
            created_by=current_user,
            object_uuid=uuid)

        db.session.commit()
        flash(_("New document added"), 'success')
        return redirect_return()

    return render_template('upload/document.html', form=form)


@blueprint.route('/document/edit/<int:document_id>', methods=['GET', 'POST'])
def document_edit(document_id: int):
    """Edits document entry.

    Args:
        document_id: ID of the document to be edited
    """
    document = Upload.get_by_id(document_id)
    if not document:
        return abort(404)

    form = DocumentEditForm()
    if request.method == 'GET':
        form.name.data = document.name
        form.description.data = document.description
        form.type.data = document.type
    elif form.validate_on_submit():
        document.name = form.name.data
        document.description = form.description.data
        document.type = form.type.data
        if form.file.data:
            document.replace(form.file.data)
        db.session.commit()
        return redirect_return()

    return render_template('upload/document.html', form=form)


@blueprint.route('/remove/<int:upload_id>')
def remove(upload_id: int):
    """Deletes uploaded file and DB record

    Args:
        upload_id: ID of the uploaded file
    """
    upload = Upload.get_by_id(upload_id)
    if not upload:
        abort(404)

    upload.delete()
    db.session.commit()
    return redirect_return()

"""Forms for upload module."""
from datetime import datetime
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SelectField, SubmitField, DateField
from wtforms.validators import InputRequired, Length

from app.upload import constants
from app.upload.constants import UploadType
from app.utils.validators import image_file, allowed_file, date_in_past


class _UploadForm(FlaskForm):
    """Common fields for upload forms."""
    name = StringField(
        _("Name"),
        [InputRequired(), Length(min=3, max=constants.MAX_NAME_LEN)])
    description = StringField(
        _("Description"), [Length(max=constants.MAX_DESCRIPTION_LEN)])
    submit = SubmitField(_("Save"))


class DocumentEditForm(_UploadForm):
    """Document edit form."""
    type = SelectField(_("Document type"), [InputRequired()],
                       coerce=UploadType.coerce,
                       choices=UploadType.choices([UploadType.PHOTO]))
    # File not required by default when editing
    file = FileField(_("Document"), [allowed_file()])


class DocumentForm(DocumentEditForm):
    """New document form."""
    file = FileField(_("Document"), [FileRequired(), allowed_file()])


class PhotoEditForm(_UploadForm):
    """Photo edit form."""
    taken_on = DateField(_('Taken on:'), [InputRequired(), date_in_past()],
                         default=datetime.utcnow)
    file = FileField(_('Photo'), [image_file()])


class PhotoForm(PhotoEditForm):
    """New photo form."""
    file = FileField(_('Photo'), [FileRequired(), image_file()])

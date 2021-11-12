"""Forms for location module."""
from datetime import datetime
from flask_babel import _
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SelectField, TextAreaField, SubmitField, \
    RadioField, ValidationError
from wtforms.validators import InputRequired, Length, URL
from wtforms.fields.html5 import DateField

from app.location import constants
from app.location.models import Bookmarks
from app.location.constants import Country
from app.upload.constants import UploadType
from app.fields import MultipleFileField
from app.validators import image_file, allowed_file, latitude, longitude, \
    date_in_past


class LocationForm(FlaskForm):
    """Generic location form"""
    name = StringField(
        _("Name"),
        [InputRequired(), Length(min=3, max=constants.MAX_NAME_LEN)])
    description = TextAreaField(
        _("Description"),
        [InputRequired(), Length(max=constants.MAX_DESCRIPTION_LEN)])
    about = TextAreaField(_("About"))

    latitude = StringField(_("Latitude"), [InputRequired(), latitude()])
    longitude = StringField(_("Longitude"), [InputRequired(), longitude()])

    published = RadioField(_("Published"), default=0,
                           choices=[(0, _("No")), (1, _("Yes"))])
    country = SelectField(_("Country"), [InputRequired()],
                          coerce=Country.coerce, choices=Country.choices(),
                          default=Country.CZECHIA)
    photo = FileField(_("Title photo"), [image_file()])
    submit = SubmitField(_("Save"))


class DocumentEditForm(FlaskForm):
    """Document edit form."""
    name = StringField(
        _("Name"),
        [InputRequired(), Length(min=3, max=constants.MAX_NAME_LEN)])
    description = StringField(
        _("Description"),
        [InputRequired(), Length(min=3, max=constants.MAX_DESCRIPTION_LEN)])
    type = SelectField(_("Document type"), [InputRequired()],
                       coerce=UploadType.coerce,
                       choices=UploadType.choices([UploadType.PHOTO]))
    # File not required by default when editing
    file = FileField(_("Document"), [allowed_file()])
    submit = SubmitField(_("Save"))


class DocumentForm(DocumentEditForm):
    """New document form."""
    file = FileField(_("Document"), [FileRequired(), allowed_file()])


class PhotoEditForm(FlaskForm):
    """Photo edit form."""
    name = StringField(
        _("Name"),
        [InputRequired(), Length(min=3, max=constants.MAX_NAME_LEN)])
    description = StringField(
        _("Description"),
        [InputRequired(), Length(min=3, max=constants.MAX_DESCRIPTION_LEN)])
    taken_on = DateField(_('Taken on:'), [InputRequired(), date_in_past()],
                         default=datetime.utcnow)
    submit = SubmitField(_('Save'))


class PhotoForm(PhotoEditForm):
    """New photo form."""
    file = FileField(_('Photo'), [FileRequired(), image_file()])


class LinkForm(FlaskForm):
    """New link form."""
    url = StringField("URL", [InputRequired(), URL(require_tld=True),
                              Length(max=constants.MAX_URL_LEN)])
    name = StringField(_("Name"), [InputRequired(),
                                   Length(min=3, max=constants.MAX_NAME_LEN)])
    submit = SubmitField(_("Save"))


class VisitForm(FlaskForm):
    """Log visit form."""
    comment = TextAreaField(_("Comment"),
                            [InputRequired(),
                             Length(min=3, max=constants.MAX_COMMENT_LEN)])
    date = DateField(_("Visited on"), [InputRequired(), date_in_past()],
                     default=datetime.utcnow)
    photos = MultipleFileField(_('Photos'), [image_file()])
    submit = SubmitField(_('Log your visit'))


class BookmarkForm(FlaskForm):
    """New bookmark form."""
    name = StringField(_('Name'), [InputRequired(),
                                   Length(min=3, max=constants.MAX_NAME_LEN)])
    submit = SubmitField(_('Add'))

    def validate_name(self, field):
        """Validates the bookmark with same name doesn't exist yet."""
        if Bookmarks.name_exists(current_user, field.data):
            raise ValidationError(_("Name already used"))

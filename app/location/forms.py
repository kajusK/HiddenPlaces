from datetime import datetime
from flask_babel import _
from flask import current_app as app
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, BooleanField, SelectMultipleField, RadioField, SelectField, ValidationError, SelectMultipleField
from flask_wtf.file import FileField, FileRequired
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import InputRequired, Length, Optional, NumberRange, URL

from app.fields import MultipleFileField
from app.upload.constants import UploadType
from app.location import constants
from app.utils import LatLon
from app.validators import image_file, allowed_file
from app.location.models import Bookmarks
from app.location.constants import LocationType, LocationState, MaterialType, Accessibility, Country


class CustomMultipleField(SelectMultipleField):
    """Custom multiple selection fields with support for StringEnum."""
    def pre_validate(self, form):
        if self.choices is None:
            raise TypeError(self.gettext("Choices cannot be None."))

        if not self.validate_choice or not self.data:
            return

        acceptable = {self.coerce(c[0]) for c in self.iter_choices()}
        if any(d not in acceptable for d in self.data):
            unacceptable = [str(d) for d in set(self.data) - acceptable]
            raise ValidationError(
                self.ngettext(
                    "'%(value)s' is not a valid choice for this field.",
                    "'%(value)s' are not valid choices for this field.",
                    len(unacceptable),
                )
                % dict(value="', '".join(unacceptable))
            )


class LocationForm(FlaskForm):
    name = StringField(_('Name'),
                       [InputRequired(),
                        Length(min=3, max=constants.MAX_LOCATION_LEN)])
    description = TextAreaField(_('Description'),
                                [InputRequired(),
                                 Length(max=constants.MAX_DESCRIPTION_LEN)])
    about = TextAreaField(_('About'))

    photo = FileField(_('Title photo'), [image_file()])
    latitude = StringField(_('Latitude'), [InputRequired()])
    longitude = StringField(_('Longitude'), [InputRequired()])

    country = SelectField(_('Country'), [InputRequired()],
                          coerce=Country.coerce, choices=Country.choices(),
                          default=Country.CZECHIA)
    type = SelectField(_('Type'), [InputRequired()],
                       coerce=LocationType.coerce,
                       choices=[('', _("Location type"))]
                       + LocationType.choices())
    state = SelectField(_('State'), [InputRequired()],
                        coerce=LocationState.coerce,
                        choices=[('', _("Location state"))]
                        + LocationState.choices())
    accessibility = SelectField(_('Accessibility'), [InputRequired()],
                                coerce=Accessibility.coerce,
                                choices=[('', _("Location accessibility"))]
                                + Accessibility.choices())
    materials = CustomMultipleField(_('Materials'), [InputRequired()],
                                    coerce=MaterialType.coerce,
                                    choices=[('', _("Select mined materials"))]
                                    + MaterialType.choices())

    length = IntegerField(_('Length [m]'), [Optional(), NumberRange(min=0)])
    geofond_id = IntegerField(_('Geofond ID'),
                              [Optional(), NumberRange(min=0)])
    abandoned = IntegerField(_('Abandoned [year]'), [Optional()])
    published = RadioField(_('Published'), default=0,
                           choices=[(0, _("No")), (1, _("Yes"))])
    submit = SubmitField(_('Save'))

    def validate_abandoned(self, field):
        if field.data > datetime.utcnow().year:
            raise ValidationError(_("It cannot be in the future"))

    def validate_latitude(self, field):
        try:
            self.latitude.data = LatLon.from_str(field.data)
        except ValueError:
            raise ValidationError(_("Invalid value"))

        if not self.latitude.data.is_latitude:
            raise ValidationError(_("Not a latitude"))

    def validate_longitude(self, field):
        try:
            self.longitude.data = LatLon.from_str(field.data)
        except ValueError:
            raise ValidationError(_("Invalid value"))

        if not self.longitude.data.is_longitude:
            raise ValidationError(_("Not a longitude"))


class DocumentEditForm(FlaskForm):
    name = StringField(_('Name'), [InputRequired()])
    description = StringField(_('Description'), [InputRequired()])
    type = SelectField(_('Document type'), [InputRequired()],
                       coerce=UploadType.coerce,
                       choices=UploadType.choices([UploadType.PHOTO]))
    # File not required by default when editing
    file = FileField(_('Document'), [allowed_file()])
    submit = SubmitField(_('Save'))


class DocumentForm(DocumentEditForm):
    file = FileField(_('Document'), [FileRequired(), allowed_file()])


class PhotoEditForm(FlaskForm):
    name = StringField(_('Name'), [InputRequired()])
    description = StringField(_('Description'), [InputRequired()])
    taken_on = DateField(_('Taken on:'), [InputRequired()],
                         default=datetime.utcnow)
    submit = SubmitField(_('Save'))

    def validate_taken_on(self, field):
        if field.data > datetime.utcnow().date():
            raise ValidationError(_("It cannot be in the future"))


class PhotoForm(PhotoEditForm):
    file = FileField(_('Photo'), [FileRequired(), image_file()])


class LinkForm(FlaskForm):
    url = StringField('URL', [InputRequired(), URL(require_tld=True)])
    name = StringField(_('Name'), [InputRequired()])
    submit = SubmitField(_('Save'))


class VisitForm(FlaskForm):
    comment = TextAreaField(_('Comment'), [InputRequired()])
    date = DateField(_('Visited on:'), [InputRequired()], default=datetime.utcnow)
    photos = MultipleFileField(_('Photos'), [image_file()])
    submit = SubmitField(_('Log your visit'))

    def validate_date(self, field):
        if field.data > datetime.utcnow().date():
            raise ValidationError(_("It cannot be in the future"))


class BookmarkForm(FlaskForm):
    name = StringField(_('Name'), [InputRequired()])
    submit = SubmitField(_('Add'))

    def validate_name(self, field):
        if len(Bookmarks.get_by_name(current_user, field.data)):
            raise ValidationError(_("Name already used"))

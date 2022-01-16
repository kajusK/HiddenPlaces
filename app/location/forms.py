"""Forms for location module."""
from datetime import datetime
from flask_babel import lazy_gettext as _
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, TextAreaField, SubmitField, \
    RadioField, DateField, ValidationError
from wtforms.validators import InputRequired, Length, URL

from app.location import constants
from app.location.models import Bookmarks
from app.location.constants import Country
from app.category.models import Category
from app.utils.fields import MultipleFileField, CustomMultipleField
from app.utils.validators import image_file, latitude, \
    longitude, date_in_past


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
    # Categories are filled up in view function
    categories = CustomMultipleField(_("Categories"), coerce=Category.coerce,
                                     choices=Category.choices)
    photo = FileField(_("Title photo"), [image_file()])
    submit = SubmitField(_("Save"))


class LinkForm(FlaskForm):
    """New link form."""
    url = StringField("URL", [InputRequired(), URL(require_tld=True),
                              Length(max=constants.MAX_URL_LEN)])
    name = StringField(_("Name"), [InputRequired(),
                                   Length(min=3, max=constants.MAX_NAME_LEN)])
    submit = SubmitField(_("Save"))


class POIForm(FlaskForm):
    """Point of interest form."""
    name = StringField(
        _("Name"),
        [InputRequired(), Length(min=3, max=constants.MAX_NAME_LEN)])
    description = StringField(
        _("Description"), [Length(max=constants.MAX_SHORT_DESC_LEN)])
    latitude = StringField(_("Latitude"), [InputRequired(), latitude()])
    longitude = StringField(_("Longitude"), [InputRequired(), longitude()])
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

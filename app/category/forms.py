"""Forms for location module."""
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import InputRequired, Length

from app.utils.validators import image_file
from app.location import constants


class CategoryForm(FlaskForm):
    """Category form"""
    name = StringField(
        _("Name"),
        [InputRequired(), Length(min=3, max=constants.MAX_NAME_LEN)])
    description = TextAreaField(
        _("Description"),
        [InputRequired(), Length(max=constants.MAX_DESCRIPTION_LEN)])
    about = TextAreaField(_("About"))
    photo = FileField(_("Title photo"), [image_file()])
    submit = SubmitField(_("Save"))

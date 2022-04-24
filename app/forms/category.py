"""Location category form."""
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import InputRequired, Length

from app.models import location
from app.utils.validators import image_file


class CategoryForm(FlaskForm):
    """Category form"""
    name = StringField(
        _("Name"),
        [InputRequired(), Length(min=3, max=location.MAX_NAME_LEN)])
    description = TextAreaField(
        _("Description"),
        [InputRequired(), Length(max=location.MAX_DESCRIPTION_LEN)])
    about = TextAreaField(_("About"))
    photo = FileField(_("Title photo"), [image_file()])
    submit = SubmitField(_("Save"))

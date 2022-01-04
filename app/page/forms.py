"""Forms for page module."""
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length


class ContactForm(FlaskForm):
    """Contact form for sending messages to admins."""
    subject = StringField(_('Subject'), [InputRequired(), Length(max=64)])
    text = TextAreaField(_('Your message'), [InputRequired()])
    submit = SubmitField(_('Send'))


class EditForm(FlaskForm):
    """Edit page form."""
    text = TextAreaField(_('Page content'), [InputRequired()])
    submit = SubmitField(_('Save'))

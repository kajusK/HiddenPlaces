"""Forms for admin module."""
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length


class MessageForm(FlaskForm):
    """Contact form for sending messages to all users."""
    subject = StringField(_('Subject'), [InputRequired(), Length(max=64)])
    text = TextAreaField(_('Your message'), [InputRequired()])
    email = BooleanField(_('Send as email'))
    submit = SubmitField(_('Send'))

"""Forms for message module."""
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length

from app.message import constants


class WriteForm(FlaskForm):
    """New message form."""
    subject = StringField(_("Subject"),
                          [InputRequired(),
                           Length(max=constants.MAX_SUBJECT_LEN)])
    message = TextAreaField(_("Message"), [InputRequired()])
    submit = SubmitField(_("Send"))


class ReplyForm(FlaskForm):
    """Reply to message form."""
    message = TextAreaField(_("Message"), [InputRequired()])
    submit = SubmitField(_("Reply"))

from flask_wtf import FlaskForm
from flask_login import current_user
from flask_babel import _
from wtforms import StringField, PasswordField, BooleanField, ValidationError, SubmitField, FileField, TextAreaField, RadioField, SelectField
from wtforms.fields.html5 import EmailField, DateField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Email, Length


class NewMessageForm(FlaskForm):
    subject = StringField(_('Subject'), [InputRequired()])
    message = TextAreaField(_('Message'), [InputRequired()])
    to = SelectField(_('To'), choices=[(0, 'User Name'), (1, 'Other User')])
    submit = SubmitField(_('Send'))


class ReplyForm(FlaskForm):
    message = TextAreaField(_('Message'), [InputRequired()])
    submit = SubmitField(_('Reply'))

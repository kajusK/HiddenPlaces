import re
from datetime import datetime
from flask_wtf import FlaskForm
from flask_babel import _
from wtforms import StringField, SelectField, TextAreaField, SubmitField, FileField, BooleanField, SelectMultipleField, RadioField, SelectField
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import InputRequired, Length


class ContactForm(FlaskForm):
    subject = StringField(_('Subject'), [InputRequired()])
    text = TextAreaField(_('Your message'), [InputRequired()])
    submit = SubmitField(_('Send'))


class EditForm(FlaskForm):
    text = TextAreaField(_('Page content'), [InputRequired()])
    submit = SubmitField(_('Save'))

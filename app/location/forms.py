import re
from datetime import datetime
from flask_wtf import FlaskForm
from flask_babel import _
from wtforms import StringField, SelectField, TextAreaField, SubmitField, FileField, BooleanField, SelectMultipleField, RadioField, SelectField
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import InputRequired, Length

from .models import Tag


class LocationForm(FlaskForm):
    name = StringField(_('Name'), [InputRequired()])
    description = TextAreaField(_('Description'), [InputRequired()])
    about = TextAreaField(_('About'))
    photo = FileField(_('Title photo'))
    latitude = StringField(_('Latitude'), [InputRequired()])
    longitude = StringField(_('Longitude'), [InputRequired()])
    materials = SelectMultipleField(_('Materials'), choices=[('', _('Choose mined material')), (1, 'Slate'), (2, 'Iron'), (3, 'Gold')])
    type = SelectField(_('Type'), choices=[('', 'Location type'), (0, 'Mine'), (1, 'Shaft')])
    state = SelectField(_('State'), choices=[(0, 'Demolished'), (1, 'Accessible')])
    area = SelectField(_('Area'), choices=[('', 'Mine location'), (0, 'Moravskoslezský'), (1, 'Jihomoravský')])
    length = IntegerField(_('Length [m]'), [InputRequired()], default=0)
    abandoned = IntegerField(_('Abandoned [year]'), [InputRequired()], default=0)
    published = RadioField(_('Published'), choices=[(0, 'No'), (1, 'Yes')], default=0)
    submit = SubmitField(_('Save'))

    #tags = SelectMultipleField(_('Tags'), choices=[])

    #def validate_latitude(self, form, field):
    #    pass

    #def validate_longitude(self, form, field):
    #    pass


class VisitForm(FlaskForm):
    comment = TextAreaField(_('Comment'), [InputRequired()])
    date = DateField(_('Visited on:'), [InputRequired()], default=datetime.now())
    submit = SubmitField(_('Log your visit'))


class DocumentForm(FlaskForm):
    name = StringField(_('Name'), [InputRequired()])
    description = StringField(_('Description'), [InputRequired()])
    source = StringField(_('Source citation'), [InputRequired()])
    file = FileField(_('Document'))
    submit = SubmitField(_('Save'))


class PhotoForm(FlaskForm):
    name = StringField(_('Name'), [InputRequired()])
    description = StringField(_('Description'), [InputRequired()])
    source = StringField(_('Source citation'), [InputRequired()])
    file = FileField(_('Photo'))
    submit = SubmitField(_('Save'))


class AttachementForm(FlaskForm):
    name = StringField(_('Name'), [InputRequired()])
    description = StringField(_('Name'), [InputRequired()])


class CommentForm(FlaskForm):
    pass

from flask_wtf import FlaskForm
from flask_babel import _
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, Length

from .models import User


class LoginForm(FlaskForm):
    username = StringField(_('Username'), [DataRequired()])
    password = PasswordField(_('Password'), [DataRequired()])
    remember_me = BooleanField(_('Remember me'))

    def validate(self):
        if not super().validate():
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user or not self.user.check_password(self.password.data):
            self.username.errors.append(_("Invalid user or password"))
            return False
        elif not self.user.active:
            self.username.errors.append(_("User is not active"))
            return False

        return True


class RegisterForm(FlaskForm):
    username = StringField(_('Username'),
                           [DataRequired(), Length(min=3, max=20)])
    email = StringField(_('Email address'), [DataRequired(), Email(),
                                             Length(min=3, max=80)])
    password = PasswordField(_('Password'), [DataRequired(), Length(min=6)])
    confirm = PasswordField(_('Repeat Password'), [
        DataRequired(),
        EqualTo('password', message=_('Passwords must match'))
        ])

    def validate(self):
        ret = True
        if not super().validate():
            ret = False

        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append(_("Username already taken"))
            ret = False

        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append(_("Email already taken"))
            ret = False

        return ret

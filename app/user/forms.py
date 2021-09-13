from flask_wtf import FlaskForm
from flask_login import current_user
from flask_babel import _
from wtforms import StringField, PasswordField, BooleanField, ValidationError, SubmitField, FileField, TextAreaField, RadioField
from wtforms.fields.html5 import EmailField, DateField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Email, Length

from .models import User
from app.utils import password_rules


class LoginForm(FlaskForm):
    email = EmailField(_('Email address'), [InputRequired(), Email()])
    password = PasswordField(_('Password'), [InputRequired()])
    remember_me = BooleanField(_('Remember me'))
    submit = SubmitField(_('Log In'))

    def validate(self):
        if not super().validate():
            return False

        self.user = User.query.filter_by(email=self.email.data).first()
        if not self.user or not self.user.check_password(self.password.data):
            self.email.errors.append(_("Invalid email or password"))
            self.password.errors.append("")
            return False
        elif not self.user.active:
            self.email.errors.append(_("User is not active"))
            return False

        return True


class RegisterForm(FlaskForm):
    first_name = StringField(_('First name'),
                             [InputRequired(),
                              Length(min=2, max=40, message=_("First name must be at least 2 characters long"))])
    last_name = StringField(_('Last name'),
                            [InputRequired(),
                             Length(min=2, max=40, message=_("Last name must be at least 2 characters long"))])
    email = EmailField(_('Email address'), [InputRequired(), Email()])
    password = PasswordField(_('Password'),
                             [InputRequired(), password_rules()])
    confirm = PasswordField(_('Repeat Password'), [
        InputRequired(),
        EqualTo('password', message=_('Passwords must match'))
        ])
    rules_agree = BooleanField()
    submit = SubmitField(_('Register'))

    def validate_email(form, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError(_("Email already used"))

    def validate_rules_agree(form, field):
        if not field.data:
            raise ValidationError(_("You must agree with page rules"))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(_('Current password'), [InputRequired()])
    password = PasswordField(_('New password'),
                             [InputRequired(), password_rules()])
    confirm = PasswordField(_('Repeat new password'), [
        InputRequired(),
        EqualTo('password', message=_('Passwords must match'))
        ])
    submit = SubmitField(_('Change password'))

    def validate_old_password(form, field):
        if not current_user.check_password(field.data):
            raise ValidationError(_("Invalid password"))


class EditProfileForm(FlaskForm):
    about = TextAreaField(_('About'), [InputRequired()])
    photo = FileField(_('Profile photo'))
    submit = SubmitField(_('Save'))


class BanForm(FlaskForm):
    reason = TextAreaField(_('Ban reason'), [InputRequired()])
    days = IntegerField(_('Ban length [days]'), [InputRequired()])
    permanent = RadioField(_('Ban permanently'), choices=[(0, 'No'), (1, 'Yes')], default=0)
    submit = SubmitField(_('Ban!'))


class InviteForm(FlaskForm):
    name = StringField(_('Name of the person'), [InputRequired()])
    email = EmailField(_('Email address'), [InputRequired(), Email()])
    reason = TextAreaField(_('Invitation reason'), [InputRequired()])
    submit = SubmitField(_('Send Invitation'))

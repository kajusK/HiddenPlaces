""" Forms for user related pages. """
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_babel import _, format_date
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, RadioField, \
    ValidationError, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Email, Length, \
    NumberRange

from app.user.models import User, Invitation
from app.validators import password_rules, image_file
from app.user.constants import LoginResult, MAX_FIRST_NAME_LEN, \
    MAX_LAST_NAME_LEN, MAX_EMAIL_LEN, MAX_ABOUT_LEN, MAX_REASON_LEN


class LoginForm(FlaskForm):
    """Login form handling."""
    email = EmailField(_("Email address"),
                       [InputRequired(), Email(), Length(max=MAX_EMAIL_LEN)])
    password = PasswordField(_("Password"), [InputRequired()])
    remember_me = BooleanField(_("Remember me"))
    submit = SubmitField(_("Log In"))
    user = None
    result = LoginResult.SUCCESS

    def validate(self, extra_validators=None) -> bool:
        """Validates the email and password against the user database."""
        if not super().validate(extra_validators):
            return False

        self.user = User.query.filter_by(email=self.email.data).first()
        self.result = LoginResult.SUCCESS
        if not self.user:
            self.result = LoginResult.INVALID_EMAIL
            self.email.errors.append(_("Invalid email or password"))
            self.password.errors.append("")
            return False
        if not self.user.check_password(self.password.data):
            self.result = LoginResult.INVALID_PASSWORD
            self.email.errors.append(_("Invalid email or password"))
            self.password.errors.append("")
            return False
        if self.user.is_banned():
            self.result = LoginResult.BANNED

            ban = self.user.get_ban()
            ban_len = _(f"until {format_date(ban.until)}")
            if ban.permanent:
                ban_len = _("forever")
            self.email.errors.append(
                _(f"You were banned for {ban_len}: {ban.reason}"))
            return False
        if not self.user.active:
            self.result = LoginResult.NOT_ACTIVE
            self.email.errors.append(_("This account is not active."))
            return False
        return True


class RegisterForm(FlaskForm):
    """Register form handling."""
    first_name = StringField(_("First name"),
                             [InputRequired(),
                              Length(min=2, max=MAX_FIRST_NAME_LEN)])
    last_name = StringField(_("Last name"),
                            [InputRequired(),
                             Length(min=2, max=MAX_LAST_NAME_LEN)])
    email = EmailField(_("Email address"),
                       [InputRequired(), Email(), Length(max=MAX_EMAIL_LEN)])
    password = PasswordField(_("Password"),
                             [InputRequired(), password_rules()])
    confirm = PasswordField(_("Repeat password"),
                            [InputRequired(),
                             EqualTo('password',
                                     message=_("Passwords must match"))])
    rules_agree = BooleanField()
    submit = SubmitField(_("Register"))

    def validate_email(self, field):
        """Checks if the email is not in the user database yet."""
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError(_("Email already used by existing user"))

    def validate_rules_agree(self, field):
        """Forces user to agree with the page rules."""
        if not field.data:
            raise ValidationError(_("You must agree with page rules"))


class ChangePasswordForm(FlaskForm):
    """Change password form."""
    old_password = PasswordField(_("Current password"), [InputRequired()])
    password = PasswordField(_("New password"),
                             [InputRequired(), password_rules()])
    confirm = PasswordField(_("Repeat new password"),
                            [InputRequired(),
                             EqualTo('password',
                                     message=_("Passwords must match"))])
    submit = SubmitField(_("Change password"))

    def validate_old_password(self, field):
        """Checks if the entered current password matches the one in DB."""
        if not current_user.check_password(field.data):
            raise ValidationError(_("Invalid password"))


class EditProfileForm(FlaskForm):
    """Edit profile form."""
    about = TextAreaField(_('About'),
                          [InputRequired(), Length(max=MAX_ABOUT_LEN)])
    photo = FileField(_('Profile photo'), [image_file()])
    submit = SubmitField(_('Save'))


class BanForm(FlaskForm):
    """Ban user form."""
    reason = TextAreaField(_('Ban reason'),
                           [InputRequired(),
                            Length(min=10, max=MAX_REASON_LEN)])
    days = IntegerField(_('Ban length [days]'),
                        [InputRequired(), NumberRange(min=0, max=360)])
    permanent = RadioField(_('Ban permanently'),
                           choices=[(0, 'No'), (1, 'Yes')], default=0)
    submit = SubmitField(_('Ban!'))


class InviteForm(FlaskForm):
    """New user invitation form."""
    name = StringField(_('Name of the person'),
                       [InputRequired(),
                        Length(max=(MAX_LAST_NAME_LEN+MAX_FIRST_NAME_LEN+1))])
    email = EmailField(_('Email address'),
                       [InputRequired(), Email(), Length(max=MAX_EMAIL_LEN)])
    reason = TextAreaField(_('Invitation reason'),
                           [InputRequired(), Length(max=MAX_REASON_LEN)])
    submit = SubmitField(_('Send Invitation'))

    def validate_email(self, field):
        """Checks if the email is not in the user database yet."""
        if User.query.filter_by(email=field.data).count():
            raise ValidationError(_("Email already used by existing user"))
        if Invitation.query.filter_by(email=field.data).count():
            raise ValidationError(_("Email already used used in invitation"))

""" Forms for user related pages. """
from flask_login import current_user
from flask_babel import format_date
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, RadioField, \
    ValidationError, SubmitField, TextAreaField, SelectField, EmailField, \
    IntegerField
from wtforms.validators import InputRequired, EqualTo, Email, Length, \
    NumberRange

from app.utils.validators import password_rules, image_file
from app.models import user as constants
from app.models.user import UserRole, LoginResult, User, Invitation


class LoginForm(FlaskForm):
    """Login form handling.

    Attributes:
        user: User that was logged in
        result: Result of the login attempt
    """
    email = EmailField(_("Email address"),
                       [InputRequired(), Email(),
                        Length(max=constants.MAX_EMAIL_LEN)])
    password = PasswordField(_("Password"), [InputRequired()])
    remember_me = BooleanField(_("Remember me"))
    submit = SubmitField(_("Log In"))
    user = None
    result = LoginResult.SUCCESS

    def validate(self, extra_validators=None) -> bool:
        """Validates the email and password against the user database."""
        if not super().validate(extra_validators):
            return False

        self.user = User.get_by_email(self.email.data)
        self.result = LoginResult.SUCCESS
        ban = self.user.get_ban() if self.user else None

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
        if ban:
            self.result = LoginResult.BANNED
            msg = _("You are banned until %(until)s: %(reason)s",
                    until=format_date(ban.until), reason=ban.reason)

            if ban.permanent:
                msg = _("You were banned permanently: %(reason)s",
                        reason=ban.reason)
            self.email.errors.append(msg)
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
                              Length(min=2, max=constants.MAX_FIRST_NAME_LEN)])
    last_name = StringField(_("Last name"),
                            [InputRequired(),
                             Length(min=2, max=constants.MAX_LAST_NAME_LEN)])
    email = EmailField(_("Email address"),
                       [InputRequired(), Email(),
                        Length(max=constants.MAX_EMAIL_LEN)])
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
        user = User.get_by_email(field.data)
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


class ChangeEmailForm(FlaskForm):
    """Change email form."""
    email = EmailField(_("New email address"),
                       [InputRequired(), Email(),
                        Length(max=constants.MAX_EMAIL_LEN)])
    submit = SubmitField(_("Confirm"))

    def validate_email(self, field):
        """Checks if the email is not in the user database yet."""
        user = User.get_by_email(field.data)
        if user:
            raise ValidationError(_("Email already used by existing user"))


class EditProfileForm(FlaskForm):
    """Edit profile form."""
    about = TextAreaField(_("About"),
                          [InputRequired(),
                           Length(max=constants.MAX_ABOUT_LEN)])
    photo = FileField(_("Profile photo"), [image_file()])
    submit = SubmitField(_("Save"))


class BanForm(FlaskForm):
    """Ban user form."""
    reason = TextAreaField(_("Ban reason"),
                           [InputRequired(),
                            Length(min=10, max=constants.MAX_REASON_LEN)])
    days = IntegerField(_("Ban length [days]"),
                        [InputRequired(), NumberRange(min=0, max=360)],
                        default=30)
    permanent = RadioField(_("Ban permanently"),
                           choices=[(0, _("No")), (1, _("Yes"))], default=0)
    submit = SubmitField(_("Ban!"))


class InviteForm(FlaskForm):
    """New user invitation form."""
    name = StringField(_("Name of the person"),
                       [InputRequired(),
                        Length(max=(constants.MAX_LAST_NAME_LEN +
                                    constants.MAX_FIRST_NAME_LEN + 1))])
    email = EmailField(_("Email address"),
                       [InputRequired(), Email(),
                        Length(max=constants.MAX_EMAIL_LEN)])
    reason = TextAreaField(_("Invitation reason"),
                           [InputRequired(),
                            Length(max=constants.MAX_REASON_LEN)])
    submit = SubmitField(_("Send Invitation"))

    def validate_email(self, field):
        """Checks if the email is not in the user database yet."""
        if User.get_by_email(field.data):
            raise ValidationError(_("Email already used by existing user"))
        if Invitation.get_by_email(field.data):
            raise ValidationError(_("This email was already invited"))


class RoleForm(FlaskForm):
    """Change user role form."""
    role = SelectField(_("Role"), [InputRequired()],
                       coerce=UserRole.coerce,
                       choices=UserRole.choices([UserRole.ROOT]))
    submit = SubmitField(_("Set Role"))


class ForgottenPasswordForm(FlaskForm):
    """Request reset users password form."""
    email = EmailField(_("Email address"), [InputRequired(), Email()])
    submit = SubmitField(_("Request password reset"))

    def validate_email(self, field):
        """Check if the user exists."""
        if not User.get_by_email(field.data):
            raise ValidationError(_("User does not exist."))


class ResetPasswordForm(FlaskForm):
    """Reset user password form."""
    password = PasswordField(_("New password"),
                             [InputRequired(), password_rules()])
    confirm = PasswordField(_("Repeat new password"),
                            [InputRequired(),
                             EqualTo('password',
                                     message=_("Passwords must match"))])
    submit = SubmitField(_("Change password"))

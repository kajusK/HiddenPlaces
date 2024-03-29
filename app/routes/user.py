"""Routing for user pages."""
from typing import Optional
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, abort, url_for, \
    redirect
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from is_safe_url import is_safe_url

from app.utils.utils import redirect_return
from app.utils.email import send_email
from app.database import db
from app.decorators import public, moderator, admin
from app.models.location import Location, LocationType
from app.models.upload import save_uploaded_file, delete_file
from app.models.page import Page, PageType
from app.models import event
from app.models.event import EventLog
from app.models.user import User, Invitation, LoginLog, Ban, InvitationState, \
    UserRole
from app.forms.user import LoginForm, RegisterForm, ChangePasswordForm, \
    EditProfileForm, InviteForm, BanForm, ResetPasswordForm, RoleForm, \
    ForgottenPasswordForm, ChangeEmailForm


blueprint = Blueprint('user', __name__, url_prefix="/user")


def _send_password_reset(user: User) -> None:
    """Sends email with password reset info.

    Args:
        user: User that requested the password reset
    """
    token = user.get_reset_token()
    send_email([user.email], _("Password reset requested"),
               text_body=render_template('email/password_reset.txt',
                                         token=token, user=user),
               html_body=render_template('email/password_reset.html',
                                         token=token, user=user))


def _send_email_change(user: User, email: str) -> None:
    """Sends email with email change link.

    Args:
        user: User that requested the email change
        email: The new email user requested
    """
    token = user.get_email_change_token(email)
    send_email([email], _("Email change requested"),
               text_body=render_template('email/email_change.txt',
                                         token=token, user=user, email=email),
               html_body=render_template('email/email_change.html',
                                         token=token, user=user, email=email))

    send_email([user.email], _("Email change requested"),
               text_body=render_template('email/email_change_warning.txt',
                                         token=token, user=user, email=email),
               html_body=render_template('email/email_change_warning.html',
                                         token=token, user=user, email=email))


def send_invitation(invitation: Invitation) -> None:
    """Sends email with invitation link.

    Args:
        invitation: Invitation tied to this email
    """
    token = invitation.get_token()
    send_email([invitation.email], _("You were invited to join us"),
               text_body=render_template('email/invite.txt',
                                         invitation=invitation, token=token),
               html_body=render_template('email/invite.html',
                                         invitation=invitation, token=token))


@blueprint.route('/login', methods=['GET', 'POST'])
@public
def login():
    """Renders login page."""
    next_hop = request.args.get('next')
    if next_hop and not is_safe_url(next_hop, request.host_url):
        next_hop = None

    if current_user.is_authenticated:
        return redirect(next_hop or url_for('page.index'))

    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember_me.data)
        LoginLog.create(form.email.data, form.result, form.user)
        db.session.commit()

        flash(_("You were logged in"), 'success')
        return redirect(next_hop or url_for('page.index'))

    if request.method == 'POST':
        LoginLog.create(form.email.data, form.result, form.user)
        db.session.commit()

    return render_template('user/login.html', form=form)


@blueprint.route('/register/<string:token>',
                 methods=['GET', 'POST'])
@public
def register(token: str):
    """Register a new user.

    Invitation based system, the user has to be invited first.

    Args:
        token: Invitation token
    """
    invitation = Invitation.check_token(token)
    if not invitation:
        flash(_("The invitation is no longer valid."), 'danger')
        return redirect(url_for('user.login'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User.create(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data
        )
        invitation.user = user
        invitation.state = InvitationState.REGISTERED
        EventLog.log(user, event.RegisterEvent())
        db.session.commit()
        flash(_("You were registered, you may now log-in"), 'success')
        return redirect(url_for('user.login'))

    rules = Page.get(PageType.RULES)
    return render_template('user/register.html', form=form, rules=rules)


@blueprint.route('/forgotten_password', methods=['GET', 'POST'])
@public
def forgotten_password():
    """Renders forgotten password form."""
    form = ForgottenPasswordForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        EventLog.log(user, event.PasswordResetRequestEvent())
        db.session.commit()
        _send_password_reset(user)
        flash(_("Password reset request was requested, check your email"),
              'warning')
        return redirect_return()
    return render_template('user/forgotten_password.html', form=form)


@blueprint.route('/password_reset/<string:token>', methods=['GET', 'POST'])
@public
def reset_password(token: str):
    """Renders reset password form.

    Args:
        token: Token tied to password reset request
    """
    user = User.check_reset_token(token)
    if not user:
        flash(_("The password reset request is no longer valid."), 'danger')
        return redirect(url_for('user.login'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        EventLog.log(user, event.PasswordResetEvent())
        db.session.commit()
        flash(_("Your password was changed, you may now log in"), 'warning')
        return redirect(url_for('user.login'))
    return render_template('user/reset_password.html', form=form)


@blueprint.route('/change_email/<string:token>', methods=['GET', 'POST'])
@public
def change_email_token(token: str):
    """Renders user email changed confirmation

    Args:
        token: Token tied to email change request
    """
    result = User.check_email_token(token)
    if not result:
        flash(_("The email change request is no longer valid."), 'danger')
        return redirect(url_for('user.login'))

    user, email = result

    user.email = email
    EventLog.log(user, event.EmailChangedEvent(email))
    db.session.commit()
    logout_user()

    flash(_("Your email was changed, you need to log in again."), 'warning')
    return redirect(url_for('user.login'))


@blueprint.route('/logout')
def logout():
    """Logout user and redirect to login page again."""
    db.session.commit()
    logout_user()
    flash(_("You were logged out."), 'info')
    return redirect(url_for('user.login'))


@blueprint.route('/profile')
@blueprint.route('/<int:user_id>')
def profile(user_id: Optional[int] = None):
    """Shows user profile.

    Args:
        user_id: ID of the user we want to display
    """
    user = current_user if not user_id else User.get_by_id(user_id)
    if not user:
        abort(404)

    locations = Location.get_by_owner(LocationType.ALL, user).count()
    visits = Location.get_visits(LocationType.ALL, user).count()
    return render_template('user/profile.html', user=user, locations=locations,
                           visits=visits, user_id=user.id)


@blueprint.route('/edit', methods=['GET', 'POST'])
def edit():
    """Edit user profile."""
    form = EditProfileForm()
    if request.method == 'GET':
        form.about.data = current_user.about
    elif form.validate_on_submit():
        # pylint: disable=assigning-non-slot
        current_user.about = form.about.data
        if form.photo.data:
            delete_file(current_user.photo_path)
            current_user.photo_path = save_uploaded_file(
                form.photo.data, 'user', str(current_user.id), reduce=True)

        db.session.commit()
        flash(_("Your profile changes were saved"), 'success')
        return redirect_return()
    return render_template('user/edit.html', form=form, user=current_user)


@blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Change user password (by himself)."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        EventLog.log(current_user, event.PasswordChangeEvent())
        db.session.commit()
        flash(_("Your password was changed"), 'warning')
        return redirect_return()
    return render_template('user/password.html', form=form)


@blueprint.route('/change_email', methods=['GET', 'POST'])
def change_email():
    """Change user email (by himself)."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        user = current_user
        email = form.email.data
        EventLog.log(user, event.EmailChangeRequestEvent(email))
        db.session.commit()
        _send_email_change(user, email)
        flash(_("Check you new email for confirmation link"), 'warning')
        return redirect_return()
    return render_template('user/email.html', form=form)


@blueprint.route('/ban/<int:user_id>', methods=['GET', 'POST'])
@moderator
def ban(user_id: int):
    """Ban selected user

    Args:
        user_id: ID of the user to be banned
    """
    banned_user = User.get_by_id(user_id)
    if not banned_user:
        abort(404)
    if banned_user.role == UserRole.ROOT or banned_user.id == 0:
        flash(_("Superuser cannot be banned"), 'danger')
        return redirect_return()

    form = BanForm()
    if form.validate_on_submit():
        ban_entry = Ban.create(
            creator=current_user,
            user=banned_user,
            reason=form.reason.data,
            permanent=bool(int(form.permanent.data)),
            until=datetime.utcnow() + timedelta(days=form.days.data)
        )
        EventLog.log(current_user, event.BanEvent(ban_entry))
        db.session.commit()
        flash(_("User %(user)s was banned", user=banned_user), 'warning')
        return redirect_return()
    return render_template('user/ban.html', form=form, user=banned_user)


@blueprint.route('/invite', methods=['GET', 'POST'])
@moderator
def invite():
    """Invite a new user."""
    form = InviteForm()
    if form.validate_on_submit():
        invitation = Invitation.create(
            email=form.email.data,
            name=form.name.data,
            reason=form.reason.data,
            invited_by=current_user,
        )
        if current_user.role <= UserRole.ADMIN:
            invitation.state = InvitationState.APPROVED
            invitation.approved_by = current_user

        EventLog.log(current_user, event.InviteEvent(invitation))
        db.session.commit()

        if invitation.state == InvitationState.APPROVED:
            send_invitation(invitation)
            flash(_("%(name)s invited", name=form.name.data), 'success')
        else:
            flash(_("Invitation created, waiting for approval by admins"),
                  'warning')
        return redirect(url_for('user.invite'))
    return render_template('user/invite.html', form=form)


@blueprint.route('/role/<int:user_id>', methods=['GET', 'POST'])
@admin
def role(user_id: int):
    """Changes user role.

    Args:
        user_id: ID of the user to change role for
    """
    user = User.get_by_id(user_id)
    if not user:
        abort(404)
    if user.id == 0:
        flash(_("You can't change root's role!"), 'danger')
        return redirect_return()
    if user == current_user:
        flash(_("You can't change your own role!"), 'danger')
        return redirect_return()

    form = RoleForm()
    if request.method == 'GET':
        form.role.data = user.role
    elif form.validate_on_submit():
        EventLog.log(current_user, event.RoleChangeEvent(
            user, form.role.data))
        user.role = form.role.data
        db.session.commit()
        flash(_("Changed role of %(user)s to %(role)s", user=user,
                role=user.role), 'warning')
        return redirect_return()
    return render_template('user/role.html', form=form, user=user)

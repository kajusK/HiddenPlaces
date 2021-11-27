"""Routing for user module."""
from typing import Optional
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, abort, url_for, \
    redirect
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from is_safe_url import is_safe_url

from app.utils import redirect_return
from app.database import db
from app.decorators import public, moderator, admin
from app.location.models import Location
from app.location.constants import LocationType
from app.upload.models import save_uploaded_file
from app.page.models import Page
from app.page.constants import PageType
from app.user.models import User, Invitation, LoginLog, Ban
from app.user.forms import LoginForm, RegisterForm, ChangePasswordForm, \
    EditProfileForm, InviteForm, BanForm, ResetPasswordForm, RoleForm
from app.user.constants import InvitationState, UserRole

blueprint = Blueprint('user', __name__, url_prefix="/user")


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


@blueprint.route('/register/<int:invite_id>/<string:uuid>',
                 methods=['GET', 'POST'])
@public
def register(invite_id: int, uuid: str):
    """Register a new user.

    Invitation based system, the user has to be invited first.

    Args:
        invite_id: ID of the invitation
        key: Key that must match the one in the invitation
    """
    invitation = Invitation.get_by_id(invite_id)
    if not invitation:
        abort(404)
    if not invitation.is_valid() or str(invitation.uuid) != uuid:
        flash(_("The invitation is not valid."), 'danger')
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
        db.session.commit()
        flash(_("You were registered, you may now log-in"), 'success')
        return redirect(url_for('user.login'))

    rules = Page.get(PageType.RULES)
    return render_template('user/register.html', form=form, rules=rules)


@blueprint.route('/reset_password', methods=['GET', 'POST'])
@public
def reset_password():
    """Reset user password."""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # TODO - send email with reset link, generate hash for pwd reset
        flash(_("Password reset was requested, check your email"), 'warning')
        return redirect_return()
    return render_template('user/reset_password.html', form=form)


@blueprint.route('/logout')
def logout():
    """Logout user and redirect to login page again."""
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
            current_user.photo_path = save_uploaded_file(
                form.photo.data, 'user', str(current_user.id))

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
        db.session.commit()
        flash(_("Your password was changed"), 'warning')
        return redirect_return()
    return render_template('user/password.html', form=form)


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
        Ban.create(
            creator=current_user,
            user=banned_user,
            reason=form.reason.data,
            permanent=bool(int(form.permanent.data)),
            until=datetime.utcnow() + timedelta(days=form.days.data)
        )
        db.session.commit()
        flash(_("User %(first)s %(last)s was banned",
                first=banned_user.first_name, last=banned_user.last_name),
              'warning')
        return redirect_return()
    return render_template('user/ban.html', form=form, user=banned_user)


@blueprint.route('/invite', methods=['GET', 'POST'])
@moderator
def invite():
    """Invite a new user."""
    form = InviteForm()
    if form.validate_on_submit():
        initial_state = InvitationState.WAITING
        if current_user.role <= UserRole.ADMIN:
            initial_state = InvitationState.APPROVED

        Invitation.create(
            email=form.email.data,
            name=form.name.data,
            reason=form.reason.data,
            valid_until=datetime.utcnow() + timedelta(days=120),
            invited_by=current_user,
            state=initial_state
        )
        db.session.commit()
        flash(_("%(name)s invited", name=form.name.data), 'success')
        # TODO send email
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
        user.role = form.role.data
        db.session.commit()
        flash(_("Changed role of %(first)s %(last)s to %(role)s",
                first=user.first_name, last=user.last_name, role=user.role),
              'warning')
        return redirect_return()
    return render_template('user/role.html', form=form, user=user)

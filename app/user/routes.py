"""Routing for /user pages."""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, abort, url_for, \
    redirect
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from is_safe_url import is_safe_url

from app.user.models import User, Invitation, LoginLog, Ban
from app.user.forms import LoginForm, RegisterForm, ChangePasswordForm, \
    EditProfileForm, InviteForm, BanForm
from app.user.constants import InvitationState, UserRole
from app.location.models import Location, Visit
from app.database import db
from app.page.models import Page
from app.decorators import public, moderator, admin

blueprint = Blueprint('user', __name__, url_prefix="/user")


@blueprint.route('/login', methods=['GET', 'POST'])
@public
def login():
    """Login page handling."""
    next_hop = request.args.get('next')
    if next_hop and not is_safe_url(next_hop, request.host_url):
        next_hop = None

    if current_user.is_authenticated:
        return redirect(next_hop or url_for('page.index'))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember_me.data)
        flash(_("You were logged in"), 'success')
        LoginLog.create_log(form.email.data, form.result, form.user)
        db.session.commit()
        return redirect(next_hop or url_for('page.index'))

    if request.method == 'POST':
        LoginLog.create_log(form.email.data, form.result, form.user)
        db.session.commit()
    return render_template('user/login.html', form=form)


@blueprint.route('/register/<int:invite_id>/<string:key>',
                 methods=['GET', 'POST'])
@public
def register(invite_id, key):
    """Register a new user.

    Invitation based system, the user has to be invited first.

    Args:
        invite_id: ID of the invitation
        key: Key that must match the one in the invitation
    """
    invitation = Invitation.get_by_id(invite_id)
    if not invitation:
        return abort(404, _("Invitation not found"))
    if not invitation.is_valid() or invitation.key != key:
        flash(_("The invitation is not valid."), 'danger')
        return redirect(url_for('user.login'))

    form = RegisterForm(request.form)
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

    rules = Page.get_page_rules()
    return render_template('user/register.html', form=form, rules=rules)


@blueprint.route('/logout')
def logout():
    """Logout user and redirect to login page again."""
    logout_user()
    flash(_("You were logged out."), 'info')
    return redirect(url_for('user.login'))


@blueprint.route('/profile')
@blueprint.route('/<int:user_id>')
def profile(user_id: int = None):
    """Shows user profile.

    Args:
        user_id: ID of the user we want to display
    """
    user = current_user if not user_id else User.get_by_id(user_id)
    if not user:
        return abort(404, _("Required user does not exist"))
    locations = Location.get_by_owner(user)
    visits = Visit.get_by_user(user)
    return render_template('user/profile.html', user=user, locations=locations,
                           visits=visits, user_id=user.id)


@blueprint.route('/edit', methods=['GET', 'POST'])
def edit():
    """Edit user profile."""
    form = EditProfileForm(request.form)
    if form.validate_on_submit():
        # pylint: disable=assigning-non-slot
        current_user.about = form.about.data
        # TODO photo
        db.session.commit()
        flash(_("Your profile changes were saved"), 'success')
        return redirect(url_for('user.profile'))
    if request.method == 'GET':
        form.about.data = current_user.about
    return render_template('user/edit.html', form=form)


@blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Change user password (by himself)."""
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash(_("Your password was changed"), 'warning')
        return redirect(url_for('user.profile'))
    return render_template('user/password.html', form=form)


@blueprint.route('/reset_password', methods=['GET', 'POST'])
@public
def reset_password():
    """Reset user password."""
    # TODO
    pass


@blueprint.route('/ban/<int:user_id>', methods=['GET', 'POST'])
@moderator
def ban(user_id: int):
    """Ban selected user

    Args:
        user_id: ID of the user to be banned
    """
    banned_user = User.get_by_id(user_id)
    if not banned_user:
        return abort(404, _("Required user does not exist"))
    if banned_user.role == UserRole.ROOT or banned_user.id == 0:
        flash(_("Superuser cannot be banned"), 'danger')
        return redirect(url_for('user.profile', user_id=banned_user.id))

    form = BanForm(request.form)
    if form.validate_on_submit():
        Ban.create(
            creator=current_user,
            user=banned_user,
            reason=form.reason.data,
            permanent=bool(int(form.permanent.data)),
            until=datetime.utcnow() + timedelta(days=form.days.data)
        )
        banned_user.active = False
        db.session.commit()
        flash(_(f"User {banned_user.first_name} {banned_user.last_name}"
                " was banned"), 'warning')
        return redirect(url_for('user.profile', user_id=banned_user.id))
    return render_template('user/ban.html', form=form, user=current_user)


@blueprint.route('/invite', methods=['GET', 'POST'])
@moderator
def invite():
    """Invite new user."""
    form = InviteForm(request.form)
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
        flash(_(f"User {form.name.data} invited"), 'success')
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
        return abort(404, _("Required user does not exist"))

    # TODO
    return render_template('user/role.html')

"""Admin interface."""
from datetime import datetime, timedelta
from typing import Optional
from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import current_user
from flask_babel import _
from sqlalchemy import or_, desc, sql

from app.user.models import User, Invitation, LoginLog
from app.user.constants import InvitationState, UserRole, LoginResult
from app.location.models import Location
from app.decorators import moderator, admin
from app.database import db


blueprint = Blueprint('admin', __name__, url_prefix="/admin")


@blueprint.route('/locations')
@moderator
def locations():
    """Lists existing locations with admin tasks. """
    locs = Location.query.all()
    return render_template("admin/locations.html", locations=locs)


@blueprint.route('/users')
@blueprint.route('/users/<string:role>')
@admin
def users(role: str = 'users'):
    """Lists existing users.

    Args:
        role: Select specific users (admins, moderators, bans, users)
    """
    if role == 'admins':
        data = User.query.filter(or_(
            User.role == UserRole.ADMIN, User.role == UserRole.ROOT))
        title = _("Admins")
    elif role == 'moderators':
        data = User.query.filter_by(role=UserRole.ADMIN)
        title = _("Moderators")
    elif role == 'bans':
        data = User.query.filter_by(active=False)
        title = _("Banned users")
    else:
        data = User.query.all()
        title = _("Users")

    users_count = User.query.count()
    admins_count = User.query.filter(or_(
        User.role == UserRole.ADMIN, User.role == UserRole.ROOT)).count()
    moderators_count = User.query.filter_by(role=UserRole.MODERATOR).count()
    bans_count = User.query.filter_by(active=False).count()

    return render_template("admin/users.html", users=data, title=title,
                           users_count=users_count, admins_count=admins_count,
                           moderators_count=moderators_count,
                           bans_count=bans_count)


@blueprint.route('/invitations')
@blueprint.route('/invitations/<string:state>')
@admin
def invitations(state: Optional[str] = None):
    """Lists invitations

    Args:
        state: State of the invitation (waiting, approved, denied, registered)
    """
    if state == 'waiting':
        data = Invitation.query.filter_by(state=InvitationState.WAITING)
        title = _("Waiting for approval")
    elif state == 'approved':
        data = Invitation.query.filter_by(
            state=InvitationState.APPROVED)
        title = _("Approved invitations")
    elif state == 'denied':
        data = Invitation.query.filter_by(
            state=InvitationState.DENIED)
        title = _("Denied invitations")
    elif state == 'registered':
        data = Invitation.query.filter_by(
            state=InvitationState.REGISTERED)
        title = _("Registered users")
    else:
        data = Invitation.query.all()
        title = _("Invitations")

    waiting = Invitation.query.filter_by(state=InvitationState.WAITING).count()
    approved = Invitation.query.filter_by(
        state=InvitationState.APPROVED).count()
    denied = Invitation.query.filter_by(state=InvitationState.DENIED).count()
    registered = Invitation.query.filter_by(
        state=InvitationState.REGISTERED).count()

    return render_template("admin/invitations.html", invitations=data,
                           waiting=waiting, approved=approved, denied=denied,
                           registered=registered, title=title)


@blueprint.route('/settings')
@admin
def settings():
    """Shows system settings."""
    return render_template("admin/settings.html")


@blueprint.route('/logins')
@admin
def logins():
    """Shows log of login attempts."""
    data = LoginLog.query.order_by(desc(LoginLog.id))
    failed = LoginLog.query.filter(
        LoginLog.result != LoginResult.SUCCESS).count()
    unique = db.session.query(
        sql.func.count(sql.func.distinct(LoginLog.ip))).count()
    per_day = LoginLog.query.filter(
        LoginLog.timestamp >= datetime.utcnow() - timedelta(days=1)).count()
    per_month = LoginLog.query.filter(
        LoginLog.timestamp >= datetime.utcnow() - timedelta(days=30)).count()

    return render_template("admin/logins.html", logins=data, failed=failed,
                           unique=unique, per_day=per_day, per_month=per_month)


@blueprint.route('invitations/approve/<int:invite_id>')
@admin
def invite_approve(invite_id: int):
    """Approves the user invitation

    Args:
        invite_id: ID of the invitation
    """
    invite = Invitation.get_by_id(invite_id)
    if not invite:
        return abort(404, _("Invitation not found."))
    if invite.state in (InvitationState.WAITING, InvitationState.DENIED):
        invite.state = InvitationState.APPROVED
        invite.approved_by = current_user
        db.session.commit()
    return redirect(url_for('admin.invitations'))


@blueprint.route('invitation/deny/<int:invite_id>')
@admin
def invite_deny(invite_id: int):
    """Denies the user invitation

    Args:
        invite_id: ID of the invitation
    """
    invite = Invitation.get_by_id(invite_id)
    if not invite:
        return abort(404, _("Invitation not found."))
    if invite.state in (InvitationState.WAITING, InvitationState.APPROVED):
        invite.state = InvitationState.DENIED
        invite.approved_by = current_user
        db.session.commit()
    return redirect(url_for('admin.invitations'))

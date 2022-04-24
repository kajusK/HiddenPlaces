"""Admin interface."""
from datetime import datetime
from typing import Optional
from flask import Blueprint, render_template, abort, flash, url_for, redirect
from flask import current_app as app
from flask_login import current_user
from flask_babel import _

from app.database import db
from app.utils.utils import redirect_return
from app.utils.email import send_email
from app.utils.pagination import Pagination
from app.decorators import moderator, admin
from app.models.location import Location, LocationType
from app.models.user import User, Invitation, LoginLog, InvitationState
from app.models import event
from app.models.event import EventLog
from app.forms.admin import MessageForm
from app.routes.user import send_invitation
from app.routes.message import send_message


blueprint = Blueprint('admin', __name__, url_prefix='/admin')


def _send_mail_to_all(subject: str, message: str) -> None:
    """Sends email to all users.

    Args:
        subject: Subject of the message
        message: Message to be sent
    """
    users = User.get()
    recipients = []
    for user in users:
        recipients.append(user.email)

    send_email(recipients, subject, message)


@blueprint.route('/locations')
@blueprint.route('/locations/<int:page>')
@blueprint.route('/locations/<string:location>')
@blueprint.route('/locations/<string:location>/<int:page>')
@moderator
def locations(page: int = 1, location: Optional[str] = None):
    """Lists existing locations.

    Args:
        page: Page number for results pagination
        location: Location type (urbex, underground, private)
    """
    if location is None:
        query = Location.get(LocationType.ALL)
        title = _("All locations")
    elif location == 'urbex':
        query = Location.get(LocationType.URBEX)
        title = _("Urbex locations")
    elif location == 'underground':
        query = Location.get(LocationType.UNDERGROUND)
        title = _("Underground locations")
    elif location == 'private':
        query = Location.get_unpublished(LocationType.ALL)
        title = _("Private locations")
    else:
        abort(404)

    query = query.paginate(page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'admin.locations',
                            location=location)

    locations_count = Location.get(LocationType.ALL).count()
    urbex_count = Location.get(LocationType.URBEX).count()
    underground_count = Location.get(LocationType.UNDERGROUND).count()
    private_count = Location.get_unpublished(LocationType.ALL).count()

    current_user.location_check_ts = datetime.utcnow()
    db.session.commit()

    return render_template('admin/locations.html', locations=query.items,
                           title=title, locations_count=locations_count,
                           underground_count=underground_count,
                           urbex_count=urbex_count,
                           private_count=private_count, pagination=pagination)


@blueprint.route('/users')
@blueprint.route('/users/<int:page>')
@blueprint.route('/users/<string:role>')
@blueprint.route('/users/<string:role>/<int:page>')
@admin
def users(page: int = 1, role: Optional[str] = None):
    """Lists existing users.

    Args:
        page: Page number for results pagination
        role: Select specific users (admins, moderators, bans)
    """
    if role is None:
        query = User.get()
        title = _("Users")
    elif role == 'admins':
        query = User.get_admins()
        title = _("Admins")
    elif role == 'moderators':
        query = User.get_moderators()
        title = _("Moderators")
    elif role == 'bans':
        query = User.get_banned()
        title = _("Banned users")
    else:
        abort(404)

    query = query.paginate(page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'admin.users', role=role)

    users_count = User.get().count()
    admins_count = User.get_admins().count()
    moderators_count = User.get_moderators().count()
    bans_count = User.get_banned().count()

    return render_template('admin/users.html', users=query.items, title=title,
                           users_count=users_count, admins_count=admins_count,
                           moderators_count=moderators_count,
                           bans_count=bans_count, pagination=pagination)


@blueprint.route('/invitations')
@blueprint.route('/invitations/<int:page>')
@blueprint.route('/invitations/<string:state>')
@blueprint.route('/invitations/<string:state>/<int:page>')
@admin
def invitations(page: int = 1, state: Optional[str] = None):
    """Lists invitations

    Args:
        page: Page number for results pagination
        state: State of the invitation (waiting, approved, denied, registered)
    """
    if state is None:
        query = Invitation.get()
        title = _("Invitations")
    elif state == 'waiting':
        query = Invitation.get_by_state(InvitationState.WAITING)
        title = _("Waiting for approval")
    elif state == 'approved':
        query = Invitation.get_by_state(InvitationState.APPROVED)
        title = _("Approved invitations")
    elif state == 'denied':
        query = Invitation.get_by_state(InvitationState.DENIED)
        title = _("Denied invitations")
    elif state == 'registered':
        query = Invitation.get_by_state(InvitationState.REGISTERED)
        title = _("Registered users")
    else:
        abort(404)

    query = query.paginate(page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'admin.invitations',
                            state=state)

    waiting = Invitation.get_by_state(InvitationState.WAITING).count()
    approved = Invitation.get_by_state(InvitationState.APPROVED).count()
    denied = Invitation.get_by_state(InvitationState.DENIED).count()
    registered = Invitation.get_by_state(InvitationState.REGISTERED).count()

    return render_template('admin/invitations.html', invitations=query.items,
                           waiting=waiting, approved=approved, denied=denied,
                           registered=registered, title=title,
                           pagination=pagination)


@blueprint.route('/logins')
@blueprint.route('/logins/<int:page>')
@blueprint.route('/logins/<string:login_type>')
@blueprint.route('/logins/<string:login_type>/<int:page>')
@admin
def logins(page: int = 1, login_type: Optional[str] = None):
    """Shows log of login attempts.

    Args:
        page: Page number for results pagination
        login_type: Login type (unique, failed)
    """
    if login_type is None:
        query = LoginLog.get()
        title = _("Logins")
    elif login_type == 'unique':
        query = LoginLog.get_unique()
        title = _("Unique IPs")
    elif login_type == 'failed':
        query = LoginLog.get_failed()
        title = _("Failed logins")
    else:
        abort(404)

    attempts = LoginLog.get().count()
    failed = LoginLog.get_failed().count()
    unique = LoginLog.get_unique().count()
    per_month = LoginLog.get_last_month().count()

    query = query.paginate(page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'admin.logins')

    current_user.login_check_ts = datetime.utcnow()
    db.session.commit()

    return render_template('admin/logins.html', logins=query.items,
                           failed=failed, unique=unique, attempts=attempts,
                           per_month=per_month, pagination=pagination,
                           title=title)


@blueprint.route('invitations/approve/<int:invite_id>')
@admin
def invite_approve(invite_id: int):
    """Approves the user invitation

    Args:
        invite_id: ID of the invitation
    """
    invite = Invitation.get_by_id(invite_id)
    if not invite:
        abort(404)

    if invite.state in (InvitationState.WAITING, InvitationState.DENIED):
        invite.state = InvitationState.APPROVED
        invite.approved_by = current_user
        EventLog.log(current_user, event.ApproveInviteEvent(invite))
        db.session.commit()
        send_invitation(invite)

    return redirect_return()


@blueprint.route('invitation/deny/<int:invite_id>')
@admin
def invite_deny(invite_id: int):
    """Denies the user invitation

    Args:
        invite_id: ID of the invitation
    """
    invite = Invitation.get_by_id(invite_id)
    if not invite:
        abort(404)

    if invite.state in (InvitationState.WAITING, InvitationState.APPROVED):
        invite.state = InvitationState.DENIED
        invite.approved_by = current_user
        EventLog.log(current_user, event.DenyInviteEvent(invite))
        db.session.commit()

    return redirect_return()


@blueprint.route('/events')
@blueprint.route('/events/<int:page>')
@admin
def events(page: int = 1):
    """Shows log of events

    Args:
        page: Page number for results pagination
    """
    query = EventLog.get()

    query = query.paginate(page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'admin.events')

    current_user.event_check_ts = datetime.utcnow()
    db.session.commit()

    return render_template('admin/events.html', events=query.items,
                           pagination=pagination)


@blueprint.route('/message', methods=['GET', 'POST'])
@admin
def message():
    """Render form to send email/message to all users"""
    form = MessageForm()
    if form.validate_on_submit():
        subject = form.subject.data
        message = form.text.data

        if form.email.data:
            _send_mail_to_all(subject, message)
            flash(_("Email to all users was sent"), 'success')
        else:
            users = User.get()
            for user in users:
                send_message(user, subject, message)
            flash(_("Message to all users was sent"), 'success')
        return redirect(url_for('page.index'))

    return render_template('admin/message.html', form=form)

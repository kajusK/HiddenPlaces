"""Email handling for page module."""
from flask import render_template
from flask_babel import _

from app.user.models import User, Invitation
from app.email import send_email


def send_password_reset(user: User) -> None:
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

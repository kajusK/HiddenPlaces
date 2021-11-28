"""Email handling for page module."""
from flask import url_for
from flask_babel import _

from app.user.models import User
from app.email import send_email


def send_message(user: User, subject: str, message: str) -> None:
    """Sends email from contact form.

    Args:
        user: User that is sending the email
        subject: Subject of the message
        message: Message to be sent
    """
    admins = User.get_admins()
    recipients = []
    for admin in admins:
        recipients.append(admin.email)

    send_email(
        recipients, subject,
        _('User %(first)s %(last)s (%(url)s) sent you a message:\n\n%(msg)s',
          first=user.first_name, last=user.last_name,
          url=url_for('user.profile', user_id=user.id, _external=True),
          msg=message))

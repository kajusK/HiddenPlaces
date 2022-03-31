"""Email handling for admin module."""
from app.user.models import User
from app.utils.email import send_email


def send_mail_to_all(subject: str, message: str) -> None:
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

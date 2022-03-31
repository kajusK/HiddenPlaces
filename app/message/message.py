from flask_login import current_user

from app.database import db
from app.user.models import User
from app.message.models import Message, Thread


def send(recipient: User, subject: str, message: str) -> None:
    """Sends message as current user into a new thread.

    Args:
        recipient: User to send message to
        subject: Subject of the message (thread name)
        message: Message body
    """
    thread = Thread.create(
        subject=subject,
        sender=current_user,
        recipient=recipient
    )
    Message.create(
        message=message,
        user=current_user,
        thread=thread,
    )
    db.session.commit()


def reply(thread: Thread, message: str) -> None:
    """Replies to existing thread.

    Args:
        thread: Thread to reply to
        message: Message body
    """
    Message.create(
        message=message,
        user=current_user,
        thread=thread,
    )
    db.session.commit()

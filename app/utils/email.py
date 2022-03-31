"""Simple email framework."""
from typing import List, Optional
from threading import Thread
from flask import Flask, current_app as app
from flask_mail import Message

from app.extensions import mail


def _send_email_async(current_app: Flask, recipients: List[str], subject: str,
                      text_body: str, html_body: Optional[str] = None) -> None:
    """Takes message and sends it over flask-mail.

    Args:
        current_app: Flask app context
        recipients: list of recipients for the email
        subject: Subject of the email
        text_body: Text to be sent
        html_body: HTML variant of the message
    """
    with current_app.app_context():
        with mail.connect() as conn:
            for recipient in recipients:
                msg = Message(subject, recipients=[recipient])
                msg.body = text_body
                msg.html = html_body
                conn.send(msg)


def send_email(recipients: List[str], subject: str, text_body: str,
               html_body: Optional[str] = None) -> None:
    """Send email.

    Args:
        recipients: list of recipients for the email
        subject: Subject of the email
        text_body: Text to be sent
        html_body: HTML variant of the message
    """
    subject = f'[HiddenPlaces] {subject}'
    # Send email from thread for faster response
    # pylint: disable=protected-access
    Thread(target=_send_email_async,
           args=(app._get_current_object(), recipients, subject,  # type:ignore
                 text_body, html_body)).start()

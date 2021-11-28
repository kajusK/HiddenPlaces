"""Simple email framework."""
from typing import List, Optional
from flask import Flask, current_app as app
from flask_mail import Message
from threading import Thread

from app.extensions import mail


def _send_email_async(current_app: Flask, msg: Message):
    """Takes message and sends it over flask-mail.

    Args:
        current_app: Flask app context
        msg: Message to be sent
    """
    with current_app.app_context():
        mail.send(msg)


def send_email(recipients: List[str], subject: str, text_body: str,
               html_body: Optional[str] = None) -> None:
    """Send email.

    Args:
        recipients: list of recipients for the email
        subject: Subject of the email
        text_body: Text to be sent
        html_body: HTML variant of the message
    """
    msg = Message(f'[HiddenPlaces] {subject}', recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # Send email from thread for faster response
    Thread(target=_send_email_async,
           args=(app._get_current_object(), msg)).start()

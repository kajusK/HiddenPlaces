"""Message models."""
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import Query

from app.models.user import User
from app.database import DBItem, db


MAX_SUBJECT_LEN = 32


class Thread(DBItem):
    """Message threads."""
    subject = db.Column(db.String(MAX_SUBJECT_LEN), nullable=False)
    # Timestamp of the last change in th thread
    timestamp = db.Column(db.DateTime(), index=True, nullable=False,
                          default=datetime.utcnow)
    sender_seen = db.Column(db.Boolean(), nullable=False, default=True)
    recipient_seen = db.Column(db.Boolean(), nullable=False, default=False)

    sender_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                          nullable=False)
    recipient_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                             nullable=False)

    sender = db.relationship('User', foreign_keys=sender_id)
    recipient = db.relationship('User', foreign_keys=recipient_id)
    messages = db.relationship('Message', back_populates='thread',
                               order_by='desc(Message.timestamp)')

    @classmethod
    def get(cls, user: User) -> Query:
        """Gets all threads related to user."""
        return cls.query.filter(
            or_(cls.recipient == user, cls.sender == user)).order_by(
                cls.timestamp.desc())

    @classmethod
    def get_unreaded(cls, user: User) -> Query:
        """Gets all threads that were not seen be user yet.

        Args:
            user: User to check messages for
        """
        return cls.query.filter(or_(
            and_(cls.recipient == user, ~cls.recipient_seen),
            and_(cls.sender == user, ~cls.sender_seen)))

    def mark_seen(self, user: User) -> None:
        """Marks thread as seen by given user

        Args:
            user: User that seen the message
        """
        if self.recipient == user:
            self.recipient_seen = True
        if self.sender == user:
            self.sender_seen = True


class Message(DBItem):
    """User messages."""
    message = db.Column(db.Text(), nullable=False)
    timestamp = db.Column(db.DateTime(), index=True, nullable=False,
                          default=datetime.utcnow)

    thread_id = db.Column(db.Integer(), db.ForeignKey('thread.id'),
                          nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                        nullable=False)

    user = db.relationship('User')
    thread = db.relationship('Thread', back_populates='messages')

    @classmethod
    def create(cls, *argc, **argv):
        """Creates a new message and updates the corresponding thread state."""
        msg = super().create(*argc, **argv)

        msg.timestamp = datetime.utcnow()
        msg.thread.timestamp = msg.timestamp
        if msg.thread.recipient == msg.user:
            msg.thread.sender_seen = False
        elif msg.thread.sender == msg.user:
            msg.thread.recipient_seen = False
        return msg

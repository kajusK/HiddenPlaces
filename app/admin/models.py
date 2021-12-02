"""Models for admin module."""
from datetime import datetime
from sqlalchemy.orm import Query

from app.database import DBItem, db
from app.admin.constants import EventSeverity, EventType
from app.admin.events import Event
from app.user.models import User


class EventLog(DBItem):
    """Event log record model."""
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow,
                          nullable=False)
    type = db.Column(db.Enum(EventType), nullable=False)
    severity = db.Column(db.Enum(EventSeverity), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User')

    @classmethod
    def get(cls) -> Query:
        """Gets list of events query."""
        return cls.query.order_by(cls.timestamp.desc())

    @classmethod
    def log(cls, user: User, event: Event) -> None:
        """Creates a log record

        Args:
            user: User that caused the event
            event: Event info
        """
        cls.create(
            user=user,
            type=event.type,
            severity=event.severity,
            text=event.text)

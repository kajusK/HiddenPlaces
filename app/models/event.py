"""Event models."""
from abc import ABC
from datetime import datetime
from sqlalchemy.orm import Query
from flask_babel import lazy_gettext as _

from app.database import DBItem, db, IntEnum
from app.utils.enums import StringEnum
from app.models.page import PageType
from app.models.location import Location, Visit, Category
from app.models.user import User, Invitation, Ban, UserRole


class EventType(StringEnum):
    """Event log record type."""
    OTHER = _("Other")
    CREATE = _("Create")
    MODIFY = _("Modify")
    DELETE = _("Delete")


class EventSeverity(StringEnum):
    """Severity of the event."""
    LOW = _("Low")
    NORMAL = _("Normal")
    HIGH = _("High")
    CRITICAL = _("Critical")


class Event(ABC):
    """Abstract class for event description."""
    text: str = ''
    severity = EventSeverity.NORMAL
    type = EventType.OTHER


#
# User Events
#
# pylint: disable=missing-class-docstring


class InviteEvent(Event):
    def __init__(self, invitation: Invitation):
        self.severity = EventSeverity.HIGH
        self.type = EventType.CREATE
        self.text = f"Invited {invitation.name}"


class ApproveInviteEvent(Event):
    def __init__(self, invitation: Invitation):
        self.severity = EventSeverity.HIGH
        self.type = EventType.MODIFY
        self.text = f"Approved invitation of {invitation.name}"


class DenyInviteEvent(Event):
    def __init__(self, invitation: Invitation):
        self.severity = EventSeverity.NORMAL
        self.type = EventType.MODIFY
        self.text = f"Denied invitation of {invitation.name}"


class RegisterEvent(Event):
    def __init__(self):
        self.severity = EventSeverity.HIGH
        self.type = EventType.CREATE
        self.text = "Registered as a new user"


class PasswordResetRequestEvent(Event):
    def __init__(self):
        self.severity = EventSeverity.NORMAL
        self.type = EventType.OTHER
        self.text = "Requested password reset"


class PasswordResetEvent(Event):
    def __init__(self):
        self.severity = EventSeverity.CRITICAL
        self.type = EventType.MODIFY
        self.text = "Reset password"


class PasswordChangeEvent(Event):
    def __init__(self):
        self.severity = EventSeverity.NORMAL
        self.type = EventType.MODIFY
        self.text = "Changed password"


class RoleChangeEvent(Event):
    def __init__(self, user: User, new: UserRole):
        self.severity = EventSeverity.CRITICAL
        self.type = EventType.MODIFY
        self.text = f"Changed role of '{user}' from {user.role} to {new}"


class BanEvent(Event):
    def __init__(self, ban: Ban):
        self.severity = EventSeverity.HIGH
        self.type = EventType.CREATE
        self.text = f"Banned '{ban.user}': {ban.reason}"


#
# Location Events
#


class AddVisitEvent(Event):
    def __init__(self, visit: Visit):
        self.severity = EventSeverity.LOW
        self.type = EventType.MODIFY
        self.text = f"Logged visit of {visit.location.name}"


class ModifyVisitEvent(Event):
    def __init__(self, visit: Visit):
        self.severity = EventSeverity.LOW
        self.type = EventType.MODIFY
        self.text = f"Modified visit of {visit.location.name}"


class DeleteVisitEvent(Event):
    def __init__(self, visit: Visit):
        self.severity = EventSeverity.NORMAL
        self.type = EventType.DELETE
        self.text = f"Deleted visit of {visit.location.name}"


class CreateLocationEvent(Event):
    def __init__(self, location: Location):
        self.severity = EventSeverity.LOW
        self.type = EventType.CREATE
        self.text = f"Created location {location.name}"


class ModifyLocationEvent(Event):
    def __init__(self, location: Location):
        self.severity = EventSeverity.NORMAL
        self.type = EventType.MODIFY
        self.text = f"Modified location {location.name}"


class DeleteLocationEvent(Event):
    def __init__(self, location: Location):
        self.severity = EventSeverity.HIGH
        self.type = EventType.DELETE
        self.text = f"Deleted location {location.name}"


#
# Category events
#
class CreateCategoryEvent(Event):
    def __init__(self, category: Category):
        self.severity = EventSeverity.LOW
        self.type = EventType.CREATE
        self.text = f"Created category {category.name}"


class ModifyCategoryEvent(Event):
    def __init__(self, category: Category):
        self.severity = EventSeverity.NORMAL
        self.type = EventType.MODIFY
        self.text = f"Modified category {category.name}"


class DeleteCategoryEvent(Event):
    def __init__(self, category: Category):
        self.severity = EventSeverity.HIGH
        self.type = EventType.DELETE
        self.text = f"Deleted category {category.name}"


#
# Page Events
#
class PageEditEvent(Event):
    def __init__(self, page_type: PageType):
        self.severity = EventSeverity.HIGH
        self.type = EventType.MODIFY
        self.text = f"Modified page {page_type}"


#
# Other Events
#
class UnauthorizedEvent(Event):
    def __init__(self, path: str):
        self.severity = EventSeverity.CRITICAL
        self.type = EventType.OTHER
        self.text = f"Unauthorized access of {path}"


class EventLog(DBItem):
    """Event log record model."""
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow,
                          nullable=False)
    type = db.Column(IntEnum(EventType), nullable=False)
    severity = db.Column(IntEnum(EventSeverity), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User')

    @classmethod
    def get(cls) -> Query:
        """Gets list of events query."""
        return cls.query.order_by(cls.timestamp.desc())

    @classmethod
    def get_since(cls, since: datetime) -> Query:
        """Query logs added since date

        Args:
            since: Start date to filter from
        """
        return cls.get().filter(cls.timestamp > since)

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

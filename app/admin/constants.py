"""Constants for admin module."""
from flask_babel import _
from app.utils.enums import StringEnum


class EventType(StringEnum):
    """Event log record type."""
    OTHER = 0, _("Other")
    CREATE = 1, _("Create")
    MODIFY = 2, _("Modify")
    DELETE = 3, _("Delete")


class EventSeverity(StringEnum):
    """Severity of the event."""
    LOW = 0, _("Low")
    NORMAL = 1, _("Normal")
    HIGH = 2, _("High")
    CRITICAL = 3, _("Critical")

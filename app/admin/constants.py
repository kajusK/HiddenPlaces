"""Constants for admin module."""
from flask_babel import lazy_gettext as _
from app.utils.enums import StringEnum


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

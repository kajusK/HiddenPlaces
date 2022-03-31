"""Events types for logging"""
from abc import ABC

from app.page.constants import PageType
from app.location.models import Location, Visit
from app.category.models import Category
from app.user.models import User, Invitation, Ban
from app.user.constants import UserRole
from app.admin.constants import EventType, EventSeverity

# pylint: disable=missing-class-docstring


class Event(ABC):
    """Abstract class for event description."""
    text: str = ''
    severity = EventSeverity.NORMAL
    type = EventType.OTHER


#
# User Events
#


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

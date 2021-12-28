"""Custom enum types."""
from enum import Enum
from typing import Optional


class OrderedEnum(Enum):
    """Implements Enum that allows comparsion of its elements together."""
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class StringEnum(OrderedEnum):
    """Enum for strings with translations.

    Define items like:
    FOO = 0, _("Translated string")
    """
    translation: str  # pylint: disable=invalid-name

    def __new__(cls, value: int, translation: str):
        """Custom object creation.

        Args:
            value: Numeric value of the item
            translation: Translation string for the item
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.translation = translation
        return obj

    @classmethod
    def choices(cls, skip: Optional[list] = None):
        """Get list of choices for wtforms (Enum, translation).

        Args:
            skip: List of enum values to be skipped in choices
        """
        data = []
        if skip is None:
            skip = []

        for item in cls:
            if item in skip:
                continue
            data.append((item.value, item.translation))
        return data

    @classmethod
    def coerce(cls, item):
        """Coerce method for wtforms.

        Args:
            item: Either class item or name to be coerced or '' for None
        Return:
            Enum item
        Raises:
            ValueError: item not corresponding to any item of this enum
        """
        if isinstance(item, str) and item == '':
            return None

        if isinstance(item, cls):
            return item
        try:
            # pylint: disable=no-value-for-parameter
            return cls(int(item))
        except KeyError as e:
            raise ValueError(item) from e

    def __str__(self) -> str:
        """Get string of the item ID."""
        return self.translation

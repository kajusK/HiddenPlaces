"""Custom enum types."""
from enum import Enum
from typing import Optional, Union
from flask_babel import LazyString


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
    FOO = _("Translated string")
    """
    translation: str  # pylint: disable=invalid-name

    def __new__(cls, translation: Union[str, LazyString]):
        """Custom object creation.

        Args:
            translation: Translation string for the item
        """
        value = len(cls.__members__) + 1
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
        return str(self.translation)

"""Database utilities."""
import uuid
from typing import Optional
from sqlalchemy import types, dialects

from app.extensions import db
from app.utils import LatLon


class DBItem(db.Model):
    """Parent class for all database items.

    It adds an id column to all DB items and defines common methods for
    commiting, deleting, etc.

    Attributes:
        id: A row ID.
    """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, unique=True,
                   autoincrement=True)

    @classmethod
    def create(cls, *args, **kwargs):
        """Creates a new DB item and add it to session.

        Returns:
            A new database item instance
        """
        instance = cls(*args, **kwargs)
        db.session.add(instance)
        return instance

    @classmethod
    def get_by_id(cls, item_id: int):
        """Gets item from database by it's ID identifier.

        Args:
            item_id: ID of the item to get from this DB table.
        Returns:
            A Database item or None.
        """
        return cls.query.get(item_id)

    def delete(self) -> None:
        """Deletes this item from the current session."""
        db.session.delete(self)


class _LatLonDb(types.TypeDecorator):
    """Custom database type for latitude/longitude data.

    The value is stored as float in decimal degrees
    """
    impl = types.Float
    cache_ok = True

    def process_bind_param(self, value: Optional[LatLon], dialect: str):
        """Converts LatLon value to float to store in DB.

        Args:
            value: LatLon object
            dialect: SQL dialect used
        Returns:
            float: LatLon converted to decimal degrees
        """
        if value is None:
            return value
        return value.value

    def process_result_value(self, value: Optional[float], dialect: str):
        """Converts float value in decimal degrees back to LatLon format

        Args:
            value: Decimal degrees value
            dialect: SQL dialect used
        Returns:
            LatLon: Value converted to object
        """
        if value is None:
            return value
        return LatLon(value, is_latitude=isinstance(self, Latitude))


class Latitude(_LatLonDb):
    """Custom database type for latitude data."""
    pass


class Longitude(_LatLonDb):
    """Custom database type for longitude data."""
    pass


class UUID(types.TypeDecorator):
    """UUID database type."""
    impl = types.BINARY(16)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Loads type implementation based on used DB dialect.

        Args:
            dialect: Dialect used (e.g. postgresql,...)
        Returns:
            Database type for given dialect
        """
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(dialects.postgresql.UUID())
        return dialect.type_descriptor(types.BINARY(16))

    def process_bind_param(self, value, dialect):
        """Converts input value to database format.

        Args:
            value: Value to be converted
            dialect: Database dialect used
        Returns:
            converted value
        """
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)

        if isinstance(value, uuid.UUID):
            return value.bytes
        return bytes(value)

    def process_result_value(self, value, dialect):
        """Converts database data back to UUID format.

        Args:
            value: Database value to be converted
            dialect: Database dialect used
        Returns:
            Converted UUID data
        """
        if value is None:
            return value

        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(bytes=value)
        return value

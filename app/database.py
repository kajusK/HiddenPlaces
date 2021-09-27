"""Database utilities."""
from app.extensions import db


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

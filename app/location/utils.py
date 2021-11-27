"""Helper functions for locations."""
from abc import ABC, abstractmethod
from app.location.models import Location
from app.location.forms import LocationForm


class LocationUtil(ABC):
    """Urbex location utilities."""
    @staticmethod
    @abstractmethod
    def create(location: Location, form: LocationForm) -> None:
        """Adds specific location data to location being created

        Args:
            location: Location to add the data to
            form: Form to get data from
        """
        pass

    @staticmethod
    @abstractmethod
    def load(location: Location, form: LocationForm) -> None:
        """Fills data from specific location type record to form.

        Args:
            location: Location to load data from
            form: Form to fill data to
        """
        pass

    @staticmethod
    @abstractmethod
    def edit(location: Location, form: LocationForm) -> None:
        """Edits existing specific location record with form data

        Args:
            location: Location to save data to
            form: Form to fill data in
        """
        pass

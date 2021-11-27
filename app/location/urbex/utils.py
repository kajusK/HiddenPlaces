"""Helper functions for urbex locations."""
from app.location.models import Location
from app.location.urbex.models import Urbex
from app.location.urbex.forms import UrbexForm
from app.location.utils import LocationUtil


class UrbexUtil(LocationUtil):
    """Urbex location utilities."""
    @staticmethod
    def create(location: Location, form: UrbexForm) -> None:
        """Creates a new urbex location from form data.

        Args:
            location: Location to add the Underground to
            form: Form to get data from
        """
        location.urbex = Urbex.create(
            type=form.type.data,
            state=form.state.data,
            accessibility=form.accessibility.data,
            abandoned_year=form.abandoned.data,
        )

    @staticmethod
    def load(location: Location, form: UrbexForm) -> None:
        """Fills data from urbex record to form.

        Args:
            location: Location to load data from
            form: Form to load data to
        """
        form.type.data = location.urbex.type
        form.state.data = location.urbex.state
        form.accessibility.data = location.urbex.accessibility
        form.abandoned.data = location.urbex.abandoned_year

    @staticmethod
    def edit(location: Location, form: UrbexForm) -> None:
        """Edits existing urbex record with form data

        Args:
            location: Location to save data to
            form: Form to fill data in
        """
        location.urbex.type = form.type.data
        location.urbex.state = form.state.data
        location.urbex.accessibility = form.accessibility.data
        location.urbex.abandoned_year = form.abandoned.data

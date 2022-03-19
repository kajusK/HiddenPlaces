"""Helper functions for hiking locations."""
from app.location.models import Location
from app.location.hiking.models import Hiking, HikingFeatures
from app.location.hiking.forms import HikingForm
from app.location.utils import LocationUtil


class HikingUtil(LocationUtil):
    """Hiking location utilities."""
    @staticmethod
    def create(location: Location, form: HikingForm) -> None:
        """Creates a new hiking location from form data.

        Args:
            location: Location to add the Hiking to
            form: Form to get data from
        """
        location.hiking = Hiking.create(
            type=form.type.data,
        )
        for feature in form.features.data:
            location.hiking.features.append(
                HikingFeatures.create(type=feature))

    @staticmethod
    def load(location: Location, form: HikingForm) -> None:
        """Fills data from hiking record to form.

        Args:
            location: Location to load data from
            form: Form to load data to
        """
        form.type.data = location.hiking.type
        form.materials.data = [f.type for f in location.hiking.features]

    @staticmethod
    def edit(location: Location, form: HikingForm) -> None:
        """Edits existing urbex record with form data

        Args:
            location: Location to save data to
            form: Form to fill data in
        """
        location.hiking.type = form.type.data

        location.hiking.features = []
        for feature in form.features.data:
            location.hiking.features.append(
                HikingFeatures.create(type=feature))

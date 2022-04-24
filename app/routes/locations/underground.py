"""Helper functions for underground locations."""
from app.models.location import Location
from app.routes.locations import LocationUtil
from app.models.locations.underground import Underground, Material
from app.forms.locations.underground import UndergroundForm


class UndergroundUtil(LocationUtil):
    """Underground location utilities."""

    @staticmethod
    def create(location: Location, form: UndergroundForm) -> None:
        """Creates a new underground location from form data.

        Args:
            location: Location to add the Underground to
            form: Form to get data from
        """
        location.underground = Underground.create(
            type=form.type.data,
            state=form.state.data,
            accessibility=form.accessibility.data,
            tools=form.tools.data,
            length=form.length.data,
            geofond_id=form.geofond_id.data,
            abandoned_year=form.abandoned.data,
        )
        for material in form.materials.data:
            location.underground.materials.append(
                Material.create(type=material))

    @staticmethod
    def load(location: Location, form: UndergroundForm) -> None:
        """Fills data from underground record to form.

        Args:
            location: Location to load data from
            form: Form to fill data in
        """
        form.type.data = location.underground.type
        form.state.data = location.underground.state
        form.accessibility.data = location.underground.accessibility
        form.materials.data = [m.type for m in location.underground.materials]
        form.tools.data = location.underground.tools
        form.length.data = location.underground.length
        form.geofond_id.data = location.underground.geofond_id
        form.abandoned.data = location.underground.abandoned_year

    @staticmethod
    def edit(location: Location, form: UndergroundForm) -> None:
        """Edits existing underground record with form data

        Args:
            location: Location to save data to
            form: Form to fill data in
        """
        location.underground.type = form.type.data
        location.underground.state = form.state.data
        location.underground.accessibility = form.accessibility.data
        location.underground.length = form.length.data
        location.underground.geofond_id = form.geofond_id.data
        location.underground.abandoned_year = form.abandoned.data
        location.underground.tools = form.tools.data

        location.underground.materials = []
        for material in form.materials.data:
            location.underground.materials.append(
                Material.create(type=material))

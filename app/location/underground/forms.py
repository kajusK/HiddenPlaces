"""Underground specific location forms."""
from datetime import datetime
from flask_babel import _
from wtforms import StringField, SelectField, ValidationError, IntegerField
from wtforms.validators import InputRequired, Length, Optional, NumberRange

from app.utils.fields import CustomMultipleField
from app.location.forms import LocationForm
from app.location.underground.constants import \
    UndergroundType, UndergroundState, MaterialType, \
    UndergroundAccessibility, MAX_TOOLS_LEN


class UndergroundForm(LocationForm):
    """Underground location metadata form."""
    type = SelectField(_("Type"), [InputRequired()],
                       coerce=UndergroundType.coerce,
                       choices=[('', _("Location type"))]
                       + UndergroundType.choices())
    state = SelectField(_("State"), [InputRequired()],
                        coerce=UndergroundState.coerce,
                        choices=[('', _("Location state"))]
                        + UndergroundState.choices())
    accessibility = SelectField(_("Accessibility"), [InputRequired()],
                                coerce=UndergroundAccessibility.coerce,
                                choices=[('', _("Location accessibility"))]
                                + UndergroundAccessibility.choices())
    materials = CustomMultipleField(_("Materials"), [InputRequired()],
                                    coerce=MaterialType.coerce,
                                    choices=[('', _("Select mined materials"))]
                                    + MaterialType.choices())

    tools = StringField(_("Tools for opening the entrance"),
                        [Length(max=MAX_TOOLS_LEN)])
    length = IntegerField(_("Length [m]"), [Optional(), NumberRange(min=0)])
    geofond_id = IntegerField(_("Geofond ID"), [Optional(),
                                                NumberRange(min=0)])
    abandoned = IntegerField(_("Abandoned [year]"), [Optional()])

    def validate_abandoned(self, field) -> None:
        """Validates the location was abandoned in the past."""
        if field.data > datetime.utcnow().year:
            raise ValidationError(_("It cannot be in the future"))

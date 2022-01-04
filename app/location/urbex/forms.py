"""Urbex specific location forms."""
from datetime import datetime
from flask_babel import lazy_gettext as _
from wtforms import SelectField, ValidationError, IntegerField
from wtforms.validators import InputRequired, Optional

from app.location.forms import LocationForm
from app.location.urbex.constants import UrbexType, UrbexState, \
     UrbexAccessibility


class UrbexForm(LocationForm):
    """Urbex location metadata form."""
    type = SelectField(_("Type"), [InputRequired()],
                       coerce=UrbexType.coerce,
                       choices=[('', _("Location type"))]
                       + UrbexType.choices())
    state = SelectField(_("State"), [InputRequired()],
                        coerce=UrbexState.coerce,
                        choices=[('', _("Location state"))]
                        + UrbexState.choices())
    accessibility = SelectField(_("Accessibility"), [InputRequired()],
                                coerce=UrbexAccessibility.coerce,
                                choices=[('', _("Location accessibility"))]
                                + UrbexAccessibility.choices())
    abandoned = IntegerField(_("Abandoned [year]"), [Optional()])

    def validate_abandoned(self, field):
        """Validates the location was abandoned in the past."""
        if field.data > datetime.utcnow().year:
            raise ValidationError(_("It cannot be in the future"))

"""Tourist specific location forms."""
from flask_babel import lazy_gettext as _
from wtforms import SelectField
from wtforms.validators import InputRequired

from app.utils.fields import CustomMultipleField
from app.location.forms import LocationForm
from app.location.hiking.constants import HikingFeature, HikingType


class HikingForm(LocationForm):
    """Hiking location metadata form."""
    type = SelectField(_("Type"), [InputRequired()],
                       coerce=HikingType.coerce,
                       choices=[('', _("Location type"))]
                       + HikingType.choices())

    features = CustomMultipleField(_("Features"),
                                   coerce=HikingFeature.coerce,
                                   choices=[('', _("Select features"))]
                                   + HikingFeature.choices())

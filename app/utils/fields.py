"""Custom fields for wtforms."""
from flask_babel import lazy_gettext as _
from werkzeug.datastructures import FileStorage
from wtforms import MultipleFileField as _MultipleFileField
from wtforms import SelectMultipleField, ValidationError


class MultipleFileField(_MultipleFileField):
    """Werkzeug-aware subclass of :class:`wtforms.fields.FileField`."""

    def process_formdata(self, valuelist):
        valuelist = [x for x in valuelist if isinstance(x, FileStorage) and x]

        if len(valuelist):
            # pylint: disable=attribute-defined-outside-init
            self.data = list(valuelist)
        else:
            self.raw_data = ()


class CustomMultipleField(SelectMultipleField):
    """Custom multiple selection fields with support for StringEnum."""
    def pre_validate(self, form):
        if self.choices is None:
            raise TypeError(self.gettext("Choices cannot be None."))

        if not self.validate_choice or not self.data:
            return

        acceptable = {self.coerce(c[0]) for c in self.iter_choices()}
        if any(d not in acceptable for d in self.data):
            unacceptable = [str(d) for d in set(self.data) - acceptable]
            raise ValidationError(_("'%(value)s' is not a valid choice.",
                                    value="', '".join(unacceptable)))

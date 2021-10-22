from werkzeug.datastructures import FileStorage
from wtforms import MultipleFileField as _MultipleFileField


class MultipleFileField(_MultipleFileField):
    """Werkzeug-aware subclass of :class:`wtforms.fields.FileField`."""

    def process_formdata(self, valuelist):
        valuelist = [x for x in valuelist if isinstance(x, FileStorage) and x]

        if len(valuelist):
            self.data = list(valuelist)
        else:
            self.raw_data = ()

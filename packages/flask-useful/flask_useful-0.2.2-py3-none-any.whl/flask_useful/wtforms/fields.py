from werkzeug.datastructures import FileStorage
from wtforms import fields
from wtforms import widgets
from wtforms.compat import text_type
from wtforms.validators import StopValidation
from .widgets import CheckboxGroup


__all__ = (
    'CheckboxGroupField', 'RadioBoxField',
    'FileField', 'ValueListField',
)


class CheckboxGroupField(fields.SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = CheckboxGroup(inline=True)
    option_widget = widgets.CheckboxInput()


class FileField(fields.FileField):
    """
    A file selection field with a save method that the Flask-Upload package uses to save.

    Attributes:
        label (str):
        upload_set:
    """

    def __init__(self, label=None, upload_set=None, **kwargs):
        super().__init__(label, **kwargs)
        self.upload_set = upload_set
        self.file = None

    def process_formdata(self, valuelist):
        if valuelist:
            file_storage = valuelist[0]

            if file_storage.filename != '':
                self.file = file_storage
                self.data = ''

    def pre_validate(self, form):
        if self.data and (not self.raw_data or not self.raw_data[0]):
            raise StopValidation

    def save(self, **kwargs):
        if self.file is not None:
            self.data = self.upload_set.save(self.file, **kwargs)
        return self.data


class RadioBoxField(fields.SelectField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = CheckboxGroup(inline=True)
    option_widget = widgets.RadioInput()


class ValueListField(fields.StringField):
    """
    List of values.

    For example, can be used to enumerate tags or scope for a REST API client.

    Parameters:
        label (str): The label of the field.
        separator (str): Separator character for values.
        coerce (callable): Callback to explicitly cast each value to the desired data type.
    """
    def __init__(self, label=None, separator=',', coerce=text_type, **kwargs):
        super().__init__(label, **kwargs)
        self.separator = separator
        self.coerce = coerce
        self.data = ()

    def _value(self):
        return self.separator.join(str(v) for v in self.data)

    def process_data(self, value):
        try:
            self.data = tuple(self.coerce(v) for v in value)
        except (ValueError, TypeError):
            self.data = ()

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = tuple(self.coerce(v.strip()) for v in valuelist[0].split(self.separator))

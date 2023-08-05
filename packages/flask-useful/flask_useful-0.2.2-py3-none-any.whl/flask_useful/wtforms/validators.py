import re

import phonenumbers
from wtforms.validators import ValidationError, StopValidation


class OnlyOne(object):
    """
    Validates that a value was entered in only one of the specified form fields.
    """

    def __init__(self, fieldnames, message=None):
        self.fieldnames = fieldnames.split() if isinstance(fieldnames, str) else fieldnames
        self.message = message

    def __call__(self, form, field):
        fieldnames = [field.short_name, *self.fieldnames]

        try:
            values = [bool(form[i].data) for i in fieldnames]
        except KeyError as err:
            field_name, *_ = err.args
            raise StopValidation(field.gettext("Invalid field name '%s'.") % field_name)

        only_one = values.count(True) == 1

        if not only_one:
            message = self.message
            if message is None:
                message = field.gettext('It is required to set the value of one of the fields: %(fieldnames)s.')

            raise StopValidation(message % {'fieldnames': ', '.join(fieldnames)})

        if only_one and not field.data:
            raise StopValidation


class Phone(object):
    def __init__(self, region=None, keep_raw_input=False, _check_region=True, message=None):
        self.region = region
        self.keep_raw_input = keep_raw_input
        self._check_region = _check_region
        self.message = message or 'Invalid phone number.'

    def __call__(self, form, field):
        try:
            numobj = phonenumbers.parse(
                field.data, region=self.region, keep_raw_input=self.keep_raw_input, _check_region=self._check_region
            )
            if not phonenumbers.is_valid_number(numobj):
                raise ValidationError(self.message)
        except phonenumbers.NumberParseException as err:
            raise ValidationError(err)


class Slug(object):
    slug_re = r'^[a-z0-9-_]+$'
    slug_unicode_re = r'^[-\w]+$'

    def __init__(self, allow_unicode=False, message=None):
        self.allow_unicode = allow_unicode
        self.message = message

    def __call__(self, form, field):
        pattern = self.slug_unicode_re if self.allow_unicode else self.slug_re
        if not re.match(pattern, field.data or '', re.I):
            raise ValidationError(self.message or field.gettext('Invalid input.'))

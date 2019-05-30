import re

from wtforms import ValidationError
from flask_babel import _


def has_upper_letter(form, field):
    password = field.data
    pattern = r'[A-Z]'
    if not re.search(pattern, password):
        raise ValidationError(_('Password should contain at least 1 capital letter'))


def has_lower_letter(form, field):
    password = field.data
    pattern = r'[a-z]'
    if not re.search(pattern, password):
        raise ValidationError(_('Password should contain at least 1 lowercase letter'))


def has_digit(form, field):
    password = field.data
    pattern = r'\d'
    if not re.search(pattern, password):
        raise ValidationError(_('Password should contain at least 1 digit'))



def is_long_enought(form, field):
    min_lenght = 10
    message = _('Password should be not less then %d symbols') % (min_lenght)
    l = field.data and len(field.data) or 0
    if l < min_lenght:
        raise ValidationError(message)


password_validators = [has_upper_letter, has_lower_letter, has_digit, is_long_enought]


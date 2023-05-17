from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from django.utils.translation import ugettext_lazy as _


# ----------------- SIGN UP VALIDATIONS -----------------
# Password validation
def validate_password(password):
    if len(password) < 6:
        raise ValidationError(
            _('Password is too short'),
        )


# Name validation
def validate_name(name):
    if not re.compile("^[A-Za-z .-]+$").match(name):
        raise ValidationError(
            _('"%(name)s" contains invalid character.'), params={'name': name},
        )

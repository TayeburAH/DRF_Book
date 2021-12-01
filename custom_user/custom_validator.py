from django.core.validators import ValidationError
from validate_email import validate_email

import DNS

DNS.defaults['server'] = ['8.8.8.8', '8.8.4.4']


def validate_emails(email):
    if not validate_email(email, verify=True):
        raise ValidationError('Invalid Email')
    else:
        return email

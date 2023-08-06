from datetime import date as _date
from datetime import datetime as _datetime

import validate_docbr as _validate_docbr
from django.utils import timezone as _timezone
from django.utils.translation import gettext as _
from rest_framework import exceptions as _exceptions

__all__ = [
    "validate_cpf",
    "validate_cnpj",
    "validate_future_datetime",
    "validate_future_date",
    "validate_start_and_end_date",
]


def validate_cpf(num_cpf):
    """Validates CPF, given a cpf number. Raises a ValidationError if it's not"""
    cpf = _validate_docbr.CPF()

    if not cpf.validate(num_cpf):
        raise _exceptions.ValidationError(_("Invalid CPF"), "invalid_cpf")


def validate_cnpj(num_cnpj):
    """Validates CNPJ, given a cnpj number. Raises a ValidationError if it's not"""
    cnpj = _validate_docbr.CNPJ()

    if not cnpj.validate(num_cnpj):
        raise _exceptions.ValidationError(_("Invalid CNPJ"), "invalid_cnpj")


def validate_future_datetime(date: _datetime):
    """Validates if a given datetime is in the future, this means the date cannot be
    earlier than timezone.now(). Raises a ValidationError if it's not
    """
    if date < _timezone.now():
        raise _exceptions.ValidationError(
            _("The datetime must be in the future"),
            "datetime_not_in_future",
        )


def validate_future_date(date: _date):
    """Validates if a given date is in the future, this means the date cannot be
    earlier than timezone.now().date().
    """
    if date < _timezone.now().date():
        raise _exceptions.ValidationError(
            _("The date must be in the future"),
            "date_not_in_future",
        )


def validate_start_and_end_date(start, end):
    """Validates if a given start date is earlier than the specified end date. Raises a
    ValidationError if it's not
    """
    if end < start:
        raise _exceptions.ValidationError(
            _("End datetime must be later than start datetime"),
            "end_datetime_earlier_than_start_datetime",
        )

from django.core import validators as _django_validators
from django.db import models as _models
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions as _exceptions
from rest_framework import serializers as _serializers

from b2_utils import validators as _validators

__all__ = [
    "CpfField",
    "CnpjField",
    "DocumentField",
    "LowercaseEmailField",
]


class CpfField(_models.CharField):
    description = "(Brazil) Cadastro de Pessoa Física"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 11
        kwargs["validators"] = [
            _django_validators.MinLengthValidator(11),
            _validators.validate_cpf,
        ]

        super().__init__(*args, **kwargs)


class CnpjField(_models.CharField):
    description = "(Brazil) Cadastro Nacional da Pessoa Jurídica"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 14
        kwargs["validators"] = [
            _django_validators.MinLengthValidator(14),
            _validators.validate_cnpj,
        ]

        super().__init__(*args, **kwargs)


class DocumentField(_models.CharField):
    CNPJ_LEN = 14
    CPF_LEN = 11

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 14
        kwargs["validators"] = [
            _django_validators.MinLengthValidator(11),
            _django_validators.MaxLengthValidator(14),
            self.validate_cnpj_cpf,
        ]

        super().__init__(*args, **kwargs)

    @classmethod
    def validate_cnpj_cpf(cls, value):
        if len(value) == cls.CPF_LEN:
            _validators.validate_cpf(value)

        elif len(value) == cls.CNPJ_LEN:
            _validators.validate_cnpj(value)

        else:
            raise _exceptions.ValidationError(
                _("Invalid CPF or CNPJ"),
                "invalid_cpf_or_cnpj",
            )


class LowercaseEmailField(_serializers.CharField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return value.lower()

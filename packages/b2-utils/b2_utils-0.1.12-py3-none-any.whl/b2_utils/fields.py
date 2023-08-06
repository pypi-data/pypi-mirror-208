from django.core import validators as _django_validators
from django.db import models as _models

from b2_utils import validators as _validators

__all__ = [
    "CpfField",
    "CnpjField",
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

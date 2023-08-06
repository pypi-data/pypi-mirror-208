from typing import List as _List

import validate_docbr as _validate_docbr
from constance import config as _config
from model_bakery import baker as _baker
from rest_framework.test import APIClient as _APIClient
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as _TokenObtainPairSerializer,
)

from b2_utils import models as _models

__all__ = [
    "sample_city",
    "sample_address",
    "sample_phone",
    "sample_cpf",
    "sample_cnpj",
    "configure_api_client",
]


def configure_api_client(
    client: _APIClient,
    set_header_version=True,
    access_token=None,
    user=None,
) -> _APIClient:
    headers = {}
    if set_header_version:
        version = _config.ALLOWED_VERSIONS.split(" ")[0]
        headers["HTTP_ACCEPT"] = f"application/json; version={version}"

    if access_token is not None:
        headers["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

    if user is not None:
        access = str(_TokenObtainPairSerializer.get_token(user).access_token)
        headers["HTTP_AUTHORIZATION"] = f"Bearer {access}"

    client.credentials(
        **headers,
    )

    return client


def sample_city(**kwargs) -> _models.City | _List[_models.City]:
    """Create and return a sample City"""

    return _baker.make(_models.City, **kwargs)


def sample_address(**kwargs) -> _models.Address | _List[_models.Address]:
    """Create and return a sample Address"""

    kwargs["city"] = kwargs.get("city", sample_city)
    return _baker.make(_models.Address, **kwargs)


def sample_phone(**kwargs) -> _models.Phone | _List[_models.Phone]:
    """Create and return a sample Phone"""

    return _baker.make(_models.Phone, **kwargs)


def sample_cpf() -> str:
    """Return a sample CPF"""

    return _validate_docbr.CPF().generate()


def sample_cnpj() -> str:
    """Return a sample CNPJ"""

    return _validate_docbr.CNPJ().generate()

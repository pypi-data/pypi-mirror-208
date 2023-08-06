import jwt as _jwt
from django.conf import settings as _settings
from django.contrib.auth import get_user_model as _get_user_model
from django.core.cache import cache as _cache
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django.utils import timezone as _timezone
from rest_framework_simplejwt.tokens import RefreshToken as _RefreshToken

__all__ = [
    "get_and_delete_cache",
    "generate_token_for_user",
    "get_access_token_for_user",
    "get_user_from_jwt_raw_token",
]


def get_and_delete_cache(key):
    value = _cache.get(key)
    _cache.delete(key)

    return value


def generate_token_for_user(user):
    return hash(f"{user.email}:{_timezone.now()}")


def get_access_token_for_user(user):
    return _RefreshToken.for_user(user).access_token


def get_user_from_jwt_raw_token(raw_token):
    token = _jwt.decode(
        raw_token,
        _settings.SECRET_KEY,
        algorithms=_settings.SIMPLE_JWT["ALGORITHM"],
    )

    return _get_object_or_404(_get_user_model(), id=token["user_id"])

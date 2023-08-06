from rest_framework import exceptions as _exceptions
from rest_framework import permissions as _permissions

__all__ = [
    "IsMe",
    "IsSafeMethods",
    "IsAnonymous",
    "IsValidVersion",
    "CanCreate",
    "CanUpdate",
    "CanDestroy",
    "IsUserActive",
]


class IsMe(_permissions.BasePermission):
    """Allows object access only if the current object is the user himself"""

    def has_object_permission(self, request, _, obj):
        return request.user == obj


class IsSafeMethods(_permissions.BasePermission):
    """Allows access only if method is in permissions.SAFE_METHODS."""

    def has_permission(self, request, _):
        return request.method in _permissions.SAFE_METHODS


class IsAnonymous(_permissions.BasePermission):
    """Allows access only if request user is Annonymous."""

    def has_permission(self, request, _):
        return request.user.is_anonymous


class IsValidVersion(_permissions.BasePermission):
    """Allows access only if version is in request."""

    def has_permission(self, request, _):
        if not request.version:
            raise _exceptions.NotAcceptable

        return True


class CanCreate(_permissions.BasePermission):
    """Allows access only if action is create."""

    def has_permission(self, _, view):
        return view.action == "create"


class CanUpdate(_permissions.BasePermission):
    """Allows access only if action is either partial_update or update."""

    def has_permission(self, _, view):
        return view.action in ["partial_update", "update"]


class CanDestroy(_permissions.BasePermission):
    """Allows access only if action is destroy."""

    def has_permission(self, _, view):
        return view.action == "destroy"


class IsUserActive(_permissions.BasePermission):
    """Allows access only if request user is active."""

    def has_permission(self, request, _):
        return request.user.is_active

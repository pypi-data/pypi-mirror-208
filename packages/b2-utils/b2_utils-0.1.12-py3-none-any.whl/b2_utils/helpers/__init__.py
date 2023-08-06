import random as _random
import urllib.parse as _urlparse
from typing import List as _List
from urllib.parse import urlencode as _urlencode

from b2_utils.helpers.auth import *  # noqa
from b2_utils.helpers.auth import __all__ as _auth_all

__all__ = _auth_all + [  # noqa: PLE0605
    "random_hex_color",
    "get_nested_attr",
    "update_url_querystring",
    "days_to_seconds",
]


def days_to_seconds(days):
    return days * 24 * 60 * 60


def random_hex_color(min_color=0x000000, max_color=0xFFFFFF) -> str:
    """Returns a random hexadecimal color in range [min_color, max_color], including
    both end points.

    Parameters
    ---------
    min_color : int
        Minimum value for color (default 0x000000)
    max_color : int
        Maximum value for color (default 0xFFFFFF)

    Returns
    -------
    str
        A random color "#XXXXXX" that is between min_color and max_color values.
    """

    return "#%06x".upper() % _random.randint(min_color, max_color)  # noqa: S311


def get_nested_attr(obj: any, path: str, raise_exception=False, default=None):
    """Gets nested object attributes, raising exceptions only when specified.

    Parameters
    ---------
    obj : any
        The object which attributes will be obtained
    path : str
        Attribute path separated with dots ('.') as usual
    raise_exception : bool = False
        If this value sets to True, an exception will be raised if an attribute cannot
        be obtained, even if default value is specified
    default : any = None
        A default value that's returned if the attribute can't be obtained. This
        parameter is ignored if raise_exception=True

    Returns
    -------
    any
        Attribute value or default value specified if any error occours while trying
        to get object attribute
    """

    for path_attr in path.split("."):
        if raise_exception:
            obj = getattr(obj, path_attr)
        else:
            obj = getattr(obj, path_attr, default)

    return obj


def update_url_querystring(
    url: str,
    params: dict,
    aditional_params: _List[str] = None,
) -> str:
    """Updates the queryparams given a URL.

    Parameters
    ---------
    url: str
        The url you want to update.
    params: dict
        A dict with the new queryparams values.

    Returns
    -------
    str
        The full url, with updated queryparams.
    """
    url_parts = list(_urlparse.urlparse(url))
    query = dict(_urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = _urlencode(query)
    if aditional_params:
        params = "&".join(aditional_params)
        if url_parts[4]:
            url_parts[4] += f"&{params}"

        else:
            url_parts[4] = params

    return _urlparse.urlunparse(url_parts)


def cnpj_parser(value: str) -> str:
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"


class Alias:
    def __init__(self, source_name, transform=None):
        self.source_name = source_name
        self.transform = transform

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        value = getattr(obj, self.source_name)

        if self.transform:
            value = self.transform(value)

        return value

    def __set__(self, obj, value):
        if self.transform:
            value = self.transform(value)

        setattr(obj, self.source_name, value)

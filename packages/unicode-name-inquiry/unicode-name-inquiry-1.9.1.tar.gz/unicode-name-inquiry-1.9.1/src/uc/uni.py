# SPDX-License-Identifier: MIT

from collections.abc import Callable
from typing import Any

import unicodedata

# Conversion

def unichr(value: int | str) -> str:
    """Converts an integer, character, or Unicode name to character."""
    if isinstance(value, int):
        return chr(value)

    if not isinstance(value, str):
        raise TypeError(f'{value} is not str or int')

    # Now we have a str.
    if len(value) == 1:
        return value

    # Check for a string that represents an integer.
    try:
        return chr(int(value, 0))
    except ValueError:
        pass

    # Check for a Unicode character name.
    try:
        return unicodedata.lookup(value)
    except KeyError:
        pass

    # Check for U+hex.
    if value.lower()[0] == 'u':
        i = value[1 :]
        if i[0] == '+':
            i = i[1 :]
        # Let this raise ValueError.
        return chr(int(i, 16))

    raise ValueError(f'No character {repr(value)}')

# Normalization

def normalize(c: str, form) -> str:
    # NB: character first.
    return unicodedata.normalize(form.upper(), c)

# Uniform property access functions. These all accept a ‘default’ argument,
# even though in many cases it is not used.

PropertyAccessFunction = Callable[[str, Any | None], Any]

PROPERTIES: dict[str, PropertyAccessFunction] = {}

def register(v: dict):

    def decorator(fn):
        v[fn.__name__] = fn
        return fn

    return decorator

@register(PROPERTIES)
def bidirectional(c: str, _=None) -> str:
    return unicodedata.bidirectional(c)

@register(PROPERTIES)
def category(c: str, _=None) -> str:
    return unicodedata.category(c)

@register(PROPERTIES)
def combining(c: str, _=None) -> int:
    return unicodedata.combining(c)

@register(PROPERTIES)
def decimal(c: str, default=None):
    return unicodedata.decimal(c, default)

@register(PROPERTIES)
def decomposition(c: str, _=None) -> str:
    return unicodedata.decomposition(c)

@register(PROPERTIES)
def digit(c: str, default=None):
    return unicodedata.digit(c, default)

@register(PROPERTIES)
def east_asian_width(c: str, _=None):
    return width(c)

@register(PROPERTIES)
def mirrored(c: str, _=None) -> int:
    return unicodedata.mirrored(c)

@register(PROPERTIES)
def name(c: str, default=None) -> str:
    try:
        return unicodedata.name(c)
    except ValueError:
        if default is not None:
            return default
        return f'U+{ord(c):04X}'

@register(PROPERTIES)
def nfc(c: str, _=None) -> str:
    return unicodedata.normalize('NFC', c)

@register(PROPERTIES)
def nfkc(c: str, _=None) -> str:
    return unicodedata.normalize('NFKC', c)

@register(PROPERTIES)
def nfd(c: str, _=None) -> str:
    return unicodedata.normalize('NFD', c)

@register(PROPERTIES)
def nfkd(c: str, _=None) -> str:
    return unicodedata.normalize('NFKD', c)

@register(PROPERTIES)
def numeric(c: str, default=None):
    return unicodedata.numeric(c, default)

@register(PROPERTIES)
def ordinal(c: str, _=None) -> int:
    return ord(c)

@register(PROPERTIES)
def width(c: str, _=None):
    return unicodedata.east_asian_width(c)

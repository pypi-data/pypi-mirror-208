# SPDX-License-Identifier: MIT

from collections.abc import Iterable, Sequence

import uc.block
import uc.uni

class UniFormat:
    """Allows a character to be passed to str.format_map()."""

    def __init__(self, c: str, eol: str = '\n'):
        self.c = c
        self.v = ord(c)
        self.eol = eol

    def __getitem__(self, key: str) -> str:
        k = key.lower()
        if k == 'char':
            return self.c
        if k == 'u':
            return f'U+{self.v:04X}'
        if k == 'v':
            return str(self.v)
        if k == 'x':
            return f'{self.v:04X}'
        if k.startswith('u') and k[1 :].isdigit():
            width = int(k[1 :])
            return f'U+{self.v:0{width}X}'
        if key in set(('utf8', 'utf-8')):
            return list_to_hex(utf32to8(self.v), 2)
        if key in set(('UTF8', 'UTF-8')):
            return repr(utf32to8(self.v))
        if key in set(('utf16', 'utf-16')):
            return list_to_hex(utf32to16(self.v), 4)
        if key in set(('UTF16', 'UTF-16')):
            return repr(utf32to16(self.v))
        if key == 'block':
            _, name = uc.block.block(self.v)
            return name
        if key == 'id':
            return uc.uni.name(self.c).replace(' ', '_').replace('-', '_')
        if k in ('nfc', 'nfkc', 'nfd', 'nfkd'):
            v = uc.uni.normalize(self.c, k)
            if key.isupper():
                return v
            return ', '.join(uc.uni.name(c) for c in v)
        if key == 'eol':
            return self.eol
        if k in uc.uni.PROPERTIES:
            return str(uc.uni.PROPERTIES[k](self.c, ''))
        raise KeyError(key)

def utf32to16(n: int) -> Sequence[int]:
    """Converts a number to a list holding its UTF-16 encoding."""
    if (n <= 0xD7FF) or (0xE000 <= n <= 0xFFFF):
        return [n]
    if n < 0x10000 or n > 0x10FFFF:
        return []
    n = n - 0x10000
    return [0xD800 + (n >> 10), 0xDC00 + (n & 0x3FF)]

def utf32to8(n: int) -> Sequence[int]:
    """Converts a number to a list holding its UTF-8 encoding."""
    if n < 0x80:
        return [n]
    r = []
    m = 0x1F
    while True:
        r.append(0x80 | (n & 0x3F))
        n = n >> 6
        if n & m == n:
            break
        m = m >> 1
    r.append((0xFE ^ (m << 1)) | n)
    r.reverse()
    return r

def list_to_hex(i: Iterable[int], w: int = 2) -> str:
    """Return a string of hexadecimal numbers from a list of integers."""
    return ' '.join(map(lambda x: f'{x:0{w}X}', i))

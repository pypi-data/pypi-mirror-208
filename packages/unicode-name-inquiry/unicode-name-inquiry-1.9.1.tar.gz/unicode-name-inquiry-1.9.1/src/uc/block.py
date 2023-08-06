# SPDX-License-Identifier: MIT

import uc.data.block

class UniBlock:
    """Representation of a Unicode block (or any contiguous character range)."""

    def __init__(self, which: int | str):
        self.range, self.name = block(which)

    def __contains__(self, key: str | int):
        if isinstance(key, str):
            key = ord(key)
        return key in self.range

    def __repr__(self):
        return 'UniBlock({repr(self.rnge)},{repr(self.name)})'

def __sq(s):
    return ''.join([c.lower() for c in s if c.isalnum()])

def by_name(name: str) -> tuple[range, str]:
    name = __sq(name)
    for r, names in uc.data.block.BLOCKS:
        for s in names:
            if name == __sq(s):
                return (r, names[0])
    raise ValueError(f'Unknown block "{name}"')

def by_code_point(value: int) -> tuple[range, str]:
    for r, names in uc.data.block.BLOCKS:
        if value in r:
            return (r, names[0])
    raise ValueError(f'No block contains 0x{value:06X}')

def block(which: int | str) -> tuple[range, str]:
    """Get a block by range, code point, character, or name."""
    if isinstance(which, int):
        # Block containing the given code point.
        return by_code_point(which)

    if isinstance(which, str):
        if len(which) == 1:
            # Block containing the given character.
            return by_code_point(ord(which))
        # Block looked up by name.
        return by_name(which)

    raise TypeError(f'{which} does not identify a unicode block')

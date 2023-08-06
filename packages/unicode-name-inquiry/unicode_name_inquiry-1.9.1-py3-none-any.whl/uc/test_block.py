# SPDX-License-Identifier: MIT
"""Test uc.block"""

import pytest

from uc.block import UniBlock

def test_uniblock_init_code_point():
    b = UniBlock(0x0123)
    assert b.range == range(0x100, 0x180)
    assert b.name == 'Latin Extended-A'

def test_uniblock_init_code_point_unassigned():
    with pytest.raises(ValueError):
        _ = UniBlock(0x43210)

def test_uniblock_init_character():
    b = UniBlock('\u2192')
    assert b.range == range(0x2190, 0x2200)
    assert b.name == 'Arrows'

def test_uniblock_init_character_unassigned():
    with pytest.raises(ValueError):
        _ = UniBlock('\U00042310')

def test_uniblock_init_type_error():
    with pytest.raises(TypeError):
        _ = UniBlock(UniBlock)

def test_uniblock_init_name():
    b = UniBlock('ASCII')
    assert b.range == range(0x00, 0x80)
    assert b.name == 'Basic Latin'

def test_uniblock_init_name_unassigned():
    with pytest.raises(ValueError):
        _ = UniBlock('This is probably not the name of a Unicode block')

def test_uniblock_contains():
    b = UniBlock('Arrows')
    assert 0x21FF in b
    assert '\u21FF' in b
    assert 0x2190 in b
    assert '\u2190' in b
    assert 0x21FF in b
    assert '\u21FF' in b
    assert 0x218F not in b
    assert '\u218F' not in b
    assert 0x2200 not in b
    assert '\u2200' not in b
    assert 'b' not in b

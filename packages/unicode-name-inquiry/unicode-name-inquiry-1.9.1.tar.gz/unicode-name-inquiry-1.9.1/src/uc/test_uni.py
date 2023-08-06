# SPDX-License-Identifier: MIT
"""Test code.block"""

from typing import Any

import pytest

import uc.uni
import uc.data.ccc

UNICHR_CASES: list[tuple[str, Any]] = [
    ('C', 67),
    ('D', 'D'),
    ('E', 'Latin capital letter E'),
    ('F', 'u46'),
    ('G', 'U+000000047'),
]

@pytest.mark.parametrize('c,i', UNICHR_CASES)
def test_unichr(c, i):
    u = uc.uni.unichr(i)
    assert u == c

def test_unichr_type_error():
    with pytest.raises(TypeError):
        _ = uc.uni.unichr(Any)

def test_uni_bidirectional():
    assert uc.uni.bidirectional('B') == 'L'
    assert uc.uni.bidirectional('\u05D0') == 'R'  # HEBREW LETTER ALEF

def test_uni_category():
    assert uc.uni.category('B') == 'Lu'
    assert uc.uni.category('\u05D0') == 'Lo'  # HEBREW LETTER ALEF

def test_uni_combining():
    assert uc.uni.combining('B') == 0
    # COMBINING DIAERESIS
    assert uc.uni.combining('\u0308') == uc.data.ccc.ABOVE

def test_uni_decimal():
    assert uc.uni.decimal('B') is None
    assert uc.uni.decimal('0') == 0
    # MATHEMATICAL DOUBLE-STRUCK DIGIT THREE
    assert uc.uni.decimal('\U0001D7DB') == 3
    assert uc.uni.decimal('\U00002464') is None  # CIRCLED DIGIT FIVE

def test_uni_decomposition():
    assert uc.uni.decomposition('B') == ''
    # LATIN SMALL LETTER E WITH ACUTE
    # → LATIN SMALL LETTER E, COMBINING ACUTE ACCENT
    assert uc.uni.decomposition('\u00E9') == '0065 0301'

def test_uni_digit():
    assert uc.uni.digit('B') is None
    assert uc.uni.digit('0') == 0
    # MATHEMATICAL DOUBLE-STRUCK DIGIT THREE
    assert uc.uni.digit('\U0001D7DB') == 3
    assert uc.uni.digit('\U00002464') == 5  # CIRCLED DIGIT FIVE

def test_uni_mirrored():
    assert uc.uni.mirrored('B') == 0
    assert uc.uni.mirrored('(') == 1

def test_uni_name():
    assert uc.uni.name('B') == 'LATIN CAPITAL LETTER B'
    assert uc.uni.name('\U00101234') == 'U+101234'
    assert uc.uni.name('B', 'Default') == 'LATIN CAPITAL LETTER B'
    assert uc.uni.name('\U00101234', 'Default') == 'Default'

def test_uni_nfc():
    assert uc.uni.nfc('B') == 'B'
    assert uc.uni.normalize('B', 'nfc') == 'B'
    # COMBINING GRAVE TONE MARK → COMBINING GRAVE ACCENT
    assert uc.uni.nfc('\u0340') == '\u0300'
    assert uc.uni.normalize('\u0340', 'nfc') == '\u0300'

def test_uni_nfkc():
    assert uc.uni.nfkc('B') == 'B'
    assert uc.uni.normalize('B', 'nfkc') == 'B'
    # LATIN CAPITAL LETTER DZ WITH CARON → D, LATIN CAPITAL LETTER Z WITH CARON
    assert uc.uni.nfkc('\u01C4') == 'D\u017D'
    assert uc.uni.normalize('\u01C4', 'nfkc') == 'D\u017D'

def test_uni_nfd():
    assert uc.uni.nfd('B') == 'B'
    assert uc.uni.normalize('B', 'nfd') == 'B'
    # LATIN CAPITAL LETTER A WITH GRAVE → A, COMBINING GRAVE ACCENT
    assert uc.uni.nfd('\u00C0') == 'A\u0300'
    assert uc.uni.normalize('\u00C0', 'nfd') == 'A\u0300'

def test_uni_nfkd():
    assert uc.uni.nfkd('B') == 'B'
    assert uc.uni.normalize('B', 'nfkd') == 'B'
    # LATIN CAPITAL LETTER DZ WITH CARON → D, Z, COMBINING CARON
    assert uc.uni.nfkd('\u01C4') == 'DZ\u030C'
    assert uc.uni.normalize('\u01C4', 'nfkd') == 'DZ\u030C'

def test_uni_numeric():
    assert uc.uni.numeric('B') is None
    assert uc.uni.numeric('0') == 0
    # MATHEMATICAL DOUBLE-STRUCK DIGIT THREE
    assert uc.uni.numeric('\U0001D7DB') == 3
    assert uc.uni.numeric('\U00002464') == 5  # CIRCLED DIGIT FIVE
    assert uc.uni.numeric('\u00BC') == 0.25  # VULGAR FRACTION ONE QUARTER

def test_uni_ordinal():
    assert uc.uni.ordinal('B') == 66

def test_uni_width():
    assert uc.uni.width('B') == 'Na'
    assert uc.uni.width('\u05D0') == 'N'  # HEBREW LETTER ALEF
    assert uc.uni.width('\u0308') == 'A'  # COMBINING DIAERESIS
    assert uc.uni.width('\u30A6') == 'W'  # KATAKANA LETTER U
    assert uc.uni.width('\uFF21') == 'F'  # FULLWIDTH LATIN CAPITAL LETTER A
    assert uc.uni.width('\uFF73') == 'H'  # HALFWIDTH KATAKANA LETTER U

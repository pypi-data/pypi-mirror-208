# SPDX-License-Identifier: MIT
"""Test code.format"""

import pytest

from uc.format import UniFormat

# yapf: disable
FORMAT_CASES: list[tuple[str, str, str]] = [
    ('B',           'char',             'B'),
    ('B',           'ordinal',          '66'),
    ('B',           'name',             'LATIN CAPITAL LETTER B'),
    ('B',           'category',         'Lu'),
    ('\u05D0',      'category',         'Lo'),
    ('B',           'bidirectional',    'L'),
    ('\u05D0',      'bidirectional',    'R'),
    ('B',           'combining',        '0'),
    ('B',           'east_asian_width', 'Na'),
    ('\u05D0',      'east_asian_width', 'N'),
    ('\u0308',      'east_asian_width', 'A'),
    ('\u30A6',      'east_asian_width', 'W'),
    ('\uFF21',      'width',            'F'),
    ('B',           'mirrored',         '0'),
    ('(',           'mirrored',         '1'),
    ('B',           'decimal',          ''),
    ('0',           'decimal',          '0'),
    ('\U0001D7DB',  'decimal',          '3'),
    ('\U00002464',  'decimal',          ''),
    ('B',           'digit',            ''),
    ('0',           'digit',            '0'),
    ('\U0001D7DB',  'digit',            '3'),
    ('\U00002464',  'digit',            '5'),
    ('B',           'utf8',             '42'),
    ('\u30A6',      'utf8',             'E3 82 A6'),
    ('\u00E0',      'utf8',             'C3 A0'),
    ('\u00E1',      'utf-8',            'C3 A1'),
    ('\u00E0',      'UTF8',             '[195, 160]'),
    ('\u00E1',      'UTF-8',            '[195, 161]'),
    ('B',           'utf16',            '0042'),
    ('\U0001D538',  'utf16',            'D835 DD38'),
    ('\U0001D539',  'utf-16',           'D835 DD39'),
    ('\U0001D538',  'UTF16',            '[55349, 56632]'),
    ('\U0001D539',  'UTF-16',           '[55349, 56633]'),
    ('\U0000D800',  'UTF-16',           '[]'),
    ('\u00E0',      'u',                'U+00E0'),
    ('\U0001D53A',  'u',                'U+1D53A'),
    ('\U0001D53B',  'v',                '120123'),
    ('\u00E2',      'x',                '00E2'),
    ('\U0001D53B',  'x',                '1D53B'),
    ('\u00E3',      'u5',               'U+000E3'),
    ('\u00E4',      'u7',               'U+00000E4'),
    ('\u00E8',      'decomposition',    '0065 0300'),
    ('\u00E5',      'block',            'Latin-1 Supplement'),
    ('\U0001D53C',  'id',               'MATHEMATICAL_DOUBLE_STRUCK_CAPITAL_E'),
    ('\u0340',      'NFC',              '\u0300'),
    ('\u0340',      'nfc',              'COMBINING GRAVE ACCENT'),
    ('\u01C4',      'NFKC',             'D\u017D'),
    ('\u01C4',      'nfkc',
     'LATIN CAPITAL LETTER D, LATIN CAPITAL LETTER Z WITH CARON'),
    ('\u00C0',      'NFD',              'A\u0300'),
    ('\u00C0',      'nfd',
     'LATIN CAPITAL LETTER A, COMBINING GRAVE ACCENT'),
    ('\u01C4',      'NFKD',             'DZ\u030C'),
    ('\u01C4',      'nfkd',
     'LATIN CAPITAL LETTER D, LATIN CAPITAL LETTER Z, COMBINING CARON'),
]
# yapf: enable

@pytest.mark.parametrize('character,key,result', FORMAT_CASES)
def test_uni_format_init(character, key, result):
    u = UniFormat(character)
    assert u[key] == result

def test_uni_format_key_error():
    u = UniFormat('X')
    with pytest.raises(KeyError):
        _ = u['probably not a valid key']

def test_uni_format_eol():
    u = UniFormat('X', eol='Y')
    assert u['eol'] == 'Y'
    assert '{char}{eol}ZZ{eol}'.format_map(u) == 'XYZZY'

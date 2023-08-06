# SPDX-License-Identifier: MIT
"""Test uni command"""

import uni

def test_no_args(capsys):
    status = uni.main(['uni'])
    out = capsys.readouterr().out
    assert status != 0
    assert 'uni' in out
    assert '--help' in out

def test_character(capsys):
    status = uni.main(['uni', 'a'])
    assert status == 0
    assert capsys.readouterr().out == 'a U+0061 LATIN SMALL LETTER A\n'

def test_character_bad(capsys):
    status = uni.main(['uni', 'xyzzy'])
    assert status != 0
    assert 'xyzzy' in capsys.readouterr().err

def test_character_name(capsys):
    status = uni.main(['uni', 'Latin small letter A'])
    assert status == 0
    assert capsys.readouterr().out == 'a U+0061 LATIN SMALL LETTER A\n'

def test_block(capsys):
    status = uni.main(['uni', '--block', 'ASCII', '--char', '-n'])
    assert status == 0
    assert capsys.readouterr().out == ('\x00\x01\x02\x03\x04\x05\x06\x07'
                                       '\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F'
                                       '\x10\x11\x12\x13\x14\x15\x16\x17'
                                       '\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F'
                                       ' !"#$%&\'()*+,-./0123456789:;<=>?'
                                       '@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_'
                                       '`abcdefghijklmnopqrstuvwxyz{|}~\x7F')

def test_block_bad(capsys):
    status = uni.main(['uni', '--block', 'this is not a block or a pipe'])
    assert status != 0
    err = capsys.readouterr().err
    assert 'block' in err
    assert 'pipe' in err

def test_search(capsys):
    status = uni.main(['uni', '-w', 'indicator', 'feminine', 'ordinal'])
    assert status == 0
    assert capsys.readouterr().out == (
        '\u00AA U+00AA FEMININE ORDINAL INDICATOR\n')

def test_properties(capsys):
    status = uni.main(
        ['uni', '--char', '-n', '--mirrored', '1', '--category', 'So'])
    assert status == 0
    assert '\u2BFE' in capsys.readouterr().out

def test_eol_nul(capsys):
    status = uni.main(['uni', '--char', '-0', 'a', 'b'])
    assert status == 0
    assert capsys.readouterr().out == 'a\0b'

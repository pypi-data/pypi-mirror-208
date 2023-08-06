#!/usr/bin/env python
# SPDX-License-Identifier: MIT

import argparse
import itertools
import pathlib
import sys

from collections.abc import Iterable

import uc.uni
import uc.block
import uc.format
import uc.search

SELF = 'uni'
error_count = 0

def error(s):
    global error_count
    error_count += 1
    print(f'{SELF}: {s}', file=sys.stderr)

def unichr_e(value) -> str | None:
    try:
        return uc.uni.unichr(value)
    except ValueError:
        error(f'No character {repr(value)}')
        return None

def unicode_points(
        blocks: Iterable[uc.block.UniBlock] | None = None) -> Iterable[int]:
    """Returns a sequence of all Unicode points in the blocks."""
    if blocks:
        source: Iterable[int] = itertools.chain.from_iterable(
            (b.range for b in blocks))
    else:
        source = range(sys.maxunicode + 1)
    return source

def unicode_chars(
        blocks: Iterable[uc.block.UniBlock] | None = None) -> Iterable[str]:
    """Returns a map of all Unicode character names in the blocks."""
    return (chr(i) for i in unicode_points(blocks))

CANNED_FORMATS = {
    'char': ('print the character', '{char}'),
    'name': ('print the character name', '{name}'),
    'short': ('print the character, code, and name', '{char} {u} {name}'),
    'long': ('print full details about the character',
             ('Character  {char}{eol}'
              'Name       {name}{eol}'
              'Ordinal    {ordinal:<16} {x}{eol}'
              'Block      {block}{eol}'
              'Category   {category}{eol}'
              'Decimal    {decimal}{eol}'
              'Digit      {digit}{eol}'
              'Bidi       {bidirectional}{eol}'
              'Combining  {combining}{eol}'
              'Width      {east_asian_width}{eol}'
              'Mirrored   {mirrored}{eol}'
              'Decomp     {DECOMPOSITION!s:16} {decomposition}{eol}'
              'NFC        {NFC:16} {nfc}{eol}'
              'NFKC       {NFKC:16} {nfkc}{eol}'
              'NFD        {NFD:16} {nfd}{eol}'
              'NFKD       {NFKD:16} {nfkd}{eol}'
              'UTF-8      {UTF8!s:16} {utf8}{eol}'
              'UTF-16     {UTF16!s:16} {utf16}{eol}')),
    'compose': ('print for XCompose', ': "{char}"   U{x} # {name}'),
}

PROPS = (
    'bidi',
    'category',
    'combining',
    'decimal',
    'decomposition',
    'digit',
    'mirrored',
    'numeric',
    'width',
)

def main(argv: list[str] | None = None):
    if argv is None:
        argv = sys.argv  # pragma: no cover
    global SELF
    SELF = pathlib.Path(argv[0]).stem
    global error_count
    error_count = 0

    parser = argparse.ArgumentParser(prog=SELF)
    search_group = parser.add_argument_group('search options')
    anyall = search_group.add_mutually_exclusive_group()
    anyall.add_argument(
        '--all',
        help='require all conditions',
        action='store_const',
        dest='fold',
        const=all,
        default=all)
    anyall.add_argument(
        '--any',
        '-a',
        help='allow any condition',
        action='store_const',
        dest='fold',
        const=any,
        default=all)
    search = search_group.add_mutually_exclusive_group()
    search.add_argument(
        '--egrep',
        '-e',
        help='search names using extended regular expressions',
        action='store_const',
        dest='search',
        const='egrep')
    search.add_argument(
        '--glob',
        '-g',
        help='search names using shell glob patterns',
        action='store_const',
        dest='search',
        const='glob')
    search.add_argument(
        '--match',
        '-m',
        help='search names using text anywhere',
        action='store_const',
        dest='search',
        const='match')
    search.add_argument(
        '--word',
        '-w',
        help='search names using full words',
        action='store_const',
        dest='search',
        const='word')

    prop_group = parser.add_argument_group('property match options')
    prop_group.add_argument(
        '--block',
        '-b',
        action='append',
        help='limit to the given Unicode block')
    for p in PROPS:
        prop_group.add_argument(f'--{p}', action='append')

    format_group = parser.add_argument_group('format options')
    format_group.add_argument(
        '--format',
        '-f',
        action='append',
        help='print according to a format string')
    for name, df in CANNED_FORMATS.items():
        format_group.add_argument(
            f'--{name}',
            dest='format',
            action='append_const',
            const=df[1],
            help=df[0])

    eol_group = parser.add_argument_group('end of line options')
    eol = eol_group.add_mutually_exclusive_group()
    eol.add_argument(
        '--nonewline',
        '-n',
        action='store_const',
        dest='eol',
        const='',
        default='\n')
    eol.add_argument('-s', '--separator', dest='eol')
    eol.add_argument(
        '-0', '--null', action='store_const', dest='eol', const=chr(0))

    parser.add_argument(
        'character',
        nargs=argparse.REMAINDER,
        help='character, name, or search pattern')
    args = parser.parse_args(argv[1 :])

    props = []
    for p in PROPS:
        if (pp := getattr(args, p, [])):
            for v in pp:
                props.append((p, v))

    blocks = []
    if args.block is not None:
        for b in args.block:
            try:
                blocks.append(uc.block.UniBlock(b))
            except ValueError as e:
                error(e)
                return error_count

    chrs: Iterable[str]
    if args.character:
        if args.search:
            chrs = uc.search.search_name(args.search, args.character,
                                         unicode_chars(blocks), args.fold)
        else:
            cc = (unichr_e(name) for name in args.character)
            chrs = (
                c for c in cc
                if c and ((any((c in b for b in blocks)) if blocks else True)))
    elif blocks:
        chrs = unicode_chars(blocks)
    elif props:
        chrs = unicode_chars()
    else:
        parser.print_help()
        return 1

    if props:
        chrs = (
            c for c in chrs if args.fold(
                str(uc.uni.PROPERTIES[p](c, '')) == v for p, v in props))

    if not args.format:
        args.format = [CANNED_FORMATS['short'][1]]
    sep = False
    for c in chrs:
        if sep:
            print(end=args.eol)
        sep = True
        for f in args.format:
            print(f.format_map(uc.format.UniFormat(c)), end='')

    if args.eol and args.eol != chr(0):
        print(end=args.eol)

    return error_count

if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))

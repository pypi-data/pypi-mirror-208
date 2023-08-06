# uni

## NAME

uni - display Unicode character information

## SYNOPSIS

**uni** [_option_]... [_character_]...

## DESCRIPTION

Displays information about Unicode characters.

In the absence of a name match option, each _character_ option can
independently be any one of:

- a single character;
- an integer code point number;
- a character name;
- the form `U+`_hexdigits_.

### NAME MATCH OPTIONS

#### `--egrep`, `-e`

The _character_ arguments are extended regular expressions, matched against
character names.

#### `--glob`, `-g`

The _character_ arguments are shell-style patterns, matched against character
names.

#### `--match`, `-m`

The _character_ arguments are text that can match anywhere in a character
name.

#### `--word`, `-w`

The _character_ arguments are full words that must appear in a character name.

### BLOCK MATCH OPTION

#### `--block=`_block_, `-b` _block_

Limits matches to characters within the given _block_(s). (Unlike other match
options, this is always restrictive even with `--any`.) A _block_ can be a
Unicode block name. It can also be any of the _character_ forms, designating
the block containing that character.

### PROPERTY MATCH OPTIONS

Currently, these are not user-friendly; the argument must exactly match
the form returned by Python `unicodedata`.

- `--bidi=`_bidi_
- `--category=`_category_
- `--combining=`_combining_
- `--decimal=`_decimal_
- `--decomposition=`_decomposition_
- `--digit=`_digit_
- `--mirrored=`_mirrored_
- `--numeric=`_numeric_
- `--width=`_width_

### GENERAL MATCH OPTIONS

#### `--all`

Given multiple match conditions, all must apply in order for a character to
be selected. This is the default.

#### `--any`, `-a`

Given multiple match conditions, any single match is sufficient for a character
to be selected.

### FORMAT OPTIONS

#### `--format=`_format_, `-f` _format_

Print according to a format string. The string may contain keywords
surrounded by curly braces, and other text printed as-is.

The keywords are:

- `{bidirectional}` - the character's bidirectional class.
- `{block}` - the name of the block containing the character.
- `{category}` - the character's category.
- `{char}` - the character.
- `{combining}` - the character's combining value.
- `{decimal}` - the character's decimal value.
- `{decomposition}` - the character's decomposition.
- `{digit}` - the character's digit value.
- `{eol}` - the end-of-line character (newline unless changed by command-line options).
- `{id}` - the character name with blanks and hyphends replaced by ‘`_`’.
- `{mirrored}` - whether the character is mirrored in bidirectional text.
- `{name}` - the character's name.
- `{nfc}` - the NFC normalization form, as character names.
- `{NFC}` - the NFC normalization form.
- `{nfd}` - the NFD normalization form, as character names.
- `{NFD}` - the NFD normalization form.
- `{nfkc}` - the NFKC normalization form, as character names.
- `{NFKC}` - the NFKC normalization form.
- `{nfkd}` - the NFKD normalization form, as character names.
- `{NFKD}` - the NFKD normalization form.
- `{numeric}` - the character's numeric value.
- `{ordinal}` - the character's code point number.
- `{utf8}` - the UTF-8 encoding of the character, as a sequence of two-digit hexadecimal numbers.
- `{utf16}` - the UTF-16 encoding of the character, as one or two four-digit hexadecimal numbers.
- `{u}` - the code point number, in the form `U+`_hexdigits_.
- `{u`_n_`}` - as `{u}`, but zero-padded to at least _n_ digits.
- `{v}` - the code point number, in decimal.
- `{width}` - the character's width class (‘East Asian width’).
- `{x}` - the code point number, in hexdecimal (with no prefix).

#### `--char`

Print the character alone.
Equivalent to `--format '{char}'`.

#### `--compose`

Print in a form useful in XCompose files.
Equivalent to `--format ': "{char}"   U{x} # {name}'`.

#### `--long`

Print full details about the character

#### `--name`

Print the character name.
Equivalent to `--format '{name}'`.

#### `--short`

Print the character, code, and name. This is the default.
Equivalent to `--format '{char} {u} {name}'`.

### SEPARATOR OPTIONS

#### `--nonewline`, `-n`

Do not print a newline between output for different characters.

#### `--separator=`_eol_, `-s` _eol_

Print _eol_ between output for different characters.

#### `--null`, `-0`

Print an ASCII NUL between output for different characters.

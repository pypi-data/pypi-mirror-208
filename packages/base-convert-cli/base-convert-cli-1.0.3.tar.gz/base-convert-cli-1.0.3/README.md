## Description
A CLI tool to convert numbers between bases, with as little typing as possible.

```
$ bs FFFE
[from hexadecimal]
  decimal     65534
  binary      1111111111111110
  octal       177776
$ bs -t d F
15
```

## Installation
This is a Python 3 script, installed from [PyPI](https://pypi.org/project/base-convert-cli/) using pip.

```
pip3 install base-convert-cli
```

Hasn't been tested on Windows.

## Examples
If you don't specify a base, it does all common conversions.

```
$ bs 0
[from decimal]
  binary      0
  hexadecimal 0
  octal       0

[from binary]
<clipped output here>
```

Specify the base through the prefix `0b` for binary, `0o` for octal, `0d` for decimal and `0x` for hex.

```
$ bs 0xF
bs 0xF
[from hexadecimal]
  decimal     15
  binary      1111
  octal       17

```

Specifying base through a flag.

```
$ bs --from hex F
[from hexadecimal]
  decimal     15
  binary      1111
  octal       17
```

From base-36 (the maximum supported base, which uses the digits 0-9 and then a-z).

```
$ bs --from 36 zx1
[from base-36]
  decimal     46549
  binary      1011010111010101
  hexadecimal B5D5
  octal       132725
```

To base-7.

```
$ bs --to 7 54
[from decimal]
  base-7 105

[from hexadecimal]
  base-7 150

[from octal]
  base-7 62
```

Specifying both input and output bases.

```
$ bs --from hex --to dec F
15
```

Shorthand for lazy people.

```
$ bs -f h -t d F
15
```

Padding with zeroes.

```
$ bs --from decimal --to binary --pad 8 14
00001110
```

Setting precision for converting fractional numbers.

```
$ bs --prec 10 --from 3 --to decimal 0.1
0.3333333333
```

Aaaaand input through a pipe.

```
$ echo '5+10' | bc | bs -t h
[from decimal]
  hexadecimal F

[from octal]
  hexadecimal D
```

## Contributing
Feel free to submit tweaks. To run tests, install tox via `pip3 install tox` and then run the `tox` command from the base directory.

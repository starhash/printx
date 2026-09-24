# printx

Color and style terminal output in Python using inline markup tags.

```python
from printx import printx

printx("<:green:b 'PASS'> 12 checks finished in <:cyan '0.4s'>")
```

printx is a single Python file with no dependencies. You put tags such as `<:red:b 'text'>` inside ordinary strings, and printx turns them into ANSI escape codes. You can also name your own reusable pieces of text (short codes) and text transformations (macros).

## Features

- **Inline markup**: style any part of a string without assembling escape codes by hand.
- **Colors**: 8 colors in normal and bright versions, for text and background, plus the 256-color palette.
- **Text styles**: bold, dim, italic, underline, strikethrough, reverse, conceal and blink.
- **Layout**: fixed widths with left, right or center alignment, plus padding, tabs and line breaks.
- **Short codes**: name a piece of text (tags included) and reuse it anywhere.
- **Macros**: name a function and use it to transform a tag's text.
- **Print or return**: print straight away, or get the formatted string back.
- **No dependencies**: one file, standard library only.

## Requirements

- Python 3 (tested on 3.10 to 3.13)
- A terminal that understands ANSI escape codes, such as most Linux and macOS terminals, or Windows Terminal

## Installation

This repository is the `printx` package itself: all of the code is in `__init__.py`. Put a copy in a folder named `printx` that your code can import from:

```bash
# clone it next to your script
git clone https://github.com/starhash/printx.git

# or add it to your own git repository as a submodule
git submodule add https://github.com/starhash/printx.git printx
```

Because it's a single file, you can also copy `__init__.py` into your project and rename it `printx.py`. Either way, you import it like this:

```python
from printx import printx, enableShortCode, enableMacro
```

> **Note:** printx isn't on PyPI. The `printx` package there is an unrelated project.

## Quick start

```python
from printx import printx

printx("<:red:b 'error:'> config file not found")            # "error:" in bold red
printx("<:u 'Summary'>")                                     # underlined
printx("<:xblue:lwhite ' INFO '> listening on port", 8080)   # white on blue, then plain text
```

`printx()` works like `print()`: it joins its arguments with spaces and converts anything that isn't a string with `str()`. Tags work in every string argument, and one string can contain any number of tags.

## Tag syntax

```text
<:code:code:... 'text'>    style a piece of text
<:code:code:...>           a tag without text, used for short codes and macros
```

- A tag starts with `<:`. Codes are separated by colons and applied from left to right.
- The text goes in single quotes, after at least one space. It can contain spaces, colons and apostrophes, but not `>`.
- Every tag resets all styling when it ends, so styles never spill into the text that follows. This also means `<:red>text` doesn't color `text`.

## Colors and styles

### Colors

| Color | Text | Bright text | Background | Bright background |
| --- | --- | --- | --- | --- |
| black | `black` | `lblack` | `xblack` | `xbblack` |
| red | `red` | `lred` | `xred` | `xbred` |
| green | `green` | `lgreen` | `xgreen` | `xbgreen` |
| yellow | `yellow` | `lyellow` | `xyellow` | `xbyellow` |
| blue | `blue` | `lblue` | `xblue` | `xbblue` |
| magenta | `magenta` | `lmagenta` | `xmagenta` | `xbmagenta` |
| cyan | `cyan` | `lcyan` | `xcyan` | `xbcyan` |
| white | `white` | `lwhite` | `xwhite` | `xbwhite` |

The plain name sets the text color. Add `l` (light) in front for the bright version, `x` for the background, or `xb` for a bright background.

```python
printx("<:lyellow 'bright yellow text'>")
printx("<:xred:lwhite:b ' ALERT '>")   # bold bright white on red
```

### Text styles

| Code | Style |
| --- | --- |
| `b` | bold |
| `xb` | dim |
| `i` | italic |
| `u` | underline |
| `s` | strikethrough |
| `x` | reverse: swap the text and background colors |
| `c` | conceal: hide the text |
| `blink` | slow blink |
| `xblink` | fast blink |
| `z` | reset |

Terminals differ in which styles they support. Italic, blink and conceal are the most likely to be missing.

```python
printx("<:b 'bold'>", "<:i 'italic'>", "<:u 'underlined'>", "<:s 'struck out'>")
```

### 256 colors

`bg<N>` and `fg<N>` pick color `N` (0 to 255) from the terminal's 256-color palette.

> **Note:** the names are currently the wrong way round: `bg<N>` sets the **text** color and `fg<N>` sets the **background**.

```python
printx("<:bg208 'orange text'>")
printx("<:fg22:lwhite ' dark green background '>")
```

## Layout

| Code | Effect |
| --- | --- |
| `len<N>` | pad the text with spaces to at least `N` characters (longer text isn't cut) |
| `left`, `right`, `center` | where the text sits inside `len<N>` (the default is `left`) |
| `pad<N>` | add `N` spaces on each side |
| `tab<N>` | add `N` tab characters before the text |
| `lf` | start a new line before the tag |
| `plf` | start a new line at the beginning of the tag's text |

The added spaces are styled along with the text, so they take on its background color. That makes `len<N>` and `pad<N>` handy for banners and badges:

```python
printx("<:xblue:lwhite:b:len24:center 'Build report'>")
printx("<:xgreen:black:pad1 'PASS'>", "unit tests")
printx("<:xred:lwhite:pad1 'FAIL'>", "integration tests")
```

## Short codes

A short code gives a piece of text a name. Register it once with `enableShortCode(name, text)`, then write `<:name>` wherever you want the text. The text can contain tags of its own, and you can style a short code like any other text.

```python
from printx import printx, enableShortCode

enableShortCode("ok", "<:green:b 'OK'>")
enableShortCode("fail", "<:red:b 'FAIL'>")
enableShortCode("tick", "✔")

printx("<:ok> database reachable")
printx("<:fail> cache timed out")
printx("<:green:tick> all done")
```

## Macros

A macro gives a function a name. Register it with `enableMacro(name, function)`. printx calls the function with the tag's text and uses the string it returns instead. That string can contain tags, so a macro can also give a combination of styles a name.

```python
from printx import printx, enableMacro, enableShortCode

enableMacro("upper", str.upper)
enableMacro("money", lambda text: f"${float(text):,.2f}")
enableMacro("error", lambda text: f"<:red:b '{text}'>")

printx("<:upper:b 'warning'> low disk space")   # "WARNING" in bold
printx("Total:", "<:green:money '1234.5'>")      # "$1,234.50" in green
printx("<:error 'disk full'>")                   # same as <:red:b 'disk full'>

# codes run left to right, so a macro can transform a short code's text
enableShortCode("status", "ready")
printx("<:status:upper>")                        # "READY"
```

### Naming rules

These rules apply to both short codes and macros:

- Names can contain letters, digits and underscores.
- A name can only be registered once. Registering it again is silently ignored.
- Some names are taken by built-in codes and won't work, and some of them raise an error:
  - names that start with `bg`, `fg`, `pad`, `len` or `tab`
  - `center`, `left`, `right`, `lf` and `plf`
- Short codes and macros take priority over the color and style codes, so a short code named `red` replaces the color.

## Options

`printx()` accepts these keyword arguments:

| Argument | Effect |
| --- | --- |
| `ret=True` | return the formatted string instead of printing it |
| `lf=True` | don't end the output with a newline, and flush it straight away |
| `force_empty=False` | print nothing if the output has no visible text |
| `print=False` | do nothing and return `None`, even with `ret=True` |

```python
label = printx("<:b 'Name:'>", ret=True)   # a str containing ANSI escape codes

printx("Downloading...", lf=True)
printx("<:green 'done'>")                  # the line reads "Downloading... done"

verbose = False
printx("<:xb 'debug details'>", print=verbose)   # printed only when verbose is True
```

Other `print()` arguments such as `sep`, `end` and `file` aren't supported and are ignored, so output always goes to standard output.

## Recipes

### Aligned table

```python
from printx import printx

servers = [("alpha", 12), ("bravo", 87), ("charlie", 240)]

printx("<:b:len10 'Server'>", "<:b:len8:right 'Latency'>")
for name, ms in servers:
    color = "green" if ms < 50 else "yellow" if ms < 200 else "red"
    printx(f"<:len10 '{name}'>", f"<:{color}:len8:right '{ms} ms'>")
```

### Progress on one line

```python
import time
from printx import printx

printx("Processing", lf=True)
for _ in range(3):
    time.sleep(0.5)
    printx("<:cyan '.'>", lf=True)
printx("<:green:b 'done'>")
```

## Known limitations

- **No nesting.** Each tag resets all styling when it ends, so in `<:red 'a <:b 'b'> c'>` the final ` c` isn't red. Put the tags side by side instead: `<:red 'a '><:red:b 'b'><:red ' c'>`.
- **No `>` in tag text.** A tag whose text contains `>` is printed as it is.
- **Text that looks like a tag is read as one.** An unknown code, as in `<:1>`, raises `KeyError`, and there's no way to escape a tag. Take care when printing text you don't control.
- **`bg<N>` and `fg<N>` are swapped.** See [256 colors](#256-colors).
- **`center` can be one character too wide.** When the space left over is 3, 7, 11 and so on characters, the result is one character wider than `len<N>`.
- **A trailing space is always added.** Arguments are joined with spaces and one more follows the last, so the output ends with a space. So does the string that `ret=True` returns.
- **Escape codes are always written**, even when the output is redirected to a file or a pipe.

## License

printx is released under the [MIT License](LICENSE).

# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project

- printx prints colored, styled terminal text from inline tags such as `<:red:b 'text'>`. The user documentation is `README.md`. There's no docs folder or wiki, and you shouldn't add one.
- The repository root **is** the `printx` package: all of the code is in `__init__.py`. Users clone the repo, or add it as a git submodule, into a folder named `printx`, then write `from printx import printx`. Keep this layout, and don't move the code into `src/` or a subfolder.
- Any `.py` file at the root becomes part of the package (`printx.<name>`), so don't put scripts or tests there.
- The code uses Python 3 and the standard library only. There's no test suite, CI or packaging config yet.
- This file is the only place for agent instructions. If a tool needs its own file, make that file point here rather than copying these rules. For Claude Code, a `CLAUDE.md` must start with `@AGENTS.md`, because Claude Code stops reading `AGENTS.md` once a `CLAUDE.md` exists.

## How the code works

Everything is in `__init__.py`:

- `SCREEN_CODES` maps code names to ANSI SGR parameters. `SHORT_CODES` and `MACROS` hold what users register with `enableShortCode()` and `enableMacro()`.
- `printx()` finds tags with two regexes, one for tags with text and one for tags without. It replaces each tag with the output of the nested `replacer()`. If the result still contains tags (for example, from a short code's text), `printx()` calls itself again with `ret=True`, then handles the keyword arguments.
- `replacer()` checks each code in this order:
  1. prefix codes (`bg`, `fg`, `pad`, `len`, `tab`)
  2. exact layout codes (`center`, `right`, `left`, `plf`, `lf`)
  3. short codes
  4. macros
  5. `SCREEN_CODES`

  The order decides which name wins, so changing it changes behavior.

## Maintaining the code

- **Keep the public API backwards compatible.** The public API is `printx()`, `enableShortCode()`, `enableMacro()`, the three module-level dicts, the tag syntax, every code name, and the keyword arguments `ret`, `lf`, `print` and `force_empty`. If a change alters visible output, even as a bug fix, say so in the commit body.
- **Keep changes small and local.** Stay in one file with no dependencies, and match the existing style (camelCase public functions, 4-space indents). Don't reformat, rename or reorder code you aren't changing.
- **Keep the CRLF line endings.** `__init__.py` uses CRLF. Never mix a line-ending change with a code change. After editing, `git diff --stat` should count only the lines you meant to change. New files use LF.
- **Update README.md in the same commit** when codes, options or behavior change, including its *Known limitations* section. The README is for users, so don't mention agents or AI tools in it.
- **Verify every change.** Exercise each code path you touched before and after the change, and compare the exact output with `repr()`. The checkout folder must be named `printx`. Run this from its parent directory:

  ```bash
  cd .. && python3 -c "from printx import printx; print(repr(printx(\"<:red:b 'hi'>\", ret=True)))"
  ```

  If the change touches anything the README examples use, run those examples too. If you add tests, put them in a `tests/` folder and use the standard library's `unittest`.

## Known bugs

These bugs reproduce on Python 3.10 to 3.13. Don't fix them as a side effect of other work: fix one only when asked, and one per commit. After a fix, update README's *Known limitations* and remove the bug from this list.

1. `bg<N>` emits `38;5;N`, which sets the text color, and `fg<N>` emits `48;5;N`, which sets the background. The names are swapped.
2. `center` splits the padding with `round()`, which rounds halves to the nearest even number. When the padding needed is 3, 7, 11 and so on, the result is one character wider than `len<N>`.
3. An unknown code raises `KeyError` from the final `SCREEN_CODES` lookup, so printed text that looks like a tag can crash `printx()`. There's no way to escape a tag.
4. Short code and macro names that start with `bg`, `fg`, `pad`, `len` or `tab` are read as those codes. For `pad`, `len` and `tab`, `int()` then raises `ValueError`. The names `center`, `left`, `right`, `lf` and `plf` are taken by the layout codes.
5. `print=False` is checked before `ret=True`, so passing both returns `None`.
6. `sep`, `end` and `file` are silently dropped.
7. `inspect` and `os` are imported but never used.

## Commit messages

Every commit uses this format:

```text
<type>: <summary>
[<tool> using <model> (<effort>)]

- <change>
- <change>
```

- **Subject:** the type in lowercase, a colon, then a short summary in the imperative mood that starts with a lowercase letter and has no full stop. The types are:
  - `feat`: new behavior
  - `fix`: a bug fix
  - `refactor`
  - `docs`: README only
  - `test`
  - `build`: packaging and releases
  - `chore`: housekeeping, such as `.gitignore` or the license
  - `agent`: agent configuration, such as this file
- **Attribution:** in commits written by an agent, the second line names the tool, model and effort level in square brackets. Leave out the effort if the tool has no such setting. Commits written by a person skip this line. This line is the whole attribution, so don't add tool-generated trailers such as `Co-Authored-By:`.
- **Body:** a blank line, then one bullet per change, each starting with a lowercase verb in the past tense (`added`, `fixed`, …).
- **Case:** keep file names, code names and acronyms as they are, such as `README.md` or `MIT`.

Example:

```text
agent: configure repository for agentic tools
[Claude Code using Opus 5.5 (Max)]

- added README.md and AGENTS.md
```

## Releasing a wheel

Only release when the owner asks. Never upload to PyPI or publish a GitHub release without the owner's explicit approval.

### First release: add packaging

1. **Ask the owner for the distribution name.** The name `printx` on PyPI belongs to an unrelated project. The import name stays `printx`, whatever the distribution is called.
2. **Add `pyproject.toml`** at the root. The root is the package, so the config has to map it explicitly. This config has been tested: it builds a wheel that contains only `printx/__init__.py` plus metadata.

   ```toml
   [build-system]
   requires = ["setuptools>=77"]
   build-backend = "setuptools.build_meta"

   [project]
   name = "<distribution name>"
   version = "0.1.0"
   description = "Color and style terminal output using inline markup tags"
   readme = "README.md"
   license = "MIT"
   license-files = ["LICENSE"]
   requires-python = ">=3.10"
   authors = [{ name = "starhash" }]

   [tool.setuptools]
   package-dir = { printx = "." }
   packages = ["printx"]
   include-package-data = false
   ```

3. **Ignore the build outputs.** Add `build/`, `dist/` and `*.egg-info/` to `.gitignore`.
4. **Update the Installation section of the README** with the new install command.

### Every release

1. **Bump `version`** in `pyproject.toml`. Follow semantic versioning: a patch release for fixes, a minor release for new codes or options, and a major release for breaking changes.
2. **Build the wheel:**

   ```bash
   rm -rf build dist *.egg-info
   python3 -m pip wheel . --no-deps --wheel-dir dist
   ```

3. **Check the wheel.** List its contents, which should be only `printx/__init__.py` and the `.dist-info` files. Then install it into a fresh virtual environment and import it from outside the checkout:

   ```bash
   python3 -m zipfile -l dist/*.whl
   python3 -m venv /tmp/printx-wheel-check
   /tmp/printx-wheel-check/bin/pip install dist/*.whl
   (cd /tmp && /tmp/printx-wheel-check/bin/python -c "from printx import printx; printx(\"<:green 'ok'>\")")
   ```

4. **Commit and tag.** Commit as `build: release vX.Y.Z`, create an annotated tag `vX.Y.Z`, then push the commit and the tag.
5. **Publish, if the owner has approved it.** Attach the wheel to a GitHub release, or upload it to PyPI with `twine`.

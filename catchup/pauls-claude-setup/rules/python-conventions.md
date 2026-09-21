---
paths:
  - "**/*.py"
  - "**/*.ipynb"
---

# Python Conventions

## Package Manager

`uv` is the sole Python package manager. Install with
`uv sync --all-extras`; run with `uv run python`. Never use
bare `pip install` or direct `.venv` Python paths.

## General Style (PEP 8)

- Indentation: 4 spaces; never tabs.
- Line length: 88 characters maximum (compatible with black formatting).
- Imports: one module per `import` statement (no `import os, sys`); `from x
  import a, b` is acceptable when it fits within 88 characters; grouped in
  this order -- standard library, third-party packages, local modules -- with
  a blank line separating each group. No wildcard imports (`from x import *`).
- Naming: `snake_case` for variables, functions, and modules;
  `PascalCase` for classes; `UPPER_SNAKE_CASE` for module-level constants.
- Blank lines: two blank lines before and after top-level function and class
  definitions; one blank line between methods inside a class.
- Strings: prefer double quotes consistently.
- Type hints: include for all function signatures when writing reusable
  functions or utility modules; optional but encouraged for notebook-level
  helper functions.
- Do not leave commented-out code blocks in final deliverables; remove or
  document them explicitly.

## File Encoding

This section matters mainly on Windows. There, Python defaults to CP-1252
when the `PYTHONUTF8` environment variable is not set, so a single `open()`
call without an explicit encoding can silently re-encode non-ASCII
characters (em-dashes, curly quotes, arrows, umlauts) as mojibake. macOS
and Linux default to UTF-8, but the rules below cost nothing there and keep
files portable across systems:

- Always pass `encoding="utf-8"` to `open()`, `Path.read_text()`,
  `Path.write_text()`, `pd.read_csv()`, `pd.read_excel()`,
  `json.load()` / `json.dump()`, and any other file I/O call that
  accepts an encoding parameter.
- When round-tripping a file (read then write back), preserve the
  original encoding. Never decode as one encoding and write as another.
- When writing JSON -- including `.ipynb` files -- use
  `ensure_ascii=False` so that non-ASCII characters are stored as
  literal UTF-8 rather than `\uXXXX` escapes.
- Prefer `newline="\n"` on the write side for cross-platform
  consistency; never mix `\r\n` and `\n` within a single file.

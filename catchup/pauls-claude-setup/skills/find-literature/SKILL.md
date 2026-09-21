---
name: find-literature
description: Cite, find reference, bibliography, BibTeX, Zotero search, locate PDF of a work.
disable-model-invocation: false
argument-hint: "<search term>"
---

# find-literature

Turn a search term into citations drawn from the live Zotero library. Reads
through Zotero's local HTTP API (clean CSL-JSON, the sanctioned read path) and,
for `--with-paths`, resolves attachment file paths through the same local API.
Never writes to Zotero.

## Prerequisite

Zotero must be running with its local API enabled. If the API on port 23119 is
unreachable, `cite.py` starts Zotero itself, waits up to 30 s for the API, and
retries the query once. It looks for Zotero at the default install location:
`C:\Program Files\Zotero\zotero.exe` on Windows,
`/Applications/Zotero.app/Contents/MacOS/zotero` on macOS, and `zotero` on
PATH elsewhere. Set `ZOTERO_EXE` to point at a different install. A connection
error therefore only surfaces when Zotero is missing at that path or fails to
come up. In that case, start it by hand:

```powershell
# Windows
Start-Process "C:\Program Files\Zotero\zotero.exe"
```

```bash
# macOS
open -a Zotero
```

See `zotero_doc.md` in this skill folder for the one-time setup and how reads
work. If the library is not at the default `~/Zotero` (your home folder plus
`Zotero`), set `ZOTERO_DATA_DIR` before running.

## Running the script

This skill is a uv project. Once, from the skill directory, run `uv sync` to
materialize the locked environment; thereafter run the script with `uv run` from
the skill directory (usually `~/.claude/skills/find-literature`):

```bash
uv run python scripts/cite.py "<search term>" [options]
```

From another working directory, target the skill explicitly:

```bash
uv run --directory ~/.claude/skills/find-literature python scripts/cite.py "<search term>" [options]
```

When invoked from inside another project's session, an active `VIRTUAL_ENV`
(that project's `.venv`) prints a harmless `VIRTUAL_ENV ... will be ignored`
warning — uv uses this skill's own environment regardless. After the one-time
`uv sync`, add `--no-sync` to skip the per-run sync and avoid that churn:

```bash
uv run --no-sync python scripts/cite.py "<search term>" [options]
```

Troubleshooting: a transient `error: Failed to install ... .whl` (a uv cache
miss, e.g. on `certifi`) is environmental, not a script fault — re-run the
command, or clear the cache once with `uv cache clean` and retry. A
`No Python at '...'` error means the venv's interpreter was removed (e.g.
after a Python-install cleanup): delete `.venv` and re-run `uv sync` against
the latest installed Python (e.g. `uv sync -p 3.14`).

**Read [arguments.md](arguments.md) for the full argument reference.**

Examples:

```bash
uv run python scripts/cite.py "Putnam social capital" --format chicago
uv run python scripts/cite.py "Granovetter 1973" --with-paths
uv run python scripts/cite.py "inequality" --format bibtex --out refs.bib
uv run python scripts/cite.py "Bourdieu" --format all
```

The search term is Zotero's quicksearch over title, creator, and year. Narrow
broad terms by adding an author surname or year.

## Filtering by facet tags

If the library is tagged with a faceted controlled vocabulary (applied by the
`zotero-curator` Mode C pass): `topic:: period:: region:: source-type::
project:: method:: discipline:: lang::`, plus free-form un-prefixed tags,
thematic retrieval becomes precise. You can slice the library by subject, era,
place, source kind, project, method, discipline, or language rather than
guessing keywords. The vocabulary's single source of truth is
`~/.claude/skills/zotero-curator/tag_vocabulary.yaml`. Without facet tags,
`--tag` still filters on any exact tag name in your library.

```bash
# discover available values for a facet
uv run python scripts/cite.py --list-tags region::

# all survey studies about Switzerland (tags AND-combined)
uv run python scripts/cite.py --tag method::survey --tag region::switzerland

# combine a quicksearch term with a facet filter
uv run python scripts/cite.py "mobility" --tag period::1945-1990 --with-paths
```

Prefer `--list-tags` (or the vocabulary file) to confirm a value before
filtering; tag names are exact and case-sensitive.

## Inserting into documents

1. Run `cite.py` with the format the target document needs.
2. For a `.docx`, use a `docx` skill, if installed, and insert the rendered reference or
   the in-text citation at the requested location.
3. For Markdown/LaTeX, prefer the `bibtex` output plus Pandoc/BibLaTeX for
   publication-grade reference lists; the `chicago` output is a ready-to-paste
   author-date string for quick prose citations.

## Notes on rendering

- Chicago author-date in-text (e.g. `(Bourdieu 1984, 23)`) and bibliography
  entries come from a deterministic formatter, not a full CSL engine; the
  BibTeX + Pandoc/BibLaTeX route above is the one for typeset, fully
  CSL-correct lists.
- CSL-JSON is the lossless, re-stylable payload; prefer it when the downstream
  tool can format its own styles.
- The displayed citekey is the work's stored Better BibTeX / CSL
  `citation-key` when present, then the CSL `id`, falling back to a derived
  `AuthorYYYYword` handle. A malformed stored key is shown as-is — the garble
  lives in Zotero, not the formatter.

## Scope

Read-only. This skill never modifies the Zotero library. For deduplication and
metadata correction, ask the user to run `/zotero-curator` (user-invoked).

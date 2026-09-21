# Zotero operational notes

Shared reference for the `find-literature` and `zotero-curator` skills. Both read
the live Zotero library entirely through its local HTTP API -- metadata and
attachment file paths alike -- and never touch `zotero.sqlite`. `zotero-curator`
additionally writes, but only through a generated Run-JavaScript snippet.

## Local API (reads)

- Reads go through Zotero's local HTTP API at `http://localhost:23119`.
- Enable it once: Zotero → Edit → Settings → Advanced → "Allow other
  applications on this computer to communicate with Zotero".
- Zotero must be running. Errors:
  - `403 Local API is not enabled` → the box above is unchecked.
  - connection refused / timeout → Zotero is not running.
- Access is via pyzotero (`local=True`), pinned to HTTP/1.1 (the local server
  rejects HTTP/2). Item metadata returns as CSL-JSON, the officially sanctioned,
  schema-stable read path.

## Environment overrides

- `ZOTERO_DATA_DIR` — Zotero data directory (default `~/Zotero`, the `Zotero`
  folder in your home directory on Windows and macOS); used only to resolve
  imported (`storage/`) attachments.
- `ZOTERO_EXE` — Zotero executable that `cite.py` starts when the API is down
  (default: the standard install location on Windows and macOS, else `zotero`
  on PATH).
- `ZOTERO_BASE_DIR` — the linked-attachment base directory; a fallback for the
  rare `attachments:` relative path the API leaves relative. Normally
  auto-detected from the profile `prefs.js`
  (`extensions.zotero.baseAttachmentPath`) on Windows; set it by hand on
  macOS if you use relative linked attachments.
- `ZOTERO_LIBRARY_ID` — pyzotero library id (default `0`).
- `ZOTERO_LIBRARY_TYPE` — `user` (default) or `group`.

## Attachment file paths (local API)

Paths come from the item's children via the local API, not from SQLite. Zotero
resolves `linked_file` paths to absolute itself — it applies the linked-
attachment base directory, so a library configured with relative base paths and
one with absolute paths both yield absolute paths here. Resolution:

- `linked_file` → absolute path as returned by the API.
- imported files → `storage/<attachmentKey>/<filename>`.
- `linked_url` / web entries have no local file and are skipped.

Because reads go through the running Zotero, they are always live (no stale
snapshot) and never hit a database lock.

## Companion files beside each attachment

If you process PDFs with the `autoexcerpter` skill, its outputs sit beside
each PDF and share the PDF's stem (a naming convention such as
`Author YYYY Title.pdf` keeps them easy to find):

- `<stem>.txt` — full verbatim transcription, with a metadata header.
- `<stem>_summary.md` / `<stem>_summary.docx` — structured summary with a
  consolidated bibliography.
- `<stem>_short_summary.md` — condensed reading note.

When you need the work's text -- to confirm title-page metadata, adjudicate a
duplicate, or read the source -- prefer the sibling `<stem>.txt` over parsing
the PDF: it is cleaner, cheaper, and its header is strong ground truth for
title, author, and year. Fall back to the PDF itself when no `.txt` exists.
Derive the companions from a resolved PDF path by swapping the
extension/suffix.

## Writes: applying the generated .js (zotero-curator only)

Never write to `zotero.sqlite` directly. All writes go through the Zotero
JavaScript API via a snippet that `scripts/build_runjs.py` generates from an
approved plan. The snippet is a plain `.js` file you run once inside Zotero; it
is not "installed" anywhere and leaves no add-on behind.

How to pass and run it:

1. Generate it from the approved plan:
   `uv run python scripts/build_runjs.py plan.json --out apply.js`
2. With Zotero closed, back up `zotero.sqlite` and the `storage/` folder, then
   reopen Zotero (it must be running to execute the snippet). `Zotero.Items.merge`
   and field edits have no undo.
3. Open `apply.js` and read the embedded `PLAN` object: it lists exactly which
   items will be merged, retyped, and re-fielded. Confirm it matches intent.
4. In Zotero: Tools → Developer → Run JavaScript.
5. Tick "Run as async function" (the snippet uses `await`; without this it
   throws a syntax error).
6. Paste the entire contents of `apply.js` into the editor pane and click Run.
7. The snippet returns a JSON log -- one entry per action listing `merged`,
   `typeChanged`, `fieldsSet`, `creatorsSet`, and any `skipped` reasons. Read it
   in the result pane to confirm the outcome; nothing is printed elsewhere.

Notes:

- Apply one action first (a one-action plan, or trim `PLAN.actions` to a single
  entry) to confirm behavior before running the full batch.
- Re-running is safe: a merge whose targets are already merged logs them as
  not-found and skips them; field fixes re-apply the same values harmlessly.
- `apply.js` is a scratch artifact -- discard it once the log looks right.

## Common Zotero field names (for metadata fixes)

`date`, `publisher`, `place`, `publicationTitle` (journal), `bookTitle`
(chapter), `proceedingsTitle`, `ISBN`, `DOI`, `language`, `edition`, `volume`,
`issue`, `pages`. Creators use `creatorType` (`author`, `editor`, `translator`)
with `firstName`/`lastName`, or `name` for a single-field corporate name.

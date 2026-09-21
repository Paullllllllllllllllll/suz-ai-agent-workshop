---
name: zotero-curator
description: Curate Zotero library — dedup, metadata repair, tagging, PDF import.
disable-model-invocation: true
argument-hint: "[dedup|metadata|tag|import|both]"
---

# zotero-curator

Four curation missions over one safe write path. Detection is deterministic and
read-only; **every decision is made by a subagent**; writes happen only through
a generated Run-JavaScript snippet that uses the real Zotero API
(`Items.merge`, `setType`, `setField`, `setCreators`, `saveTx`,
`new Zotero.Item`, `Attachments.linkFromFile`), so merges stay lossless and
nothing edits `zotero.sqlite` directly.

The missions: **A (dedup)** resolves duplicate/mis-typed works via fuzzy
title/author/year matching plus an optional byte-identical attachment pass,
with subagents adjudicating each candidate. **B (metadata)** repairs sparse or
wrong fields, with web-enabled subagents reading the PDFs and looking the
works up. **C (tag)** applies a faceted controlled-vocabulary scheme and
clears legacy auto-tags. **D (import)** accessions loose PDFs: researches each
work's bibliography, renames it to "Author YYYY Title.pdf", files it into the
correct content-type subfolder of your literature folder, and creates linked
Zotero items. Modes A to C work with any Zotero library; Mode D is only for
libraries that keep PDFs as linked files in a folder outside Zotero's
`storage/`.

Write all run artifacts (plans, worklists, generated snippets, logs) to the
session scratchpad — never into this skill folder.

## Prerequisite

Zotero must be running with its local API enabled. See `zotero_doc.md` in this
skill folder for the one-time setup, environment overrides, attachment-path
resolution, and the step-by-step Run-JavaScript write path.

This skill is a uv project. Once, from the skill directory, run `uv sync` to
materialize the locked environment; thereafter run every script with `uv run`
from the skill directory (usually `~/.claude/skills/zotero-curator`):

```bash
uv run python scripts/<script>.py [args]
```

From another working directory, target the skill explicitly:

```bash
uv run --directory ~/.claude/skills/zotero-curator python scripts/<script>.py [args]
```

Troubleshooting: a `No Python at '...'` error means the venv's interpreter
was removed (e.g. after a Python-install cleanup): delete `.venv` and re-run
`uv sync` against the latest installed Python (e.g. `uv sync -p 3.14`).

## Selecting the branch

The skill argument chooses which mission(s) to run:

- `dedup` — run **Mode A only** (duplicate detection + adjudication + merges).
- `metadata` — run **Mode B only** (sparse/wrong-metadata detection + research).
- `tag` — run **Mode C only** (faceted controlled-vocabulary tagging + clearing
  the old automatic import tags). Library-wide tagging is a long, staggered run;
  it is opt-in and never part of the `both` default.
- `import` — run **Mode D only** (accession loose PDFs into the library: research
  metadata, rename + file into the literature folder, create linked Zotero
  items). Opt-in and never part of the `both` default; it adds works rather than
  curating existing ones. Requires `LIT_ROOT` (see Mode D).
- `both` (or no argument) — run **both** Mode A and Mode B, then combine their
  confirmed verdicts into one plan and apply it in a single Run-JS snippet.

When the argument is missing or ambiguous, default to `both` and state which
branches you are running. Each branch's detection script and subagent pass are
independent; only the final plan and apply step are shared. When running
`both`, key the actions by `keep` so a record that is both a merge keeper and a
metadata-fix target becomes one action rather than two.

## Mode A — Deduplicate

### A1. Detect (read-only)

```bash
uv run python scripts/scan_duplicates.py --out dup_worklist.json
```

Writes `clusters` (high-confidence groups, with `flags` like `mixed item types`
or `some members missing a year`) and `review_pairs` (weaker matches, never
auto-clustered). The script only *proposes* candidates; it decides nothing. Add
`--hash` for the byte-identical attachment pass (slower; reads files).

### A2. Adjudicate (one subagent per candidate)

For each cluster and each review pair, launch a `general-purpose` subagent on
the `sonnet` model (it has `WebSearch`/`WebFetch` and `Read` for PDFs).
**Dispatch them in batches of 5: launch five at once and wait until all five
have returned before launching the next batch.** Give each subagent the members
and their attachment PDF paths (resolve via `scan_metadata.py --with-paths`, the
`find-literature` skill, or the library folder). Each subagent must decide:

- True duplicate, or distinct editions/volumes/translations that merely share a
  title? Confirm against the PDFs' title pages and, when needed, web catalogs.
  Default to NOT merging when uncertain.
- Which member is the **keeper** (richest, correctly-typed, best attachment).
- Any **field fix** the keeper needs (corrected `itemType`, missing year, etc.).

Treat `review_pairs` the same way, more skeptically.

## Mode B — Repair metadata

### B1. Detect (read-only)

```bash
uv run python scripts/scan_metadata.py --with-paths --out meta_worklist.json
```

Flags entries that are sparse (no creators, no year, no journal/publisher for
their type) or suspect (garbled/ALL-CAPS titles, implausible years), sorted by
severity, each with its resolved `pdf_paths`.

### B2. Research (one web-enabled subagent per entry)

For each flagged entry, launch a `general-purpose` subagent on the `sonnet`
model. **Dispatch them in batches of 5: launch five at once and wait until all
five have returned before launching the next batch.** Each subagent must:

1. **Read the PDF(s)** at `pdf_paths` — the title page, verso, and colophon are
   the strongest ground truth for title, authors, year, place, and publisher.
2. **Retrieve authoritative metadata, do not recall it.** Run the lookup script
   to pull live records from OpenAlex and Crossref rather than relying on
   memory:

   ```bash
   uv run python scripts/fetch_metadata.py --doi <doi>
   uv run python scripts/fetch_metadata.py --query "<title>" --author <surname> --year <yyyy>
   ```

   It returns candidates already mapped to Zotero field names, with the DOI and
   record id. Set `CONTACT_EMAIL` to your address to use the catalogs'
   faster "polite pool" (optional). For books, gray literature, or older works
   the catalogs above may have no entry — then confirm against
   `WebSearch`/`WebFetch` of a library catalog (WorldCat/OCLC, national library
   catalogs). A DOI, year, venue, or author list must come from the PDF or one
   of these records — never from the model's own memory.
3. Return corrected Zotero fields (use Zotero field names: `date`,
   `publicationTitle`/`bookTitle`, `publisher`, `place`, `ISBN`, `DOI`,
   `language`, ...), a `creators` array, and a recommended `itemType` — quoting
   the title-page or catalog record the value came from. Return "leave" (no
   change) when neither the PDF nor a catalog confirms it; never invent a value.

## Mode C — Tag

Apply a faceted controlled vocabulary (`facet::value` manual tags) across the
library and clear the legacy automatic (type=1) import tags. The vocabulary
lives in `tag_vocabulary.yaml` at the skill root and is the single source of
truth; facets are general so the scheme outlives any one project. The shipped
file holds example values only: replace them with your own (and add your
project codes) before the first run. **Run AFTER deduplication** so the
worklist covers survivors only.

### C1. Detect (read-only)

```bash
uv run python scripts/scan_tags.py --out tag_worklist.json
```

One entry per work: `key`, `item_type`, `title`, `authors`, `date`,
`abstract`, resolved `pdf_paths`, AutoExcerpter `companion_paths`
(.txt / _summary.md /_short_summary.md beside the PDF), and the work's
`existing_auto_tags` (hints to absorb).

### C2. Tag (one subagent per small chunk)

Chunk the worklist (~8 works each) and dispatch `general-purpose` subagents on
the `sonnet` model. Launch in batches (default 10 agents), waiting between
batches per the user's cadence; checkpoint after each batch. Give each subagent
its chunk **and the full `tag_vocabulary.yaml`**. Each subagent, per work:

1. Read the companion (`.txt` head or `_summary.md`) if present, else the PDF
   front matter (title page, verso, TOC, first ~15 pp.) via pypdf (installed
   in this skill's environment) or the Read tool, plus the title/abstract
   and `existing_auto_tags` as hints.
2. Map the work to EXISTING `facet::value` tags (topic, period, region,
   source-type, project, method, discipline, lang). Where an old auto-tag
   (e.g. a Library of Congress heading such as "Emigration and immigration")
   clearly matches a facet value, fold it into that value.
3. Return JSON: `add_tags` (controlled tags), `additional` (≤ max_additional
   free-form un-prefixed tags for salient specifics), `proposed_new_values`
   (facet + value + why) for anything not yet in the vocabulary — never invent a
   controlled value, propose it — and, when the PDF filename **substantively
   misnames** the work (wrong/garbled author·year·title, or a scanner-default
   name; NOT mere stylistic title-shortening), a `rename` object
   `{att_key, current_path, suggested_filename ("Author YYYY Title.pdf"), reason}`
   using the work's `pdf_atts` for the attachment key.

Write each subagent's result to a JSON file, then assemble the plan:

```bash
uv run python scripts/tag_plan.py --results <dir> \
    --out-plan plan.json --out-proposals proposals.json --progress tag_progress.json
```

`tag_plan.py` validates every tag against the vocabulary (unknown values are
dropped to `proposals.json`, never applied), caps free-form tags, sets
`clear_auto_tags: true` per work, collects rename proposals into `renames.json`,
and maintains the resumable `tag_progress.json` checkpoint. Review
`proposals.json` and fold approved values into `tag_vocabulary.yaml` (bump
`version`).

### C3. Rename misnamed PDFs (optional, after approval)

Show the user `renames.json`. For approved entries, rename on disk (linked files
only; companions renamed alongside; reversible `rename_log.csv`) and emit a
relink map, then fold it back into the plan so tags + relink apply together.
Like Mode D, this step needs `LIT_ROOT` set to your literature folder; the
script exits with an error if it is unset. Skip it if Zotero stores your PDFs
itself.

```bash
uv run python scripts/rename_links.py --renames renames.json          # dry run
uv run python scripts/rename_links.py --renames renames.json --apply \
    --out-relink relink_map.json
uv run python scripts/tag_plan.py --results <dir> --relink relink_map.json \
    --out-plan plan.json
```

`build_runjs.py` then applies each `relink` (updates the attachment's path +
title via the Zotero API; disk files already moved). The same `relink` action
serves Mode A keepers that need renaming.

## Mode D — Import (accession new PDFs)

Bring loose PDF files into the library: research each work, rename it to the
`Author YYYY Title.pdf` convention, **move** it into the correct content-type
subfolder of your literature folder, and create a new Zotero item with a
**linked-file** attachment (the PDF stays in the literature folder; Zotero
links to it, it is not copied into `storage/`). Unlike Modes A–C this *adds*
works, so it is opt-in and never part of `both`.

Mode D is only for libraries that keep PDFs as linked files in a folder
outside Zotero's `storage/`. If Zotero stores your PDFs itself (the default),
use Zotero's own import instead. Mode D requires the `LIT_ROOT` environment
variable, set to that literature folder; there is no default, and
`place_imports.py` exits with an error if it is unset.

**Never file a PDF at the literature-folder root.** Every import goes into one
subfolder of `LIT_ROOT`. Document your taxonomy where the agent can read it,
for example in `LIT_ROOT/CLAUDE.md`, and consult it for edge cases. An example
taxonomy you can adapt:

- `Papers` — journal articles, working papers, conference papers
- `Monographs` — single- or co-authored scholarly books (secondary literature)
- `Primary_Sources` — original historical texts, classic theoretical works
  (Marx, Smith, Weber), source editions
- `Handbooks` — reference works, companions, encyclopedias
- `Textbooks` — educational/methods books
- `Anthologies_Chapters_Journal_Volumes` — edited volumes, essay collections,
  extracted chapters
- `Reviews` — book reviews

### D1. Gather candidates (read-only)

Use the PDF paths or folder the user names. If they name none, ask for the
folder (for example their Downloads folder) or find candidates with Glob
(e.g. `**/*.pdf` in that folder). Then feed the hits to:

```bash
uv run python scripts/scan_imports.py <pdf-or-folder> [...] --out import_worklist.json
```

Accepts PDF paths, a folder, or globs. Per PDF it records the absolute path,
size, MD5, page count, any embedded title/author, and a first-page text snippet,
then checks the candidate against the existing library so nothing is imported
twice: a byte-identical MD5 match against current attachments (`already_in_library`)
and a fuzzy-title match against existing works (`possible_duplicate`). Read-only:
it never moves a file or writes to Zotero.

### D2. Research (one web-enabled subagent per PDF)

For each candidate, launch a `general-purpose` subagent on the `sonnet` model
(`WebSearch`/`WebFetch`/`Read`). **Dispatch in batches of 5.** Each subagent:

1. **Read the PDF** front matter (title page, verso, colophon) at `path` — the
   strongest ground truth for title, authors, year, place, publisher.
2. **Retrieve authoritative metadata, do not recall it.** Run the lookup script
   against OpenAlex + Crossref and adopt only fields a record (or the PDF)
   confirms — the DOI especially must come from a record, never from memory:

   ```bash
   uv run python scripts/fetch_metadata.py --query "<title>" --author <surname> --year <yyyy>
   uv run python scripts/fetch_metadata.py --doi <doi>   # if the PDF prints one
   ```

   It returns candidates already mapped to Zotero field names. For works the
   catalogs do not index, confirm via `WebSearch`/`WebFetch` of a
   library catalog (WorldCat/OCLC, national library catalogs).
3. Return JSON per PDF: recommended `itemType`, a `fields` object (Zotero field
   names — `title`, `date`, `publicationTitle`/`bookTitle`, `publisher`,
   `place`, `ISBN`, `DOI`, `url`, `language`, `abstractNote`, ...), a `creators`
   array, a `suggested_filename` = `"Author YYYY Short Title.pdf"` (short title,
   no subtitle), a `subfolder` from your taxonomy (mandatory — pick the
   content type the work actually is, e.g. an article → `Papers`, a modern
   scholarly book → `Monographs`), and optional controlled `add_tags` from
   `tag_vocabulary.yaml`. Cite the PDF page or catalog record each field came
   from. Return `skip` (with reason) when the work cannot be identified or D1
   flagged it as already in the library — never invent fields.

Assemble the confirmed results into an approved JSON list, one object per PDF:
`{current_path, itemType, fields, creators, add_tags, suggested_filename,
subfolder}`. `subfolder` is required on every entry; an entry without one must
not be placed.

- **Always tag on import.** Every newly imported work must carry controlled
  `facet::value` tags from `tag_vocabulary.yaml` (never leave `add_tags` empty);
  treat tagging as part of accession, not an optional extra.

### D3. Place files + build the create plan

```bash
uv run python scripts/place_imports.py --imports approved.json          # dry run
uv run python scripts/place_imports.py --imports approved.json --apply \
    --out-plan import_plan.json --log import_move_log.csv
```

Dry run by default. With `--apply` it sanitizes each `suggested_filename`, moves
the PDF (and any AutoExcerpter companions beside it) into the entry's
`subfolder` under `LIT_ROOT` (the script treats `subfolder` as optional, but
every approved entry must carry one — see the taxonomy), resolving name
collisions, writes a reversible
`import_move_log.csv`, and emits `import_plan.json` = `{ "creates": [ {itemType,
fields, creators, add_tags, path} ] }` with each `path` the file's final
absolute location.

### D4. Generate + apply the Run-JS

```bash
uv run python scripts/build_runjs.py import_plan.json --out import.js
```

`build_runjs.py` reads the `creates` array and emits a snippet that, per entry,
creates a new item, sets its fields/creators/tags, saves it, and attaches the
moved PDF as a linked file via `Zotero.Attachments.linkFromFile`. Show the user
`import.js`; they run it via Tools → Developer → Run JavaScript with "Run as
async function" checked. Test on one PDF first.

## Apply (all modes, user-run)

Assemble the confirmed verdicts into one plan JSON. An action may merge, fix
fields, replace creators, tag, or any combination:

```json
{
  "actions": [
    { "keep": "ABCD1234", "merge": ["EFGH5678"], "field_fixes": { "itemType": "book", "date": "1982" } },
    { "keep": "MNOP3456", "field_fixes": { "publisher": "Simon & Schuster", "place": "New York" },
      "creators": [ {"creatorType": "author", "lastName": "Putnam", "firstName": "Robert D."} ] }
  ]
}
```

`keep`/`merge` are Zotero item keys (the `key` field from either worklist). Omit
anything the subagents could not confirm; report those to the user instead. A
plan may also carry a top-level `creates` array (Mode D) and a `removals` array;
each section is independent, so Mode D import plans use the same `build_runjs.py`
and apply path as the curation modes.

1. The user **backs up** `zotero.sqlite` and `storage/` (Zotero closed), then
   reopens Zotero. Merges and edits have no undo.

2. Generate the snippet:

   ```bash
   uv run python scripts/build_runjs.py plan.json --out apply.js
   ```

3. Show `apply.js` so the user can review the embedded `PLAN`.

4. The user opens Tools → Developer → Run JavaScript, checks "Run as async
   function", pastes the snippet, and runs it. It returns a JSON log of what was
   merged, retyped, and re-fielded, with any skips.

Test on one action first before applying the whole plan.

- **Report the full path of every generated `.js`.** For all modes, always give
  the user the absolute path of each Run-JS file produced (e.g. `apply.js`,
  `import.js`) so they can locate it easily.
- **Always hand the user a loader snippet alongside the path.** Pasting a large
  `.js` file by hand truncates silently (the run then ends in `undefined` and
  applies nothing), so give the user this short loader — with the generated
  file's absolute path substituted and, on Windows, backslashes doubled — to
  paste into Run JavaScript ("Run as async function" checked) instead of the
  file's contents:

  ```javascript
  const path = "C:\\absolute\\path\\to\\apply.js";  // macOS: "/Users/<you>/.../apply.js"
  const src = await Zotero.File.getContentsAsync(path);
  const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
  const run = new AsyncFunction(src);
  return await run();
  ```

  A successful run prints the snippet's JSON log; `undefined` means the script
  body did not execute (wrong path, truncated file, or the async box unchecked).

## Safety

- Read-only detection (`scan_duplicates.py`, `scan_metadata.py`,
  `scan_imports.py`). The only writes are the reviewed Run-JS snippet the user
  runs. No direct `zotero.sqlite` writes anywhere (the Apply step backs up
  first; merges have no undo).
- Conservative by design: the fuzzy matcher avoids transitive over-merge, and
  subagents must default to "leave"/"don't merge" when evidence is thin.
- Mode D moves files on disk. `place_imports.py` is a dry run unless `--apply`
  is passed, writes a reversible `import_move_log.csv`, and never overwrites an
  existing file (collisions get a numbered suffix). Imported PDFs are linked,
  not copied into `storage/`.

## Scope

Library curation across four modes: deduplication, item-type/field correction,
metadata enrichment, faceted tagging, and importing/accessioning new PDFs as
linked items. For producing citations or locating a work's PDF, use the
`find-literature` skill.

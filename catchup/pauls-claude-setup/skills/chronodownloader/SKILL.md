---
name: chronodownloader
description: Download digitized historical sources from digital libraries.
disable-model-invocation: false
argument-hint: "<csv-file> | --id IDENTIFIER [--provider KEY] | --iiif URL [--options]"
---

# ChronoDownloader Skill

**Repository**: <https://github.com/Paullllllllllllllllll/ChronoDownloader>

**Repository root**: `<CHRONODOWNLOADER_DIR>`

## First-time setup

1. Clone the tool:
   `git clone https://github.com/Paullllllllllllllllll/ChronoDownloader`
2. In the clone, run `uv sync` to create the virtual environment. Add
   `--extra impersonate` only if a provider you use needs it (see the README).
3. Set the API key env vars for the providers you need (listed below). Most
   providers need no key.
4. Replace every `<CHRONODOWNLOADER_DIR>` in this skill folder with the path of
   your clone.

## Prerequisites

- Python 3.11+ (`pyproject.toml` `requires-python = ">=3.11"`)
- uv-managed virtual environment at `<CHRONODOWNLOADER_DIR>/.venv`. Set up: `uv sync`.
- Optional API keys (set as environment variables):
  - `EUROPEANA_API_KEY` (required for Europeana)
  - `DDB_API_KEY` (required for DDB)
  - `DPLA_API_KEY` (required for DPLA)
  - `GOOGLE_BOOKS_API_KEY` (required for Google Books)
  - `ANNAS_ARCHIVE_API_KEY` (optional; enables fast downloads for Anna's Archive)

## CLI Agent Contract

- **Exit codes**: `0` full success; `1` one or more works failed or are
  partial; `2` usage/config error (missing/invalid CSV, no providers enabled,
  interactive mode requested without a TTY, an unrecognized CLI flag, or a
  config/`--verify`/`--quota-status` error); `130` interrupted (Ctrl-C).
  Unrecognized flags are rejected with exit `2` -- a typo can no longer fall
  through to the interactive wizard.
- **`--json`**: emits one machine-readable JSON summary line on stdout at
  exit (counts of processed/succeeded/failed/deferred/skipped, output paths).
  Combine with `--non-interactive` for scripted/agentic runs.
- **`--non-interactive`**: force CLI mode; never prompt. Equivalent to
  `--cli` for mode-forcing purposes but is the preferred flag name for
  agents.
- **Non-TTY guard**: if interactive mode is requested (explicitly or by
  default) without a TTY on stdin, the tool exits immediately with code `2`
  instead of blocking on a prompt.
- **`--dry-run` is fully side-effect-free**: it performs discovery, resume
  classification, and candidate matching, but writes no work directories,
  `work.json` files, or `index.csv` rows, and makes no downloads.
- **`--search` / `--search-only` return structured metadata**: same
  side-effect-free discovery as `--dry-run`, but each work's full ranked
  candidate list is printed on stdout (NDJSON with `--json`, logs on stderr).
  Preferred over `--dry-run` when the candidates themselves are needed.
- CLI invocations (positional CSV, `--iiif`, `--id`, `--search`, `--dry-run`,
  `--verify`, `--json`, and other command-style flags) are auto-detected, so
  agents need not toggle `interactive_mode` in config first.

## CLI Usage

All commands run from the ChronoDownloader project root using `uv run python`. Entry point is the `main.cli` module, invoked as `python -m main.cli`.

Relative paths (the positional CSV, `--output_dir`) resolve against the
current working directory — run from the project root as instructed, or pass
absolute paths. (Unlike ChronoTranscriber, there is no config-based path
rebasing.)

### Main Download (CSV batch)

```bash
# Interactive mode (guided workflow)
uv run python -m main.cli

# Process CSV file (CLI auto-detected from positional arg)
uv run python -m main.cli sample_works.csv

# Custom output directory
uv run python -m main.cli works.csv --output_dir ./historical_sources

# Dry run (search + select, skip downloads)
uv run python -m main.cli works.csv --dry-run

# Custom configuration file
uv run python -m main.cli works.csv --config config_small.json

# Force CLI mode explicitly
uv run python -m main.cli --cli works.csv

# Verbose logging
uv run python -m main.cli works.csv --log-level DEBUG
```

### Direct IIIF Download

```bash
# Single manifest with custom name
uv run python -m main.cli --iiif "https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb11280551/manifest" --name Taillevent

# Multiple manifests
uv run python -m main.cli --iiif URL1 --iiif URL2 --output_dir ./iiif_downloads

# Dry run (fetch manifest info only)
uv run python -m main.cli --iiif URL --name MyWork --dry-run
```

### Identifier-Based Download

Download by provider-specific identifier instead of a full manifest URL. Simpler for agents -- just pass the item ID.

```bash
# With explicit provider
uv run python -m main.cli --id bsb11280551 --provider mdz --output_dir ./downloads

# With auto-detection (provider inferred from identifier format)
uv run python -m main.cli --id bsb11280551 --output_dir ./downloads

# With custom name stem
uv run python -m main.cli --id bpt6k1511262r --provider bnf_gallica --name Taillevent

# Dry run (resolve manifest, preview info, no download)
uv run python -m main.cli --id bsb11280551 --provider mdz --dry-run

# Internet Archive by identifier
uv run python -m main.cli --id ThreeBooksOfCookery1575 --provider internet_archive

# Native-download provider (Anna's Archive by MD5)
uv run python -m main.cli --id abc123md5hash --provider annas_archive
```

**Auto-detection patterns** (no `--provider` needed):

| Pattern | Provider |
|---------|----------|
| `bsb*` (e.g., `bsb11280551`) | MDZ |
| `bpt6k*`, `btv1b*`, `cb*`, `ark:/12148/*` | BnF Gallica |
| `mdp.*`, `inu.*`, `uc1.*`, `hvd.*`, `nyp.*`, etc. | HathiTrust |
| `vdc_*` | British Library |

For identifiers without a recognizable pattern, `--provider` is required.

**Precedence**: `--iiif` > `--id` > CSV file. When `--id` is given, CSV and search are bypassed.

### Search-Only (Metadata Preview)

Runs the full discovery + fuzzy-matching pipeline and prints structured
candidate metadata, downloading nothing. Fully side-effect-free; unlike
`--dry-run` it returns the ranked candidate list and ignores resume status
(completed works are searched again). Interactive mode has a matching
"Search Only" menu entry.

```bash
# Ad hoc search (human-readable ranked table)
uv run python -m main.cli --search "Le Viandier" --creator "Taillevent"

# Agent-friendly: one NDJSON line per work on stdout, logs on stderr
uv run python -m main.cli --search "Le Viandier" --creator "Taillevent" --json

# Search CSV rows (all rows with a title; --entry-ids/--limit narrow the set)
uv run python -m main.cli works.csv --search-only --json --limit 10

# Restrict providers for a faster fan-out
uv run python -m main.cli --search "Opera" --providers mdz,bnf_gallica --json
```

**NDJSON schema** (one line per work): `entry_id`, `query` (`title`,
`creator`), `status` (`match` | `no_match` | `no_candidates`), `selected`
(dict or null), `candidates` (list). Selected and each candidate carry
`provider`, `provider_key`, `title`, `creators`, `date`, `source_id`,
`item_url`, `iiif_manifest`, and `scores` (`score` = title score gated by
`min_title_score`, `total` = ranking score incl. creator bonus).

**Chaining pattern**: search first, inspect candidates, then download
deterministically -- `--id <source_id> --provider <provider_key>` or
`--iiif <iiif_manifest>`. This avoids gambling on fuzzy matching during the
expensive download step.

**Exit codes**: `0` every queried work matched; `1` at least one work had no
match; `2` usage error. A slow provider would gate the whole fan-out (searches
run in parallel but results print after selection); the per-provider
`selection.search_timeout_seconds` (default 60s, override per run with
`--search-timeout SECONDS`) drops any provider that exceeds it, and
`--providers` scopes the run to a subset.

### Quota Management

```bash
# Show quota usage and deferred queue status
uv run python -m main.cli --quota-status

# Show works-CSV progress (pass the csv_file) plus quota/deferred status
uv run python -m main.cli sample_works.csv --status

# Remove completed items from deferred queue
uv run python -m main.cli --cleanup-deferred

# List available provider keys
uv run python -m main.cli --list-providers
```

`--quota-status` and `--cleanup-deferred` honor `--config`. There is no
long-lived background daemon: ready deferred items are retried synchronously
at the start of every run.

### Verify Existing Downloads

`--verify` audits works already downloaded under `--output_dir`: checks file
size, PDF/EPUB magic bytes, and recorded page counts, then flips any
incomplete work to `partial` status in `work.json` and `index.csv` so the
normal pipeline re-downloads it on the next run. Read-mostly -- it never
deletes files.

```bash
uv run python -m main.cli --verify --output_dir ./downloads

# Machine-readable summary (ok / partial / total counts)
uv run python -m main.cli --verify --output_dir ./downloads --json
```

### Agentic / Advanced Invocation

```bash
# Provider control + scope filters + runtime overrides
uv run python -m main.cli works.csv --providers mdz,bnf_gallica --pending-mode failed --entry-ids 12035,14141 --limit 10 --resume-mode reprocess_all --selection-strategy sequential_first_hit --min-title-score 40 --download-strategy all --no-keep-non-selected-metadata

# Quick single-item download by identifier (agent-friendly)
uv run python -m main.cli --id bsb11280551 --provider mdz --name Kochbuch --output_dir ./downloads
uv run python -m main.cli --id bpt6k1511262r --name Taillevent --output_dir ./downloads

# Scripted run with a JSON summary and a deterministic exit code
uv run python -m main.cli works.csv --non-interactive --json --output_dir ./downloads
```

CLI invocations are auto-detected from command-style arguments (`--iiif`, `--id`, `--dry-run`, `--verify`, `--json`, a positional CSV path, etc.), so agents need not toggle `interactive_mode` in config first.

## All CLI Arguments

**Read [arguments.md](arguments.md) for the full argument reference.**

## CSV Input Format

**Required columns**: `entry_id` (always required); `short_title` (required unless `direct_link` is present)

**Optional columns**: `main_author`, `year` (publication year sought;
activates the edition-year ranking penalty via `selection.year_tolerance`),
`retrievable` (download status: `True`/`False`/`deferred`/empty;
auto-updated; German-locale Excel `WAHR`/`FALSCH` are recognized, and
CRLF/BOM Excel round-trips are preserved), `link` (item URL; auto-populated), `direct_link` (IIIF
manifest URL for direct download)

The works CSV is the authoritative status ledger. `deferred` marks a
quota-deferred work (distinct from `False`/failed); it counts as pending and
is retried automatically at the start of the next run. `--pending-mode
failed` matches only literal failures, not `deferred` rows; use
`--pending-mode all` (the default) to include both.

Additional columns are preserved but not used.

**Standard CSV**:

```csv
entry_id,short_title,main_author
6106,Tractatus de uino,Anonymous
12495,Tractatus de praeparandis,Hier. Emser
```

**CSV with direct IIIF links** (short_title optional for rows with direct_link):

```csv
entry_id,short_title,main_author,direct_link
1,Kochbuch,Anonymous,https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00001234/manifest
2,,Unknown,https://gallica.bnf.fr/iiif/ark:/12148/bpt6k5678/manifest.json
```

After processing, `retrievable` and `link` columns are updated in-place (thread-safe). Additional columns `download_provider` and `download_timestamp` may be added.

## Configuration (config.json)

Full config reference and recommended defaults: see REFERENCE.md in this folder.

An optional `api_keys.json` placed next to the resolved `config.json` can remap each provider's API key to a custom environment-variable name (e.g. `europeana` -> `EUROPEANA_API_KEY_2`); the built-in default names apply when the file or a provider entry is omitted.

## Direct IIIF Mode

Four ways to trigger direct downloads (bypassing provider search):

1. **Identifier**: `--id IDENTIFIER [--provider KEY] [--name STEM]` (auto-detects provider when possible)
2. **CLI flag**: `--iiif URL [--name STEM]` (repeatable for multiple manifests)
3. **CSV column**: Add a `direct_link` column with IIIF manifest URLs; rows with a `direct_link` value are downloaded directly
4. **Interactive mode**: Select "Direct IIIF Download" from the mode menu

Direct IIIF supports IIIF Presentation API v2 and v3, manifest renderings (PDF/EPUB), and URL pattern caching to avoid redundant 400 errors across pages. IIIF works record `pages_expected`/`pages_downloaded` in `work.json` and are marked `partial` (not `completed`) unless every expected page arrived.

Renderings take precedence over page images by default. With the shipped `prefer_pdf_over_images: true`, a manifest that advertises an `application/pdf` rendering (Internet Archive, Wellcome, the DFG viewer) produces one PDF and no images, and the work is recorded `completed` with `pages_expected`/`pages_downloaded` unset. When you want the page images, pass `--images-only` (v1.27.0), which clears both keys for the run; `--no-prefer-pdf-over-images` alone fetches both and does not save the PDF transfer. Preview with `--dry-run` first — a non-empty `rendering_formats` in the manifest preview means the PDF path will win. See arguments.md for the full flag semantics.

## Output Structure

```
downloaded_works/
  index.csv                           # Tracks all processed works
  <entry_id>_<work_name>/
    work.json                         # Selection metadata, scores, provider info
    metadata/
      <entry_id>_<work_name>_<provider>.json
    objects/
      <entry_id>_<work_name>_<provider>.pdf
      <entry_id>_<work_name>_<provider>_image_001.jpg
```

File naming uses strict snake_case. Page images are numbered by their page
index (provider patterns like `_p00001`, `_page_0001`, `_img0001`), so a
failed page leaves an honest gap that a resume run retries; non-page images
use a 3-digit success counter. Multiple non-image files get numeric suffixes.
Naming conventions are controlled by the `naming` config section.

Downloads are atomic: each file streams to a `.part` file and is renamed into
place only after validation; `.pdf`/`.epub` payloads must carry correct magic
bytes or the download is rejected. `index.csv` is an upsert
snapshot keyed on `(work_id, entry_id)` (one row per work-entry pair, so
different editions of the same title keep separate rows; reprocessing updates
the row in place rather than appending a duplicate); `status` is one of
`completed`, `partial`, `failed`, `deferred`, `no_match`.

The source CSV is updated in place: `retrievable` set to `True`/`False`/`deferred`, `link` populated with the item URL, and `download_provider` / `download_timestamp` columns added.

# ChronoDownloader — CLI Arguments

**Positional**:
- `csv_file` (optional): Path to CSV file. Must contain `short_title` or `direct_link` (with required `entry_id`).

**General options**:
- `--output_dir DIR`: Output directory (default: `downloaded_works`)
- `--dry-run`: Run searches and select candidates, but skip downloads. Fully
  side-effect-free: writes no work directories, `work.json`, or `index.csv`
  rows.
- `--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: Logging level (default: `INFO`)
- `--config PATH`: Path to JSON config file (default: `config.json`)
- `--interactive`: Force interactive mode regardless of config
- `--cli`: Force CLI mode regardless of config
- `--non-interactive`: Force non-interactive (CLI) mode; never prompt
- `--json`: Emit a single machine-readable JSON summary line on stdout at exit
- `--verify`: Verify downloaded works under `--output_dir` (file size, PDF/EPUB
  magic bytes, recorded page counts) and flip incomplete works to `partial`,
  then exit

**Search only** (no downloads, fully side-effect-free):
- `--search TITLE`: Search all enabled providers for a title and print
  structured candidate metadata (ranked table; NDJSON with `--json`). No CSV
  needed.
- `--creator NAME`: Creator/author for `--search` (improves match scoring)
- `--search-only`: With a CSV file: search and match every row that has a
  title (ignores retrievable/resume status; `--entry-ids` and `--limit`
  narrow the set), printing one result per work. Exit `0` only if every
  queried work matched; `1` if any had no match.

**Direct IIIF**:
- `--iiif URL`: IIIF manifest URL to download (repeatable for multiple manifests). Bypasses CSV and search.
- `--name STEM`: Output name stem for IIIF and identifier downloads (e.g., `Taillevent_Viandier`)

**Identifier-based download**:
- `--id IDENTIFIER`: Provider-specific item identifier (e.g., `bsb11280551` for MDZ, `bpt6k1511262r` for Gallica). Bypasses CSV and search.
- `--provider KEY`: Provider key for `--id` lookup (e.g., `mdz`, `bnf_gallica`, `internet_archive`). Optional when auto-detection can infer the provider from the identifier format.

**Quota / utility**:
- `--quota-status`: Display quota and deferred queue status, then exit.
  Honors `--config`.
- `--status`: Display works-CSV progress (pass `csv_file`) plus quota and
  deferred queue status, then exit
- `--cleanup-deferred`: Remove completed items from deferred queue, then exit.
  Honors `--config`.
- `--list-providers`: List all available provider keys and exit

**Provider selection overrides**:
- `--providers KEYS`: Comma-separated provider keys to use (replaces config set)
- `--enable-provider KEYS`: Force-enable provider(s) (comma-separated or repeat flag)
- `--disable-provider KEYS`: Force-disable provider(s) (comma-separated or repeat flag)

**Processing scope**:
- `--pending-mode {all,new,failed}`: Which CSV rows to process. `all`
  (default) processes everything not `completed` (pending + failed +
  deferred, via `get_pending_works`); `new` only never-tried (empty status)
  rows; `failed` only rows with a literal `False`/failed status -- it does
  NOT include `deferred` rows. Deferred works are otherwise retried
  automatically and synchronously at the start of every run regardless of
  `--pending-mode`.
- `--entry-ids IDS`: Restrict to specific entry_id values (comma-separated or repeat flag)
- `--limit N`: Process at most N pending rows after filters

**Runtime config overrides** (concurrency remains config-only):
- `--resume-mode {skip_completed,reprocess_all,skip_if_has_objects,resume_from_csv}`
- `--selection-strategy {collect_and_select,sequential_first_hit}`
- `--min-title-score FLOAT`: Minimum PURE title-match score (0-100) required
  to accept a candidate. Creator similarity is a ranking bonus only and never
  lowers this gate; missing creator metadata is not penalized (v1.7.0:
  previously creator similarity could count toward the gate itself).
- `--search-timeout SECONDS`: Per-provider search timeout (float) overriding
  `selection.search_timeout_seconds` for this run; a provider exceeding it is
  dropped so one slow provider cannot stall the fan-out (`0` disables it)
- `--creator-weight FLOAT`: Creator match weight (0.0-1.0), applied as a
  positive ranking bonus only
- `--year-tolerance YEARS`: Overrides `selection.year_tolerance` (default 15)
  for this run; candidates dated outside the window around the CSV's `year`
  column take a capped ranking penalty (`0` = exact-year preference). Fails
  open on missing/unparseable dates; inert without a CSV `year` column
- `--max-candidates-per-provider INT`: Max search results per provider
- `--download-strategy {selected_only,all}`
- `--keep-non-selected-metadata` / `--no-keep-non-selected-metadata`
- `--prefer-pdf-over-images` / `--no-prefer-pdf-over-images`
- `--download-manifest-renderings` / `--no-download-manifest-renderings`
- `--max-renderings-per-manifest INT`
- `--images-only` (v1.27.0)
- `--rendering-mime-whitelist MIMES` (comma-separated; repeatable)
- `--overwrite-existing` / `--no-overwrite-existing`
- `--include-metadata` / `--no-include-metadata`

**PDF renderings vs. page images.** The shipped config sets
`prefer_pdf_over_images: true` and `download_manifest_renderings: true`, so a
manifest advertising an `application/pdf` rendering (Internet Archive, Wellcome,
the DFG viewer, and others do) yields one PDF and *no* page images: renderings
are fetched first, and the prefer-PDF gate then returns before any canvas is
touched.

- `--images-only`: page images only. Use this whenever the goal is an image
  set. It clears both keys for the run; either flag below, given explicitly,
  still overrides it.
- `--no-download-manifest-renderings`: never fetch the PDF/EPUB. Same effect as
  `--images-only` unless the config also carries a custom prefer-PDF setting
  you want left alone.
- `--no-prefer-pdf-over-images`: fetch the rendering *and* the images. The PDF
  still downloads, so this alone does not save the transfer.
- `--max-renderings-per-manifest 0` matches
  `--no-download-manifest-renderings`.

Run `--dry-run` first: the manifest preview reports `rendering_formats`, so a
non-empty list tells you the PDF path will win before anything transfers.

**Exit codes** (CLI agent contract): `0` full success; `1` one or more works
failed or are partial; `2` usage/config error; `130` interrupted (Ctrl-C).

# ChronoDownloader Reference

A tracked `config.example.json` ships with
conservative defaults; the real `config.json` is gitignored and user-local.
The loader falls back to `config.example.json` (with an INFO log line) when
`config.json` is absent, so a fresh clone is runnable without setup.

## Full config.json

Located at `<CHRONODOWNLOADER_DIR>/config.json`. Override
path with `--config` or `CHRONO_CONFIG_PATH` env var. Nine sections:

### 1. general

```json
{ "interactive_mode": true, "default_output_dir": "downloaded_works", "default_csv_path": "sample_works.csv" }
```

### 2. providers

Enable/disable each of the 17 providers by key (`true`/`false`).

### 3. provider_settings

Per-provider rate limiting and behavior. Each provider may have:

- `max_pages` / `max_images` / `max_files`: Download caps per work (0 = unlimited)
- `min_title_score`: Provider-specific fuzzy match threshold
- `network`: `{ delay_ms, jitter_ms, max_attempts, base_backoff_s, backoff_multiplier,
  max_backoff_s, timeout_s, headers, circuit_breaker_enabled, circuit_breaker_threshold,
  circuit_breaker_cooldown_s, ssl_error_policy }`
- `quota` (quota-limited providers only):
  `{ enabled, daily_limit, reset_hours, wait_for_reset }`
- Google Books extras: `free_only`, `prefer`, `allow_drm`

### 4. download

```json
{
  "resume_mode": "skip_if_has_objects",
  "prefer_pdf_over_images": true,
  "download_manifest_renderings": true,
  "max_renderings_per_manifest": 5,
  "rendering_mime_whitelist": ["application/pdf", "application/epub+zip"],
  "overwrite_existing": false,
  "include_metadata": true,
  "allowed_object_extensions": [".pdf", ".epub", ".zip", ".jpg", ".jpeg", ".png",
    ".jp2", ".tif", ".tiff", ".webp", ".bmp", ".gif"],
  "save_disallowed_to_metadata": true,
  "max_parallel_downloads": 10,
  "provider_concurrency": {
    "default": 5, "annas_archive": 3, "bnf_gallica": 1, "google_books": 1,
    "internet_archive": 3, "mdz": 2, "wellcome": 2, "slub": 1,
    "e_rara": 1, "sbb_digital": 2
  },
  "queue_size": 100,
  "worker_timeout_s": 600
}
```

Resume modes: `skip_completed` (work.json exists); `skip_if_has_objects` (objects/ has
files); `resume_from_csv` (retrievable=True); `reprocess_all`.

`worker_timeout_s` is a TOTAL ceiling in seconds for waiting on a parallel
download batch (not a per-task timeout). Setting it to `0` now truly waits
indefinitely (previously `0` could still time out); `config.example.json`
ships with `0` as the recommended default.

Downloads stream to a `.part` file and are promoted to the final name only
after validation, so truncated/interrupted transfers are discarded instead of
recorded as complete. `.pdf`/`.epub` files must carry correct magic bytes or
the download is rejected; extension inference prefers the `Content-Type`
response header.

### 5. selection

```json
{
  "strategy": "collect_and_select",
  "max_parallel_searches": 10,
  "provider_hierarchy": ["mdz", "slub", "bnf_gallica", "e_rara", "annas_archive",
    "internet_archive", "wellcome", "google_books", "loc", "europeana", "dpla",
    "ddb", "polona", "sbb_digital", "hathitrust"],
  "min_title_score": 35,
  "search_timeout_seconds": 60,
  "creator_weight": 0.2,
  "year_tolerance": 15,
  "max_candidates_per_provider": 5,
  "download_strategy": "selected_only",
  "keep_non_selected_metadata": false
}
```

Strategies: `collect_and_select` (query all enabled providers, score, rank, select
best) or `sequential_first_hit` (stop at first match above threshold).

`search_timeout_seconds` caps each provider's search (default 60; `0`/`null`
disables it). A provider exceeding its timeout is logged at WARNING and dropped
so one slow provider cannot stall the fan-out; override per provider via
`provider_settings.<key>.search_timeout_seconds`. It is resolved live from the
config at search time, so it applies to both CLI and interactive runs;
`--search-timeout SECONDS` is a CLI-only per-run override.

`min_title_score` gates the PURE title-match score only.
`creator_weight` is applied purely as a positive ranking bonus on top of
candidates that already pass the title gate; a strong creator match never
lowers or substitutes for the title threshold, and a candidate with no
creator metadata at all is not penalized.

### 6. naming

```json
{ "include_creator_in_work_dir": true, "include_year_in_work_dir": true, "title_slug_max_len": 80 }
```

### 7. download_limits

```json
{
  "total": { "images_gb": 100, "pdfs_gb": 50, "metadata_gb": 1 },
  "per_work": { "images_gb": 5, "pdfs_gb": 3, "metadata_mb": 250 },
  "on_exceed": "stop"
}
```

### 8. deferred

```json
{
  "background_enabled": true,
  "max_retries": 5
}
```

There is no background daemon thread or interactive prompt. Ready deferred
items are retried synchronously at the start of every run; a successful
retry writes through to the works CSV, `work.json`, and `index.csv`.
`background_enabled` is retained for compatibility but no longer drives an
active polling thread.

**State file location**: moved to `~/.chronodownloader/.downloader_state.json`
by default (previously a CWD-relative `.downloader_state.json`), so quota
counters persist across working directories. A legacy CWD state file is
adopted (copied) once automatically on first run. Override with:

- `state_dir`: directory for the state file (recommended override)
- `state_file`: full path override (legacy behavior). A config that still
  sets `state_file` keeps the old, pre-1.7.0 location instead of moving to
  `~/.chronodownloader/`.

The state file (and the works CSV) now write atomically; a corrupted state
file is preserved as `.corrupt` rather than silently resetting quota
counters.

### 9. direct_iiif

```json
{
  "enabled": true,
  "link_column": "direct_link",
  "check_link_column": true,
  "naming_template": "{provider}_{item_id}"
}
```

Naming placeholders: `{entry_id}`, `{name}`, `{provider}`, `{item_id}`. Page suffix
`_p00001.jpg` is appended automatically.

## Supported Providers (17)

| Key | Provider | Region | API Key | IIIF | Notes |
|-----|----------|--------|---------|------|-------|
| `internet_archive` | Internet Archive | US | No | Yes | |
| `bnf_gallica` | BnF Gallica | France | No | Yes | |
| `loc` | Library of Congress | US | No | Yes | |
| `europeana` | Europeana | EU (aggregator) | Yes | Yes | |
| `dpla` | DPLA | US (aggregator) | Yes | Yes | |
| `ddb` | Deutsche Digitale Bibliothek | Germany | Yes | Yes | |
| `british_library` | British Library | UK | No | Yes | |
| `mdz` | MDZ (BSB Munich) | Germany | No | Yes | |
| `polona` | Polona | Poland | No | Yes | |
| `bne` | Biblioteca Nacional de Espana | Spain | No | Yes | |
| `google_books` | Google Books | Global | Yes | No | Circuit breaker; DRM controls |
| `hathitrust` | HathiTrust | US | Optional | Yes | |
| `wellcome` | Wellcome Collection | UK | No | Yes | |
| `annas_archive` | Anna's Archive | Global (aggregator) | Optional | No | Daily quota; deferred queue |
| `slub` | SLUB Dresden | Germany | No | Yes | |
| `e_rara` | e-rara | Switzerland | No | Yes | |
| `sbb_digital` | SBB Digital Collections | Germany | No | No (METS) | |

## Parallel Download Config Keys

- `download.max_parallel_downloads`: Number of concurrent download workers across all
  works (default: 10)
- `download.provider_concurrency`: Per-provider semaphore limits prevent overwhelming
  individual APIs
- `selection.max_parallel_searches`: Concurrent provider searches during the selection
  phase (default: 10)
- `download.queue_size`: Download task queue size (default: 100)
- `download.worker_timeout_s`: TOTAL ceiling in seconds for waiting on a
  parallel batch, not a per-task timeout; `0` waits indefinitely (see
  section 4 above)

When `max_parallel_downloads` = 1, downloads run sequentially. Parallel and sequential
modes use the same execution logic via `main/execution.py`.

## Quota Management Config Keys

Quota limits apply only to providers with daily/hourly hard caps (currently Anna's
Archive). All other providers use network rate limiting (delays, backoff) without quotas.

When a quota-limited provider exhausts its limit (locally-tracked, or reported
by the provider's own API as a server-side quota error):

1. The work is recorded as `deferred` in the works CSV (not `failed`) and
   queued in the persistent state file.
2. At the start of the *next* run, every currently-ready deferred item is
   retried synchronously before new works are processed -- there is no
   background daemon thread or interactive prompt.
3. A successful retry writes through to the works CSV, `work.json`, and
   `index.csv` in the same pass.
4. Max retries configurable via `deferred.max_retries` (default: 5).
5. Old completed/failed items are auto-cleaned after 7 days.

Quota units are only recorded when the fast-download API path was actually
used; public-scraping fallbacks (e.g. Anna's Archive without an API key) do
not consume quota.

Use `--quota-status` (or `--status <csv_file>`, which adds works-CSV
progress) to inspect current state, and `--cleanup-deferred` to manually
remove completed items. Both `--quota-status` and `--cleanup-deferred` honor
`--config`.

**Anna's Archive**: supports the active `.gl` domain alongside the other
domains, host-relative link rebuilding, and server-side quota-deferral
detection.

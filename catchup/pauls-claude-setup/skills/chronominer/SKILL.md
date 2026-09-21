---
name: chronominer
description: Extract structured data from documents via schema-driven LLM extraction.
disable-model-invocation: false
argument-hint: "--schema <SchemaName> --input <path> [--options]"
---
# ChronoMiner Skill

## First-time setup

1. Clone the tool:
   `git clone https://github.com/Paullllllllllllllllll/ChronoMiner`
2. In the clone, run `uv sync` to create the virtual environment.
3. Set at least one API key as an environment variable: `OPENAI_API_KEY`,
   `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, or `OPENROUTER_API_KEY`.
4. Replace every `<CHRONOMINER_DIR>` in this skill folder with the path of
   your clone.

## Prerequisites

- Python 3.12+; uv-managed venv at `<CHRONOMINER_DIR>/.venv`.
  Set up: `uv sync`.
- One API key env var: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`,
  or `OPENROUTER_API_KEY`
- Project root: `<CHRONOMINER_DIR>`
- Run all scripts from the project root with `uv run python`
- CLI mode activates automatically once any CLI argument is passed; force it
  explicitly with `--non-interactive` (or force the wizard with
  `--interactive`), which overrides `general.interactive_mode` in
  `paths_config.yaml`. Editing that config key is no longer necessary for
  agent use.

## CLI Usage

**Read [arguments.md](arguments.md) for the full argument reference.**

Relative `--input` and other CLI paths resolve against the current working
directory — run from the project root as instructed, or pass absolute paths.
(Unlike ChronoTranscriber, there is no config-based path rebasing.)

`extract.py` collects both `.txt` and `.md` files as text inputs
in CLI mode. The tool's own sidecar/report files (`*_line_ranges.txt`, legacy
singular `*_line_range.txt`, `*_context.txt`, `*_output.txt`) are always
excluded from discovery, so a second run never re-extracts from its own
output.

## CLI Agent Contract

`extract.py` and `check_batches.py` follow a uniform contract for
scripting and CI:

- Exit `0` -- every file completed (or was already complete);
- Exit `1` -- one or more files failed or completed partially (and, for
  `check_batches.py`, one or more batches remain pending or failed);
- Exit `2` -- usage/configuration error, or interactive mode requested
  without a TTY;
- Exit `130` -- interrupted by the user (Ctrl+C).
- `--json` prints a single machine-readable summary line at the end
  (files/complete/partial/failed/skipped, token totals for
  `extract.py`; finalized/pending/failed counts for
  `check_batches.py`).
- `--dry-run` (`extract.py` only) discovers inputs, classifies
  resume state, and reports planned actions with zero API calls or side
  effects.

## Configuration Files

All in `config/` at project root. Unless the user instructs otherwise, leave configs unchanged when running extractions.

Full config reference and recommended defaults: see REFERENCE.md in this folder.

### Other Config Files

- **`chunking_and_context.yaml`**: `chunking.default_tokens_per_chunk`, line-range adjustment matching/retry settings (`certainty_threshold`, `max_low_certainty_retries`, `max_context_expansion_attempts`; the context window doubles per expansion, and `min_substring_length` is enforced on markers). `scan_range_multiplier` is deprecated and ignored -- a leftover key in the YAML is harmless.
- **`concurrency_config.yaml`**: concurrency limits (overridable via `--concurrency-limit` and `--delay`), retry backoff, OpenAI `service_tier`, `daily_token_limit` enforcement
- **`api_keys_config.yaml`** (optional): remaps each provider (`openai`, `anthropic`, `google`, `openrouter`) to a custom env var name holding its API key (e.g. `openai: OPENAI_API_KEY_2`), defaults applying when the file or an entry is omitted; the remap also reaches batch mode

## Context Files (Hierarchical Resolution)

Context is resolved automatically per task (extraction or line-range adjustment). Most specific wins:

1. **File-specific**: `{filename}_extract_context.txt` or `{filename}_adjust_context.txt` next to input file
2. **Folder-specific**: `{foldername}_extract_context.txt` or `{foldername}_adjust_context.txt` in parent directory
3. **General fallback**: `context/extract_context.txt` or `context/adjust_context.txt` at project root

Keep context files under 4,000 characters. Legacy per-schema files are in `context/legacy/` for reference.

## Available Schemas

13 registered schemas. Full schema inventory: see REFERENCE.md in this folder.

Custom schemas: create JSON schema in `schemas/`, register in
`modules/extract/schema_handlers.py`, add paths in `paths_config.yaml`.

## Visual Input Pipeline

ChronoMiner accepts images and PDFs directly via vision-capable LLMs, bypassing ChronoTranscriber.

- **Auto-detection**: Input type (`text`, `image`, `pdf`, `mixed`) is detected from file extensions. Override with `--input-type`.
- **Supported extensions**: images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`), PDFs (`.pdf`)
- **Processing**: Images/PDFs are preprocessed per provider config (grayscale, transparency, resize, JPEG compression), then sent as base64 content blocks with `prompts/image_extraction_prompt.txt`. PDFs are rendered page-by-page at `target_dpi`; each page is one chunk.
- **Batch support**: Visual inputs work in batch mode across OpenAI, Anthropic, and Google.
- **Chunk slicing**: `--first-n-chunks N` / `--last-n-chunks N` limits which pages or images are processed.
- **Detail control**: `--image-detail low|high|auto|original` overrides per-provider defaults. `original` is honored by Responses-API-routed models: the GPT-5.6 family (`gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`), `gpt-5.5-pro`, `gpt-5.4-pro`, `gpt-5.4`. On other models it is sent as `high`, with a once-per-model warning naming the models that honor it. `original` acts on two layers: in preprocessing it skips the `high_target_box` fit-and-pad and caps only at `original_max_side_px`/`original_max_pixels`, so a downgraded request still sends full-resolution pixels under a `high` detail parameter. It bills roughly 1.4x the input tokens of `high` on the same image. Use a model that honors it for page-image extraction.

## Anthropic Prompt Caching

For Anthropic models (direct or via OpenRouter), prompt caching is enabled automatically. The system message content block is annotated with `cache_control: {"type": "ephemeral"}`, allowing Anthropic to cache and reuse the system prompt across chunks. Cache hit/miss is logged with token counts (`cache_creation_input_tokens`, `cache_read_input_tokens`). This reduces cost and latency for multi-chunk extractions.

## Resume and Force

- `--resume`: Skips fully processed files; resumes partially processed files from last completed chunk via `_temporary.jsonl` tracking.
- `--force`: Reprocesses all files from scratch, ignoring existing outputs and tracking files.
- For line range adjustment: `--resume` skips files whose completed adjustment JSONL matches the current settings, the current `_line_ranges.txt` fingerprint, and the prompt hash (regenerating the ranges file or editing the prompt invalidates the marker and triggers re-adjustment); `--force` re-adjusts all.
- `--force` takes precedence if both flags are set.
- Temp JSONLs carry a format-version header; resume refuses to merge
  unversioned or stale-versioned artifacts left over from older runs instead
  of silently mis-merging them. Re-run with `--force` to regenerate a stale
  temp file. Adjustment temp JSONLs (`*_adjust_temp.jsonl`) use header
  version 2; older adjustment artifacts are rejected as stale and re-adjust
  once on the next run.
- Sliced runs (`--first-n-chunks`, `--last-n-chunks`, `--page-range`)
  write absolute chunk indices and custom_ids into records, not indices
  relative to the slice.
- Text outputs stamp `chunking_text_version: 2` in `_chronominer_metadata`
  (chunking preserves newlines when joining chunks, so LLM inputs keep
  their line structure); use this field to distinguish chunking eras
  in downstream analysis.

## Batch Management

Batch processing across OpenAI (50% discount), Anthropic, and Google with unified interface.

1. **Submit**: `uv run python main/extract.py --schema <name> --input <path> --batch`
2. **Monitor**: `uv run python main/check_batches.py [--schema <name>] [--json]`
3. **Cancel**: `uv run python main/cancel_batches.py [--force]`
4. **Repair**: `uv run python main/repair.py [--schema <name>] [--files f1 f2]`

Statuses: `validating`, `in_progress`, `finalizing`, `completed`, `failed`, `expired`, `cancelled`. Completed batches auto-download into all configured output formats.

Large request sets are auto-split by the provider's per-batch request-count
and byte limits into `_part{n}` submissions (one tracking record per part);
`check_batches.py` merges the parts back into a single final output.
Remote input/output files are deleted only after the final output JSON is
durably written locally, so a mid-download failure never destroys results.

`check_batches.py --json` prints a one-line JSON status summary and exits
non-zero while any batch is still pending or failed, so a poller can loop
the command until every batch resolves.

`repair.py` routes status checks and result retrieval through
the provider-agnostic batch backend, so it does not require
`OPENAI_API_KEY` at startup for non-OpenAI batches; the
regenerated output is marked `fully_completed` only when no batch failed, is
missing, or is still running — a repair over pending batches stays
re-runnable instead of being finalized prematurely. Batch submissions persist
their schema and model in the tracking records, and `check_batches.py`
finalizes under the recorded schema when it is unambiguous (legacy artifacts
fall back to the configured assumption with a warning).

## Line Range Tools

Two utilities for optimizing text chunking boundaries before extraction.

- **Generate** (`main/generate_line_ranges.py`): Creates `{filename}_line_ranges.txt` with token-based ranges. `--tokens N` overrides default chunk size. `--first-n-chunks` / `--last-n-chunks` limits output ranges.
- **Adjust** (`main/adjust_line_ranges.py`): LLM-powered semantic boundary detection with certainty scoring (0-100), automatic retry, and geometric context expansion (window radius doubles per attempt). The model sees a `<<<CURRENT_CHUNK_START>>>` sentinel marking the boundary under review plus the schema name as the semantic unit type; deleting a no-content range requires the certainty threshold. Configured via `chunking_and_context.yaml`. Supports `--resume` and `--force` as well as `--first-n-chunks` / `--last-n-chunks` (absolute range indices; unselected ranges pass through unchanged, and sliced runs are never marked complete).
- **Chunking strategies**: `--chunking line_ranges` uses pre-existing files; `--chunking adjust-line-ranges` generates and adjusts in one step.

## Cost Analysis

Daily token budgeting is configured in `concurrency_config.yaml`; see REFERENCE.md in
this folder for the full config block. Tracks every API call, resets at 00:01
UTC (one minute after OpenAI's 00:00 UTC free-token reset), displays usage at
startup/completion, and pauses when budget is exhausted (resumes after reset
or Ctrl+C). For Anthropic, cache-specific
tokens are also tracked. Chunk-level token counting uses the target model's
own encoding when known, rather than a generic fallback.

Token-budget state lives in a user-level directory,
`~/.chronominer/.chronominer_token_state.json` by default, so the budget is
shared across runs regardless of the working directory. Override the
directory via `general.state_dir` in `paths_config.yaml`. A legacy
`.chronominer_token_state.json` left in the working directory from
pre-1.18 runs is adopted once into the new location if the user-level file
is absent. Writes are debounced (with a flush at exit).

**Shared cross-tool budget (optional, off by default).** Setting
`enabled: true` in the `shared_token_budget` block of each tool's config lets
ChronoMiner, ChronoTranscriber, and AutoExcerpter share ONE combined daily
budget. When enabled, combined usage lives in
`~/.chronopipeline/token_ledger.json` with one field per tool — read that
file to see today's split before planning large runs. `daily_token_limit`
is enforced against the COMBINED total across all three tools, so several
tools running at once cannot collectively overshoot; keep `daily_tokens`
identical in every tool that runs. A tool waiting at the limit re-reads
`daily_tokens` from config every poll cycle (~60 s), so raising the limit
mid-wait takes effect without restarting the run. Batch API usage never
counts toward the budget. If the ledger is unavailable the tool degrades to
its private per-tool counter with one warning.

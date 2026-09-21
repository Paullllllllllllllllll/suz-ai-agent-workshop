---
name: chronotranscriber
description: Transcribe PDFs, scans, ebooks, audio to text via OCR/LLM/speech-to-text.
disable-model-invocation: false
argument-hint: "--type <type> --method <method> --input <path> [--options]"
---

# ChronoTranscriber Skill

ChronoTranscriber transforms historical documents, academic papers, and ebooks into searchable, structured text using AI models or local Tesseract OCR. Multi-provider LLM support via LangChain (OpenAI, Anthropic, Google, OpenRouter, custom endpoints); multi-format output (txt, md, json); prompt caching across all providers; batch processing with 50% cost savings (OpenAI). Since v3.0.0 it also transcribes audio recordings (speech-to-text) via the OpenAI audio API, Gemini, or local faster-whisper.

**Repository**: `<CHRONOTRANSCRIBER_DIR>`

## First-time setup

1. Clone the tool:
   `git clone https://github.com/Paullllllllllllllllll/ChronoTranscriber`
2. In the clone, run `uv sync` to create the virtual environment. Add
   `--extra audio` if you want local Whisper audio transcription.
3. Set at least one API key as an environment variable: `OPENAI_API_KEY`,
   `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, or `OPENROUTER_API_KEY`.
4. Replace every `<CHRONOTRANSCRIBER_DIR>` in this skill folder with the path
   of your clone.

## Prerequisites

- Python 3.13+; uv-managed venv at `<CHRONOTRANSCRIBER_DIR>/.venv`. Set up: `uv sync`.
- One API key env var: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`,
  or `OPENROUTER_API_KEY`
- Tesseract OCR (optional, for offline `--method tesseract`)
- FFmpeg (optional, on system PATH; auto-fallback for JPEG2000 files with sub-8-bit/bilevel codestreams that openjpeg cannot decode, and required for audio only when chunking long recordings or using `--pages` on audio)
- faster-whisper (optional, for offline `--method whisper`; install via `uv sync --extra audio`; first run downloads the configured model)

## CLI Usage

**Read [arguments.md](arguments.md) for the full argument reference.**

**Always pass absolute `--input`/`--output` paths.** Relative paths do NOT
resolve against the current working directory: they resolve against the
per-type base directories configured in `paths_config.yaml`
(`file_paths.<Type>.input`/`.output`, via `resolve_path` in
`modules/core/cli_args.py`), which may point at unrelated folders. A
relative path therefore fails with "Input path does not exist"
under an unexpected prefix, or silently lands output elsewhere. (ChronoMiner
and AutoExcerpter resolve relative paths against the CWD; this caveat is
specific to ChronoTranscriber.)

## CLI Agent Contract

All five entry points (`transcribe.py`, `check_batches.py`,
`cancel_batches.py`, `repair.py`,
`postprocess.py`) share one execution contract:

- **Exit codes**: `0` full success; `1` one or more items failed or partial;
  `2` usage/configuration error; `130` interrupted by the user (Ctrl+C).
- **Mode override**: `--interactive` / `--non-interactive` (mutually
  exclusive) override `general.interactive_mode` in `paths_config.yaml` for
  that one run. To drive the tool as an agent, pass `--non-interactive` plus
  explicit CLI arguments rather than editing the gitignored config file —
  editing the YAML to force CLI mode is no longer necessary and is obsolete
  advice.
- **Non-TTY guard**: if interactive mode is in effect (via config or
  `--interactive`) and stdin is not a TTY, the tool now exits `2` with a
  clear message instead of hitting EOF and reporting a false success (`0`).
- **`--json`**: accepted and honored on every entry point.
  `transcribe.py` emits `{"tool": "chronotranscriber", "dry_run":
  bool, "items_total": int, "items_processed": int, "items_failed": int,
  "exit_code": int}`; the other four emit `{"tool": ..., "command": ...,
  ..., "exit_code": int}` with per-script counts (check_batches:
  finalized/pending/failed; cancel_batches: cancelled/failed;
  repair: repaired/failed; postprocess:
  files_processed/files_failed).
- **`--dry-run`** (`transcribe.py` only): reports discovery and
  resume/skip counts with no API calls and no writes; always exits `0`.
- `check_batches.py` exits non-zero if any batch reached a terminal failure;
  `cancel_batches.py` exits non-zero if any cancellation failed.

## Output Formats

Set via `--output-format` or `general.output_format` in `paths_config.yaml`.

- **`txt`** (default): Plain text, one page per block. Output file: `*_transcription.txt`.
- **`md`**: Markdown with page headers (`## Page N` or `## image_name`). Output file: `*_transcription.md`.
- **`json`**: Structured JSON array with per-page metadata. Output file: `*_transcription.json`.

## Audio Transcription

`--type audio` transcribes speech recordings (mp3, wav, m4a, mp4, mpga, mpeg,
webm, flac, ogg, aac, aiff) to plain text — no timestamps, no diarization.
Two methods:

- **`--method audio-api`** (default for audio): venue set by
  `audio_transcription.provider` in `config/audio_config.yaml` — `openai`
  (default model `gpt-transcribe`; also `gpt-4o-transcribe`,
  `gpt-4o-mini-transcribe`, `whisper-1`; 25 MB/request) or `google`
  (audio-capable Gemini models; ~20 MB inline). Token usage counts toward the
  daily token budget.
- **`--method whisper`**: local faster-whisper, offline, no API key, no
  budget accounting. Handles long files natively.

Long recordings are cut into chunks with ffmpeg (`chunking.target_seconds`,
default 600); each chunk is one JSONL record, so page-level resume and
`--retry-errors` work per chunk. Changing `target_seconds` invalidates an
in-progress resume (the tool detects the drift and restarts the item). Audio
is sync-only: `--batch` is warned about and ignored. `repair.py`
does not cover audio; use `--retry-errors` instead.

```
PY main/transcribe.py --non-interactive --type audio --method audio-api --input /abs/path/recordings --output /abs/path/transcripts
PY main/transcribe.py --non-interactive --type audio --method whisper --input /abs/path/recordings --output /abs/path/transcripts
```

## Configuration Files

All in `<CHRONOTRANSCRIBER_DIR>/config/`. Unless the user instructs otherwise,
use the existing config values and leave files unchanged.

Six config files, each with a tracked `.example.yaml` sibling; the sixth,
`audio_config.yaml`, holds the audio venue, per-provider audio models and
language hints, chunking, local-whisper, ffmpeg, and the speech
postprocessing profile.

The optional `api_keys_config.yaml` remaps each provider's API key to a custom environment variable name (e.g. `openai: OPENAI_API_KEY_2`), with the default env var names applying when the file or a provider entry is omitted.

Full config reference and recommended defaults: see REFERENCE.md in this folder.

## Context Files

Hierarchical context resolution (most specific wins), using the `_transcr_context` filename suffix:

1. **File-specific**: `{input_stem}_transcr_context.txt` next to the input file
2. **Folder-specific**: `{parent_folder}_transcr_context.txt` next to the input's parent folder
3. **General fallback**: `context/transcr_context.txt` in the project root

Keep context files under 4,000 characters. Can also be passed via `--context <path>`.

For context **images** (sent alongside each page image), the same hierarchy applies with the `_transcr_context_image` suffix:

1. **File-specific**: `{input_stem}_transcr_context_image.{ext}`
2. **Folder-specific**: `{parent_folder}_transcr_context_image.{ext}`
3. **General fallback**: `context/transcr_context_image.{ext}`

Override per run with `--context-image <path>`.

## Page Range Filtering

Via `--pages`:

| Syntax | Meaning |
|---|---|
| `5` or `first:5` | First 5 pages |
| `last:5` | Last 5 pages |
| `3-7` | Pages 3 through 7 (1-indexed, inclusive) |
| `3-` | Page 3 to end |
| `-7` | Start to page 7 |
| `1,3,5-8` | Compound: pages 1, 3, and 5 through 8 |

For image folders, indices refer to sorted image files. For audio, indices
refer to planned chunks (default 600 s each), not minutes; a page range on
audio requires ffmpeg.

## Resume & Overwrite

Precedence: CLI flag (`--resume` / `--force`) > `general.resume_mode` in `paths_config.yaml` > hardcoded default (`skip`).

Resume (skip mode) operates at two levels:

1. **File-level**: If the final output file exists, the entire file is skipped.
2. **Page-level**: If a partial `.jsonl` tracking file exists, only remaining pages are transcribed.

Use `--force` / `--overwrite` to reprocess all files. Use `--resume` to explicitly enforce skip mode (e.g. when config has `resume_mode: overwrite`).

By default, pages left as `[transcription error]` count as done and are
**not** retried on resume. Pass `--retry-errors` to re-attempt them on the
next resume run instead.

Temp `.jsonl` tracking files carry a resume-format version tag. Resume
refuses to build on an unversioned artifact left over from an older
run — regenerate the run (or delete the stale `.jsonl`) rather than
resuming onto it. Image folders sort naturally for both page-range
filtering and resume (`page_2` before `page_10`).

## Batch Management

Batch processing submits async jobs (OpenAI, Anthropic, Google; not OpenRouter). Typically completes within 24 hours; 50% cost reduction on OpenAI.

```
PY main/transcribe.py --type pdfs --method gpt --batch --input ./archive --output ./results
PY main/transcribe.py --type pdfs --method gpt --batch --sync-fallback --input ./archive --output ./results
PY main/check_batches.py                       # Check status; auto-downloads completed results
PY main/check_batches.py --output-format json   # Finalize with JSON output
PY main/cancel_batches.py                       # Cancel all non-terminal OpenAI batches
PY main/cancel_batches.py --batch-ids batch_123 # Cancel specific batch(es); routes by id shape

PY main/repair.py --transcription ./results/doc_transcription.txt --errors-only
```

Output files: `*_transcription.{txt,md,json}` (final), `*_temporary.jsonl` (tracking), `*_batch_submission_debug.json` (metadata).

**Batch hardening behavior:**

- Oversized submissions are automatically split into provider-limited parts
  (request-count and byte limits); every part's id is recorded in
  `*_batch_submission_debug.json` for retrieval.
- If batch **submission** fails, the run exits non-zero rather than
  silently reprocessing the whole job synchronously at full price. Pass
  `--sync-fallback` to opt into synchronous fall-back instead.
- Expired or cancelled batches are treated as terminal and finalized
  with `[transcription error]` placeholders instead of polling forever.
- OpenAI batch error-file pages are always parsed and reconciled against
  the submitted request map, so failed pages surface as explicit
  `[transcription error]` placeholders in the final output instead of
  vanishing (completeness contract: one block per expected page). Repair
  correlates results by request index rather than position.

## Post-Processing

Standalone text cleanup for transcription output. Can also be configured in `paths_config.yaml` under `postprocessing:` and applied automatically during transcription.

```
PY main/postprocess.py --input results/doc_transcription.txt --in-place --merge-hyphenation
PY main/postprocess.py --input results/ --recursive --in-place --auto-wrap
PY main/postprocess.py --input doc.txt --in-place --wrap-width 100 --max-blank-lines 1
PY main/postprocess.py --input doc.txt --use-config --in-place
```

## Key Architecture Notes

- **Output writing**: handled by `modules/postprocess/writer.py`.
- **LLM providers**: `modules/llm/providers/` (openai, anthropic, google, openrouter) with the centralized capability registry in `modules/config/capabilities/` (`registry.py`, `detection.py`, `params.py`).
- **MOBI/KFX support**: covers unencrypted MOBI, AZW, AZW3, and KFX files via `--type mobis --method native`.
- **FFmpeg fallback**: JPEG2000 images with sub-8-bit codestreams are automatically decoded via FFmpeg when openjpeg fails; no configuration needed if FFmpeg is on PATH.
- **Original image detail**: GPT-5.4+ models support `original` detail mode (full-resolution image input without tiling), set via `llm_detail: original` in `image_processing_config.yaml`.
- **Prompt caching**: reduces input token costs and latency. Anthropic uses explicit `cache_control` annotations; OpenAI uses automatic prefix caching with optional retention extension; Google is fully automatic; OpenRouter passes through provider-native signals.
- **Custom endpoints**: `modules/llm/providers/custom_provider.py` supports self-hosted OpenAI-compatible endpoints in three modes: structured output, JSON-instructed, and plain text. Configured via `provider: custom` and `custom_endpoint:` block in `model_config.yaml`.
- **Schemas**: in `schemas/` directory. Default: `markdown_transcription_schema.json`. Also: `plain_text_transcription_schema.json`, `plain_text_transcription_with_markers_schema.json`.
- **Token-budget state**: the daily token counter persists under a
  user-level state directory, `~/.chronotranscriber/token_state.json` by
  default (`modules/infra/token_budget.py`), not the CWD. Override via
  `general.state_dir` in `paths_config.yaml`. A legacy per-CWD
  `.chronotranscriber_token_state.json` is adopted once, if present, when
  the resolved state file does not yet exist.
- **Shared cross-tool budget (optional, off by default)**: setting
  `enabled: true` in the `shared_token_budget` block of
  `concurrency_config.yaml` lets ChronoTranscriber, ChronoMiner, and
  AutoExcerpter share ONE combined daily budget. When enabled, combined
  usage lives in
  `~/.chronopipeline/token_ledger.json` with one field per tool — read it
  to see today's split before planning large runs. `daily_token_limit.
  daily_tokens` is enforced against the COMBINED total across all three
  tools; keep the value identical in every tool that runs. A run waiting
  at the limit re-reads `daily_tokens` every poll cycle (~60 s), so a
  mid-wait raise takes effect without restart. Batch API usage never
  counts toward the budget. If the ledger is unavailable the tool
  degrades to its private counter with one warning.
- **EPUB extraction** follows spine order (`modules/documents/`).
- **Content-quality validators** (hallucination loops, truncation,
  system-prompt bleed, excessive line repetition) run inside the retry
  loop and do not flag the schema's own `![Image: ...]` markers, but
  remain **disabled by default** (`content_quality.enabled: false` in
  `concurrency_config.yaml`).

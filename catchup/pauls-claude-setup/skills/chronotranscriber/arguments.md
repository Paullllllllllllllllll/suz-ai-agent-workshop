# ChronoTranscriber — CLI Arguments

All commands run from the project root. Abbreviation: `PY` = `uv run python` (run from project root).

### CLI Agent Contract Flags (all five entry points)

Every parser below is extended with these shared flags
(`modules/core/cli_args.py::add_agent_contract_args`):

| Argument | Type | Description |
|---|---|---|
| `--interactive` | flag | Force the interactive wizard, overriding `interactive_mode` in config (mutually exclusive with `--non-interactive`) |
| `--non-interactive` | flag | Force non-interactive CLI mode, overriding `interactive_mode` in config |
| `--json` | flag | Emit a JSON summary line on stdout at the end. All five entry points emit a real summary: `transcribe.py` uses `{tool, dry_run, items_total, items_processed, items_failed, exit_code}`; the other four carry `{tool, command, ..., exit_code}` with per-script counts (check: finalized/pending/failed; cancel: cancelled/failed; repair: repaired/failed; postprocess: files_processed/files_failed) |

Exit codes are uniform across all five entry points: `0` success, `1` one or
more items failed/partial, `2` usage/configuration error, `130` interrupted.

### Main Transcription (`main/transcribe.py`)

```
PY main/transcribe.py [OPTIONS]
```

| Argument | Type | Description |
|---|---|---|
| `--input`, `-i` | str | Input path (file or directory) |
| `--output`, `-o` | str | Output directory |
| `--type`, `-t` | choice | Document type: `images`, `pdfs`, `epubs`, `mobis`, `audio` |
| `--method`, `-m` | choice | Transcription method: `native`, `tesseract`, `gpt` (documents/images); `audio-api`, `whisper` (audio) |
| `--auto` | flag | Auto mode: infer type/method/paths from config |
| `--batch` | flag | Use batch API (OpenAI/Anthropic/Google; 50% cheaper) |
| `--sync-fallback` | flag | On batch-submission failure, fall back to synchronous (full-price) processing instead of exiting non-zero. Default: off |
| `--schema` | str | Schema name (from `schemas/` directory) |
| `--context` | str | Path to additional context file |
| `--context-image` | str | Path to a context image (e.g. title page, TOC) sent alongside each page image; else hierarchical resolution |
| `--model` | str | Override model ID (e.g. `gpt-5.4`, `claude-sonnet-4-5-20250929`, `gemini-3-pro`) |
| `--provider` | choice | Override provider: `openai`, `anthropic`, `google`, `openrouter`. With `--type audio`: `openai` or `google` only; `--provider`/`--model` then target `audio_config.yaml`, not `model_config.yaml` |
| `--reasoning-effort` | choice | Override reasoning: `none`, `low`, `medium`, `high`, `xhigh` |
| `--model-verbosity` | choice | Override verbosity (GPT-5 family): `concise`, `medium`, `verbose` |
| `--max-output-tokens` | int | Override max output tokens per response |
| `--output-format` | choice | Output format: `txt`, `md`, `json` (overrides `paths_config.yaml`) |
| `--output-mode` | choice | Output layout: `hash` (default, hash-suffixed subdirs), `mirror` (replicate input hierarchy under output root) |
| `--pages` | str | Page range filter (see Page Range Filtering) |
| `--resume` | flag | Explicitly set skip mode (overrides `resume_mode` in config) |
| `--force` / `--overwrite` | flag | Reprocess all files, overwriting existing output (overrides config) |
| `--retry-errors` | flag | On resume, re-process pages left as `[transcription error]`. Default: errors count as done |
| `--files` | str+ | Specific files to process (relative to input) |
| `--recursive` | flag | Process files recursively in subdirectories |
| `--dry-run` | flag | Report discovery + resume/skip counts; no API calls or writes. Always exits `0` |
| `--interactive` / `--non-interactive` / `--json` | flag | Shared agent-contract flags — see table above |

### Repair Transcriptions (`main/repair.py`)

```
PY main/repair.py --transcription <path> [OPTIONS]
```

| Argument | Type | Description |
|---|---|---|
| `--transcription`, `-t` | str (required) | Path to transcription file to repair |
| `--errors-only` | flag | Repair only `[transcription error]` lines |
| `--not-possible` | flag | Include `[Transcription not possible]` lines |
| `--no-text` | flag | Include `[No transcribable text]` lines |
| `--all-failures` | flag | Repair all failure types |
| `--indices` | str | Comma-separated line indices (e.g. `0,5,12`) |
| `--batch` | flag | Use batch processing mode |
| `--interactive` / `--non-interactive` / `--json` | flag | Shared agent-contract flags — see table above |

### Check Batches (`main/check_batches.py`)

```
PY main/check_batches.py [OPTIONS]
```

| Argument | Type | Description |
|---|---|---|
| `--directory`, `-d` | str | Directory to scan for batch files |
| `--no-diagnostics` | flag | Skip API diagnostics |
| `--output-format` | choice | Output format: `txt`, `md`, `json` |
| `--interactive` / `--non-interactive` / `--json` | flag | Shared agent-contract flags — see table above |

### Cancel Batches (`main/cancel_batches.py`)

```
PY main/cancel_batches.py [OPTIONS]
```

| Argument | Type | Description |
|---|---|---|
| `--batch-ids` | str+ | Specific batch IDs to cancel; routed to the right provider by id shape (`msgbatch_...` Anthropic, `batches/...` Google, else OpenAI). Bare invocation (no `--batch-ids`) lists and cancels OpenAI batches only |
| `--force` | flag | Skip confirmation prompt |
| `--interactive` / `--non-interactive` / `--json` | flag | Shared agent-contract flags — see table above |

### Post-Processing (`main/postprocess.py`)

```
PY main/postprocess.py --input <path> [OPTIONS]
```

| Argument | Type | Description |
|---|---|---|
| `--input`, `-i` | str (required) | Input file or directory of `*_transcription.*` files |
| `--output`, `-o` | str | Output path (prints to stdout if omitted and not `--in-place`) |
| `--in-place` | flag | Modify input file(s) in-place |
| `--recursive`, `-r` | flag | Process files recursively when input is a directory |
| `--merge-hyphenation` | flag | Merge words hyphenated across line breaks |
| `--no-collapse-spaces` | flag | Do not collapse long internal runs of spaces |
| `--max-blank-lines` | int | Maximum consecutive blank lines to keep (default: 2) |
| `--tab-size` | int | Spaces per tab (default: 4) |
| `--wrap-width` | int | Hard-wrap lines longer than this width |
| `--auto-wrap` | flag | Auto-detect wrap width from text blocks |
| `--use-config` | flag | Use `paths_config.yaml` postprocessing section as base settings |
| `--interactive` / `--non-interactive` / `--json` | flag | Shared agent-contract flags — see table above |

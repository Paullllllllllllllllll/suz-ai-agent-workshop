# ChronoMiner — CLI Arguments

### Main Extraction (`main/extract.py`)
```
uv run python main/extract.py --schema <SchemaName> --input <path> [options]
```

**All CLI arguments:**
| Argument | Type / Choices | Default | Description |
|---|---|---|---|
| `--schema` | string | (required) | Schema name (e.g., `BibliographicEntries`) |
| `--input` | path | (required) | Input file or directory |
| `--output` | path | config/input dir | Output directory |
| `--output-mode` | `flat` `mirror` | `flat` | Output layout: flat (all in one dir) or mirror (replicate input hierarchy) |
| `--chunking` | `auto` `auto-adjust` `line_ranges` `adjust-line-ranges` | `auto` | Chunking strategy (ignored for visual inputs); `line_ranges` fails loudly if a file's `_line_ranges.txt` sidecar is missing |
| `--batch` | flag | off | Batch processing (50% cost reduction on OpenAI; results within 24h) |
| `--resume` | flag | off | Skip fully processed files; resume partial ones |
| `--force` | flag | off | Reprocess all files, ignoring existing outputs |
| `--model` | string | from config | Override `extraction_model.name` for this run |
| `--reasoning-effort` | `low` `medium` `high` `xhigh` `none` | from config | Override `extraction_model.reasoning.effort` |
| `--verbosity` | `low` `medium` `high` | from config | Override `extraction_model.text.verbosity` (GPT-5 family only) |
| `--max-output-tokens` | int >0 | from config | Override `extraction_model.max_output_tokens` |
| `--temperature` | float | from config | Override `extraction_model.temperature` (0.0-2.0) |
| `--top-p` | float | from config | Override `extraction_model.top_p` (0.0-1.0) |
| `--chunk-size` | int >0 | from config | Override `chunking.default_tokens_per_chunk` |
| `--context` | `auto` `none` or file path | `auto` | Context mode: auto (hierarchical fallback), none (disabled), or path to manual context file |
| `--context-image` | flag | off | Inject a hierarchical context image (`{name}_extract_context.png/jpg`) before the input; uses the `--image-detail` level |
| `--concurrency-limit` | int >0 | from config | Override `concurrency.extraction.concurrency_limit` for this run |
| `--delay` | float >=0 | from config | Override `concurrency.extraction.delay_between_tasks` (seconds) for this run |
| `--image-detail` | `low` `high` `auto` `original` | from config | Image detail level for vision models |
| `--input-type` | `text` `image` `pdf` | auto-detected | Override auto-detected input type |
| `--first-n-chunks` | int | all | Process only the first N chunks/pages per file |
| `--last-n-chunks` | int | all | Process only the last N chunks/pages per file |
| `--page-range` | START-END | all | Process pages START through END (1-based, inclusive, e.g. 70-337) |
| `--quiet` | flag | off | Suppress non-essential output |
| `--interactive` | flag | off | Force interactive UI mode, overriding the config-file mode (mutually exclusive with `--non-interactive`) |
| `--non-interactive` | flag | off | Force non-interactive CLI mode, overriding the config-file mode (mutually exclusive with `--interactive`) |
| `--json` | flag | off | Emit a one-line JSON run summary on stdout at completion |
| `--dry-run` | flag | off | Discover inputs, classify resume state, and report planned actions; zero API calls or side effects |

`--first-n-chunks`, `--last-n-chunks`, and `--page-range` are mutually exclusive. `--force` takes precedence over `--resume`. `--interactive` and `--non-interactive` are mutually exclusive.

### Exit codes and automation

`extract.py`: `0` every file completed (or already complete); `1`
one or more files failed or completed partially; `2` usage/configuration
error or interactive mode requested without a TTY; `130` interrupted
(Ctrl+C).

### Check Batches (`main/check_batches.py`)
```
uv run python main/check_batches.py [--schema <name>] [--input <dir>] [--verbose] [--json] [--interactive | --non-interactive]
```
Lists all batch jobs with status; automatically downloads and processes
completed batches; merges auto-split `_part{n}` submissions back into one
final output. `--json` prints a one-line JSON status summary
(`finalized`/`pending`/`failed` counts) and the command exits `1` while any
batch remains pending or failed, `0` once every batch has resolved.
Submissions persist their schema and model in the tracking records and debug
artifact; finalization detects the recorded schema when it is unambiguous and
configured, so `--input` on a foreign directory no longer silently stamps the
first configured schema (legacy artifacts without a recorded schema fall back
to the assumption with a warning).

### Cancel Batches (`main/cancel_batches.py`)
```
uv run python main/cancel_batches.py [--force] [--interactive | --non-interactive]
```
Cancels non-terminal batches. `--force` skips the confirmation prompt.

### Repair Extractions (`main/repair.py`)
```
uv run python main/repair.py [--schema <name>] [--files f1.jsonl f2.jsonl ...] [--force] [--verbose] [--interactive | --non-interactive]
```
Discovers incomplete jobs, recovers batch IDs from debug artifacts, retrieves
responses, and regenerates outputs. Provider-agnostic: status checks and
result retrieval route through each batch's own backend, so no
`OPENAI_API_KEY` is required at startup for non-OpenAI batches. The
regenerated output is marked `fully_completed` only when no batch failed, is
missing, or is still running; a repair over pending batches is marked
re-runnable with a warning instead of being finalized prematurely.

### Generate Line Ranges (`main/generate_line_ranges.py`)
```
uv run python main/generate_line_ranges.py --input <path> [--tokens N] [--first-n-chunks N | --last-n-chunks N] [--verbose]
```
Creates `{filename}_line_ranges.txt` with token-based chunk boundaries.

### Adjust Line Ranges (`main/adjust_line_ranges.py`)
```
uv run python main/adjust_line_ranges.py --input <path> --schema <name> [--context-window N] [--prompt-path <path>] [--resume] [--force] [--model M] [--reasoning-effort {low,medium,high,xhigh,none}] [--max-output-tokens N] [--temperature T] [--top-p P] [--first-n-chunks N | --last-n-chunks N]
```
LLM-powered semantic boundary detection with certainty scoring and automatic retry. `--input` and `--schema` are both required.

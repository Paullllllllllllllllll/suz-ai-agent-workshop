# AutoExcerpter — CLI Arguments

Argument parsing is two-stage: a pre-pass consumes `--cli`/`--interactive` to
resolve the execution mode (`config.CLI_MODE`) *before* the main parser is
built, because the shape of the main parser (which positionals/flags exist)
depends on that mode. `--cli`/`--interactive`, `--json`, `--dry-run`,
`--retranscribe`, and `--resume`/`--force` are declared identically in both
modes; everything else below the first table is CLI-mode only, except
`--input` and `--output`, which are interactive-mode only.

## Mode control & agent contract (both modes)

| Argument | Type / Choices | Description |
|---|---|---|
| `--cli` | flag | Force CLI (non-interactive) mode, overriding `cli_mode` in app.yaml. Mutually exclusive with `--interactive` |
| `--interactive` | flag | Force interactive mode, overriding `cli_mode` in app.yaml. Mutually exclusive with `--cli` |
| `--json` | flag | Emit one machine-readable JSON run-summary line on stdout at exit |
| `--dry-run` | flag | Discover inputs and classify resume state without any API calls or writes; report the planned actions and exit |
| `--retranscribe` | flag | Force fresh transcription of resumable items instead of reusing logged transcriptions (summary-only resume) |
| `--resume` | flag | Skip files whose output already exists (default behavior). Mutually exclusive with `--force` |
| `--force` / `--overwrite` | flag | Force reprocessing of all files, overwriting existing output. Mutually exclusive with `--resume` |

Exit codes: `0` = all requested items succeeded; `1` = one or more items
failed or were partial; `2` = usage/config error (non-TTY interactive
invocation, or multiple discovered items in CLI mode with neither `--all`
nor `--select`); `130` = user interrupt (Ctrl+C).

## Interactive mode only

| Argument | Type / Choices | Description |
|---|---|---|
| `--input` | path | Path to the folder containing PDFs/image folders, or a single PDF/image folder. Defaults to `input_folder_path` in app.yaml |
| `--output` | path | Output directory for transcriptions and summaries. Defaults to `output_folder_path` in app.yaml |

## CLI mode only

| Argument | Type / Choices | Description |
|---|---|---|
| `input` (positional) | path | Path to PDF, image folder, or directory containing items |
| `output` (positional) | path | Output directory for transcriptions and summaries |
| `--input-path` | path | Named input path (overrides positional input) |
| `--output-path` | path | Named output path (overrides positional output) |
| `--all` | flag | Process all discovered items without prompting |
| `--select` | string | Select by number (`5`), range (`1-10`), comma-list (`1,3,5`), or filename pattern (`Mennell`). Unmatched/out-of-range parts are logged as a warning, not a hard error |
| `--context` | string | Topics for focused summarization (e.g., `"Food History, Wages, Early Modern"`) |
| `--summarize` / `--no-summarize` | flag | Enable/disable summarization phase. Overrides `summarize` in app.yaml |
| `--cleanup` / `--no-cleanup` | flag | Enable/disable cleanup of temporary working directory. Overrides `delete_temp_working_dir` in app.yaml |
| `--model` | string | Set both transcription and summary model names |
| `--transcription-model` | string | Override transcription model only |
| `--summary-model` | string | Override summary model only |
| `--reasoning-effort` | none/minimal/low/medium/high/xhigh | Set reasoning effort for both models |
| `--transcription-reasoning-effort` | none/minimal/low/medium/high/xhigh | Override transcription reasoning effort |
| `--summary-reasoning-effort` | none/minimal/low/medium/high/xhigh | Override summary reasoning effort |
| `--verbosity` | low/medium/high | Set output verbosity for both models (GPT-5 family only) |
| `--transcription-verbosity` | low/medium/high | Override transcription verbosity |
| `--summary-verbosity` | low/medium/high | Override summary verbosity |
| `--max-output-tokens` | positive int | Set max output tokens for both models |
| `--transcription-max-output-tokens` | positive int | Override transcription max output tokens |
| `--summary-max-output-tokens` | positive int | Override summary max output tokens |
| `--temperature` | float (0.0-2.0) | Set temperature for both models |
| `--transcription-temperature` | float (0.0-2.0) | Override transcription temperature |
| `--summary-temperature` | float (0.0-2.0) | Override summary temperature |
| `--provider` | openai/anthropic/google/openrouter/custom | Set provider for both models |
| `--transcription-provider` | openai/anthropic/google/openrouter/custom | Override transcription provider |
| `--summary-provider` | openai/anthropic/google/openrouter/custom | Override summary provider |

`input`/`output` (or `--input-path`/`--output-path`) are both required in CLI
mode; the parser errors out immediately if either is missing. When a
directory resolves to more than one discovered item, CLI mode now requires
`--all` or `--select` -- omitting both exits 2 instead of silently processing
only the first item.

CLI arguments apply runtime overrides to `model.yaml` and `app.yaml` without modifying files on disk. Concurrency, retry, rate-limit, citation, and token-limit settings remain config-only and are not exposed via CLI.

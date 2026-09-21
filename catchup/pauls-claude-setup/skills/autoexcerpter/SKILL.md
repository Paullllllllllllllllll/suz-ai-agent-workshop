---
name: autoexcerpter
description: Transcribe and summarize academic PDFs/images with enriched citations.
disable-model-invocation: false
argument-hint: "<input-path> <output-path> [--options]"
---

# AutoExcerpter Skill

AutoExcerpter is an intelligent document processing pipeline that transcribes and summarizes PDF documents and image collections using vision-enabled LLMs via LangChain. It produces structured text with optional summaries and enriched bibliographic citations. Supports OpenAI, Anthropic, Google, and OpenRouter providers, as well as custom OpenAI-compatible endpoints.

**Repository root**: `<AUTOEXCERPTER_DIR>`

## First-time setup

1. Clone the tool:
   `git clone https://github.com/Paullllllllllllllllll/AutoExcerpter`
2. In the clone, run `uv sync` to create the virtual environment.
3. Set at least one API key as an environment variable: `OPENAI_API_KEY`,
   `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, or `OPENROUTER_API_KEY`.
4. Replace every `<AUTOEXCERPTER_DIR>` in this skill folder with the path of
   your clone.

## Prerequisites

- Python 3.13+
- One API key env var: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`,
  or `OPENROUTER_API_KEY`
- uv-managed virtual environment at `<AUTOEXCERPTER_DIR>/.venv`. Set up: `uv sync`.
- Entry point: `main/excerpt.py`

## CLI Usage (Interactive + CLI Mode)

Execution mode is normally set by `cli_mode` in app.yaml, but `--cli` /
`--interactive` override it at invocation time -- **prefer these flags over
editing the gitignored YAML** when driving the tool as an agent.

Relative input/output paths resolve against the current working directory --
run from the repository root, or pass absolute paths; `~` and drive-relative
paths are expanded. (Unlike ChronoTranscriber, there is no config-based path
rebasing.)

### Interactive Mode (default, `cli_mode: false` in app.yaml)

```bash
uv run python main/excerpt.py [--resume | --force]
uv run python main/excerpt.py --interactive   # force interactive even if app.yaml sets cli_mode: true
```

Selection syntax at the interactive prompt: single (`1`), multiple (`1,3,5`), ranges (`1-5`), `all`, or filename search (`Mennell`). Exit at any prompt with `exit`, `quit`, or `q`. Interactive mode requires a TTY; a non-TTY invocation (e.g. piped/scripted) fails fast with exit code 2 rather than hanging.

### CLI Mode (set `cli_mode: true` in app.yaml, or pass `--cli`)

```bash
# Positional input/output
uv run python main/excerpt.py <input> <output> [--all] [--select PATTERN] [--context TOPICS] [--model MODEL] [--resume | --force] ...

# Named paths (override positional when both provided)
python main/excerpt.py --input-path <input> --output-path <output> [options]

# Force CLI mode without touching app.yaml
python main/excerpt.py --cli <input> <output> --all
```

**When the input directory contains multiple discovered items, `--all` or `--select` is required in CLI mode.** Omitting both is now a usage error (exit code 2) rather than silently processing only the first item -- always pass one or the other for multi-item inputs.

### Agent Contract (exit codes, `--json`, `--dry-run`)

- Exit codes: `0` = all requested items succeeded; `1` = one or more items failed or were partial; `2` = usage/config error (non-TTY interactive invocation, or multiple discovered items with neither `--all` nor `--select`); `130` = user interrupt (Ctrl+C).
- `--json`: emit one machine-readable JSON run-summary line on stdout at exit (`items_total`, `items_complete`, `items_failed`, `items_skipped`, `outputs`, `tokens_used_today`, `daily_token_limit`).
- `--dry-run`: discover inputs and classify resume state without any API calls or writes; reports the planned action per item (and, with `--json`, a JSON plan) then exits 0.
- Malformed or out-of-range `--select` parts (e.g. `99` when only 10 items exist) are logged as a warning naming the unmatched part(s) rather than failing silently.

### All CLI Arguments

**Read [arguments.md](arguments.md) for the full argument reference.**

## Configuration Files

All config files live in `<AUTOEXCERPTER_DIR>/config/defaults/`. **Unless the
user instructs otherwise, apply these defaults when invoking AutoExcerpter:**
(1) output files are written beside each input file
(`input_paths_is_output_path: true`), (2) temporary working directories are
deleted after processing (`delete_temp_working_dir: true` / `--cleanup`), and
(3) OpenAI flex processing is enabled (`service_tier: flex` under
`api_requests.transcription` in concurrency.yaml). **Leave all other configs
unchanged unless the user specifies otherwise.**

Summaries run inline within the transcription workers and share the transcription phase's concurrency limit and one rate limiter per provider -- there is no separate `api_requests.summary` block in concurrency.yaml; the summary phase's OpenAI service tier simply falls back to the transcription tier.

The optional `api_keys.yaml` remaps each provider to the NAME of the environment variable holding its API key (e.g. `openai: OPENAI_API_KEY_2`), letting you swap keys between runs by editing one file; defaults apply when the file or an entry is omitted.

Full config reference and recommended defaults: see REFERENCE.md in this folder.

## Context System (Hierarchical Resolution)

Summary context guides the model to focus on specific topics. Resolution order (highest priority first):

1. **CLI/Interactive context**: `--context "Food History, Wages"` or entered at the interactive prompt
2. **File-specific**: `<filename>_summary_context.txt` next to the input file
3. **Folder-specific**: `<foldername>_summary_context.txt` in the parent directory
4. **General fallback**: `context/summary/general.txt` in the project root

If no context is found through any method, summarization proceeds without topic-specific focus.

## Resume & Force

AutoExcerpter uses a checkpoint/resume system managed by `pipeline/resume.py`. The `ProcessingState` enum tracks item state:

| State | Meaning |
|---|---|
| `COMPLETE` | All expected outputs exist AND the log's logged page count is not short of the document's total (a stalled/crashed run that wrote complete-looking outputs is never trusted as COMPLETE) |
| `TRANSCRIPTION_ONLY` | The .txt transcription exists but summary outputs are missing, or the log shows fewer pages than expected |
| `PARTIAL` | A transcription JSONL log exists with entries (mid-document crash recovery) |
| `NONE` | No output exists; must process from scratch |

- `--resume` (default): skips COMPLETE items; for TRANSCRIPTION_ONLY/PARTIAL items, **reuses the logged transcriptions with zero transcription API calls** and only (re)generates the missing summaries/pages -- a crashed run no longer loses already-completed pages' summaries. If the logged transcription model differs from the currently configured model, a warning is logged and recorded in the output metadata (mixed-provenance notice).
- `--retranscribe`: forces a fresh transcription pass for resumable items instead of reusing logged transcriptions (use after changing the transcription model/prompt when you want consistent provenance).
- `--force` / `--overwrite`: treats all items as NONE regardless of existing output.

**Content-filter failures.** OpenAI's content filter can stop pages dense with long verbatim quotations from copyrighted texts. Such a page fails after one call, without retries, with `error_type` `content_filter` (or `refusal`) in the working log, and counts as failed for resume. Repair it with `--resume` using another provider; the OpenRouter model `z-ai/glm-5.3-flash` has handled every such page so far.

`--resume`/`--force` are mutually exclusive; `--retranscribe` combines with `--resume`. All three are available in both interactive and CLI modes.

**Working logs are true JSONL** (one JSON object per line) with a format-version marker in the header; crash-truncated tail lines are dropped on parse. Old logs lacking this marker are **refused for resume** -- delete the stale `_working_files/` directory (or run with `--force`) to reprocess such items from scratch.

## Output Files

For each processed document, AutoExcerpter generates:

- `<name>.txt` -- Full verbatim transcription with metadata header, markdown formatting, LaTeX equations, page number XML tags, footnotes, tables, and visual element descriptions. A page without a printed page number is preceded by `<page_break pdf="N"/>` (`image="N"` for image folders), N being its 1-based input position
- `<name>.docx` -- Formatted Word summary with page-by-page bullet points, consolidated bibliography with deduplicated citations, page ranges, and clickable hyperlinks (if `summarize: true` and `summary_output.docx: true`)
- `<name>.md` -- Markdown summary with identical content structure, LaTeX preserved as `$...$` / `$$...$$` (if `summarize: true` and `summary_output.markdown: true`)
- `<name>_working_files/` -- JSON logs for transcription and summary phases with per-page metadata, timing, and retry statistics (deleted if `delete_temp_working_dir: true`)

## Citation Features

Deduplication and enrichment run through a single `CitationManager` pass (`rendering/citations.py`), shared by both the DOCX and Markdown writers, so citations are consolidated identically across output formats.

- **Folding + structured keys**: citation text is Unicode/diacritic-folded (NFKD, combining marks stripped, casefolded, curly quotes/dashes and `&` normalized) and keyed by `(author, year, volume, title)`, so `Müller`/`Muller` or accent/quote variants collapse together while different editions never do.
- **Conservative fuzzy consolidation**: within a `(first-author surname, year)` block, near-identical variants merge only when `SequenceMatcher` ratio (`citation.merge_ratio`) or token-set Jaccard (`citation.merge_jaccard`) clears its threshold. Different years or volumes never merge. Every merge is logged.
- **Page range tracking** with consolidation per numbering system, never mixed in one range: printed arabic and roman pages (`pp. 5, 12-15`, `pp. x-xii`), pages without a printed number by position (`PDF p. 7`, `Image 7`), and numbers inferred from neighboring pages in brackets (`p. [6]`), e.g. `pp. 5-7; PDF p. 12`.
- **OpenAlex API metadata enrichment** (DOI, authors, publication year, venue), toggled via `enable_openalex_enrichment`, run exactly once per document. When a title can be isolated (text after `(Year).`, or an italicized/quoted title), the lookup uses a `title.search` filter with the cited year +/-1 (either year of a reprint); otherwise the free-text search. A candidate links only when title-word overlap clears `citation.match_title_overlap` **and** a corroborating signal matches (publication year within +/-1, or the candidate author surname appears in the citation) -- stricter than before, preferring no link over a wrong one. After enrichment, entries sharing a DOI/OpenAlex id undergo a second merge pass.
- **`citation.max_api_requests` caps the number of citations submitted for OpenAlex lookup** (each looked-up citation can issue up to 6 HTTP requests). All requests run through one shared HTTP session per enrichment run, the polite delay applies to every request including misses, and results are cached persistently in the state directory across runs and items, so repeat lookups do not re-hit the API.
- Clickable hyperlinks for citations with DOI information in DOCX output.
- Consolidated bibliography section, sorted stably by folded author, year, and title.

Tune deduplication aggressiveness in `app.yaml` under `citation`: `merge_ratio` (default 0.90), `merge_jaccard` (default 0.85), `match_title_overlap` (default 0.5). Lower thresholds merge more aggressively (riskier).

## Token Budget Tracking

Daily token limits are enforced via `llm/token_tracker.py`. Persistent state (and the OpenAlex citation cache) now live under a **user-level state directory**, `~/.autoexcerpter` by default, resolved by `config/state.py`. Override the location via `paths.state_dir` in `app.yaml`. A legacy `.autoexcerpter_token_state.json` in the project working directory is adopted once (copied into the state dir) when the user-level file is absent, so upgrading preserves accumulated state.

- Tracks `usage.total_tokens` from every API call (transcription + summary, including retries)
- Enforced per page (transcription + optional summary reserved together), not just between files, so a single large document cannot overshoot by a whole file's worth; when the budget is exhausted mid-file, in-flight pages drain, the run waits for the daily reset, then resumes the still-pending pages from the log
- Resets automatically at 00:01 UTC, one minute after OpenAI's 00:00 UTC free-token reset; state survives application restarts
- When the limit is reached, processing pauses and displays the reset ETA
- In interactive mode, type `q` + Enter during the wait to cancel immediately
- Thread-safe for concurrent API calls
- Delete or edit the state file in the state directory manually to resync with provider dashboards

**Shared cross-tool budget (optional, off by default).** Setting
`enabled: true` in the `shared_token_budget` block of `app.yaml` lets
AutoExcerpter, ChronoMiner, and ChronoTranscriber share ONE combined daily
budget. When enabled, combined usage lives in
`~/.chronopipeline/token_ledger.json` with one field per tool — read it to see
today's split before planning large runs. `daily_token_limit.daily_tokens` is
enforced against the COMBINED total across all three tools; keep the value
identical in every tool that runs. The `--json` run summary reports the tool's
own `tokens_used_today` plus `combined_tokens_today`, and token summaries
display the per-tool breakdown. A run waiting at the limit re-reads
`daily_tokens` every poll cycle, so a mid-wait raise takes effect without
restart. If the ledger is unavailable the tool degrades to its private counter
with one warning.

## Page Numbering

Handles documents with mixed Roman-numeral (preface) and Arabic (main text)
numbering. The summary schema reports `page_number_type` as `"roman"`,
`"arabic"`, or `"none"`, and `page_types` as an array of per-page
classifications.

No output passes a position off as a printed page number. A page without a
`<page_number>` tag gets `page_number_integer: null` and is headed
`[No printed number; PDF p. N]` in the summaries. A number inferred for a
single untagged page between two numbered neighbors is bracketed: `Page [6]`,
cited as `p. [6]`. A summary page number that disagrees with the page's tags
is logged as a warning, never overwritten.

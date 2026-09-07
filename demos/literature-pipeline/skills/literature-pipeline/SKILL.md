---
name: literature-pipeline
description: End-to-end literature processing — select works, deep-read via the literature-reader agent, condense into the project's literature overview xlsx, and maintain the reading registry CSV. Use for bulk or staged processing of academic sources.
disable-model-invocation: true
argument-hint: "[works...] [--stage <stage>] [--audit] [--all-pending]"
---

# Literature Pipeline (Workshop Edition)

End-to-end orchestration: select works, deep-read each one with the
`literature-reader` agent, build condensation entries, update the literature
overview xlsx, maintain the reading registry CSV.

## Invocation

1. Full pipeline: `/literature-pipeline Helfer 2023, Baranzini 2008`
2. Resume at stage: `/literature-pipeline Baranzini 2008 --stage read`
3. Single stage: `/literature-pipeline --stage xlsx`
4. Audit (find incomplete rows): `/literature-pipeline --audit`
5. Everything not yet done: `/literature-pipeline --all-pending`

## Canonical paths

All paths are relative to the project root (the folder holding
`sample_library/`):

```text
LIB      = sample_library/
REGISTRY = sample_library/reading_registry.csv
OVERVIEW = sample_library/DEMO_literature_overview.xlsx
```

The registry has one row per work with the columns `work_id`, `citation`,
`doi`, `status`, `summary_file`, `date_read`. `status` moves through
`pending` -> `summarized` -> `condensed`.

## Pipeline stages

| Stage | Tool | Registry effect |
|-------|------|-----------------|
| 0 Work selection | Inline | — |
| 1 Transcription | External tool — SKIPPED in this edition | — |
| 2 Deep reading | `literature-reader` agent | status = summarized |
| 3 Condensation + xlsx | openpyxl | status = condensed |
| 4 Registry update | Inline CSV write | all columns current |

## Stage 0: Work selection

Accept: author-year strings, registry `work_id` numbers, file paths, or
`--all-pending`. Resolve author-year strings by globbing
`LIB/*<Surname>*<Year>*.pdf`. Check for an existing summary `.md` beside the
PDF. Present a pre-flight table (work, PDF found, current status) and confirm
before proceeding.

## Stage 1: Transcription — skipped in the workshop edition

The original workflow runs an external OCR/summarization tool here, producing
a plain-text transcription and a first summary beside each PDF. That tool is
not bundled; skip this stage and read the PDFs directly in Stage 2. A
pre-made summary ships for one paper (Helfer, Grossmann, and Osikominu 2023),
so its registry row already starts at `condensed`.

## Stage 2: Deep reading

Skip if `status` is `summarized` or `condensed` and the registry's
`summary_file` exists. Otherwise dispatch the `literature-reader` agent with
the PDF path and instruct it to return a structured entry: full citation,
research question, data, method, main findings with magnitudes, limitations,
and quotable passages with page numbers.

Write the agent's entry to `LIB/<PDF base name> summary.md`, then set
`status = summarized` and record `summary_file` and `date_read`.

## Stage 3: Condensation + xlsx update

Skip if `status = condensed`. Two phases:

### 3a: Construct condensation

From the summary file, build one overview row per work:

```text
Citation:    <full citation>
DOI:         <doi>
Question:    <one sentence>
Data:        <sources, coverage, units>
Method:      <identification / approach in one sentence>
Key finding: <main result with magnitudes>
Relevance:   <High / Medium / Low, with a short reason>
```

Present the condensation to the user for approval before 3b. Do not write
anything until approved.

### 3b: Apply to xlsx

`OVERVIEW` has one sheet, `Literature`, with the header row `Citation`,
`DOI`, `Question`, `Data`, `Method`, `Key finding`, `Relevance`.

Row matching: case-insensitive first-author surname substring plus exact year
in the `Citation` column. No match = append a new row. Match = update the
remaining columns. Back up the xlsx (copy it beside itself with a date
suffix) before writing; use openpyxl for the write.

## Stage 4: Registry update

Update the CSV row: set `status` and the remaining columns to current values.
New works get the next sequential `work_id`. Write with `encoding="utf-8"`,
`newline="\n"`, and — when using Python's `csv` module — also
`lineterminator="\n"` (the module's default emits `\r\n` regardless of the
file's newline setting).

## Constraints

- Never modify source PDFs.
- Always back up the xlsx before modification.
- Condensation must be user-approved before any xlsx write.
- Do not update the registry until the xlsx write succeeds.
- Missing files: note it in the pre-flight table and skip the work.
- Already-done works: confirm with the user before reprocessing.

Footnote: on Windows machines with the Everything CLI (`es.exe`) installed,
`es -path <LIB> <Surname> <Year> ext:pdf` resolves files faster than
globbing; this is an optional speed-up, not a requirement.

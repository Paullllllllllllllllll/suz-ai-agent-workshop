# Demo: literature-pipeline (workshop edition)

This backup demo runs an end-to-end literature workflow on a bundled sample
library of three open-access papers. The workflow selects works from the
library, deep-reads each one with a dedicated subagent, condenses the reading
into an overview spreadsheet, and keeps a reading registry in sync. Everything
runs inside this folder without external tools or network access. To wire the
same pattern to your own Zotero library at home, see
`../zotero-extension.md`.

## Two-line starter

The version you could run on your own PDF folder today, no skills required:

```text
Deep-read the PDFs in sample_library/ that the reading registry does not mark
as done, write a structured summary for each, add one condensed row per paper
to DEMO_literature_overview.xlsx (show me each row for approval first), and
update the reading registry to match.
```

## Where the demo enters the workflow

The full pipeline has five stages: work selection, transcription, deep
reading, condensation into the overview spreadsheet, and registry update. This
workshop edition starts at the deep-read stage because the transcription stage
depends on an external OCR/summarization tool that is not bundled here. In the
original workflow, that transcription stage runs over each PDF and leaves a
plain-text transcription plus a first summary beside it; here we skip it and
read the PDFs directly. The `sample_library/` folder ships with a pre-made
summary for one paper (Helfer, Grossmann, and Osikominu 2023), so the registry
starts with one work already done and the skip-if-done logic can demonstrate
how it behaves.

## Run the demo

1. Copy this whole `literature-pipeline/` folder to a location outside the
   cloned workshop repository.
2. Install the skill and the agent into the copy (see the next section).
3. Start Claude Code in the copy's root and run `/literature-pipeline
   --all-pending`.

When the demo finishes, the `literature-reader` agent should have deep-read
the two pending papers, shown each condensation for approval, added the
approved rows to `sample_library/DEMO_literature_overview.xlsx`, and updated
`sample_library/reading_registry.csv` to mark all three works done.

## Installing the skill and the agent

Both are project-level. Copy them into the project copy's `.claude/` folder so
that these two files exist:

```text
your-copy/.claude/skills/literature-pipeline/SKILL.md
your-copy/.claude/agents/literature-reader.md
```

Restart Claude Code in the copy's root; `/literature-pipeline` appears as a
slash command and the `literature-reader` agent becomes available for
dispatch.

## The bundled sample library

Three open-access papers on Swiss housing, all redistributable under Creative
Commons licenses:

| File | License | DOI |
| --- | --- | --- |
| Helfer Grossmann Osikominu 2023 How Does Immigration Affect Housing Costs in Switzerland.pdf | CC BY 4.0 | 10.1186/s41937-023-00110-1 |
| Baranzini Schaerer Ramirez Thalmann 2008 Do Foreigners Pay Higher Rents Geneva Zurich.pdf | CC BY 2.0 (per the publisher's records; the 2008 PDF itself carries no license notice) | 10.1007/BF03399272 |
| Debrunner Hengstermann 2023 Vier Thesen zur effektiven Umsetzung der Innenentwicklung in der Schweiz.pdf (German) | CC BY 4.0 | 10.1080/02513625.2023.2229632 |

`sample_library/` also carries the reading registry
(`reading_registry.csv`), the overview spreadsheet
(`DEMO_literature_overview.xlsx`), and the pre-made Helfer summary.

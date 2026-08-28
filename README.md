# SUZ AI Agent Workshop v0.4.0

This repository holds the materials for the one-day workshop "AI Agents
for Social Science Research" at the Department of Sociology (SUZ),
University of Zurich.

The workshop runs on Tuesday, 8 September 2026, from 9:00 to 17:00
(door opens at 8:30).

## Programme

| Time  | Block                                                     |
|-------|-----------------------------------------------------------|
| 8:30  | Door opens; setup help desk                               |
| 9:00  | LLMs and coding agents (type-along)                       |
| 10:00 | Guided walkthrough: one research workflow, CLI + Desktop  |
| 12:15 | Lunch                                                     |
| 13:15 | Advanced workflow demos: a research hub, then a dataset   |
| 14:30 | One literature workflow, live                             |
| 14:50 | Hands-on in tracks (pipelines, quant, literature, open)   |
| 16:30 | Open discussion: responsible AI use; feedback             |
| 17:00 | End                                                       |

## Quick start (before the workshop)

1. Follow the install guide for your system (`install/windows.md` or
   `install/macos.md`) before 8 September. Installation takes 30 to 45
   minutes and requires a Claude account.
2. Clone this repository before the workshop, or join us at 10:00 to do
   it together:

   ```bash
   git clone https://github.com/Paullllllllllllllllll/suz-ai-agent-workshop.git
   ```

3. Bring your laptop and, if you have one, a small project or dataset
   of your own to work with in the afternoon. Ensure the data is anonymized
   or not privacy-protected.

## Repository layout

The repository is organized into five top-level folders:

```text
install/       setup guides (Windows, macOS; Claude Code CLI + Desktop)
walkthrough/   morning: step-by-step handout and the toy project
demos/         afternoon: workshop editions of advanced skills
tryouts/       afternoon: starter packages per hands-on track
catchup/       added after the workshop for those who missed it
```

## Changelog

- **v0.4.0** (28 August 2026) -- six readings added to READING_LIST.md
  from Nico's side, per the 26 August division (Paul preps the list,
  Nico adds his own material). Two new sections: "What this means for
  our own work", carrying the closing discussion's new fifth theme, and
  "Synthetic participants: standing in for people", which is the
  literature behind the afternoon's dataset block and the one thing the
  list did not cover. The defensible-core section gains Mittelstadt on
  why principles alone do not produce ethical practice, Raji et al. on
  internal algorithmic auditing (the scholarly form of the audit the
  hands-on block asks for), and Binz et al. on how LLMs should change
  the practice of science. Section 4 renumbered to 5; the intro now
  names five questions rather than four.
- **v0.3.0** (26 August 2026) -- afternoon restructured per the joint
  facilitators' decision: the demos run as one block (a research hub,
  then a synthetic dataset from a codebook), followed by a live
  literature workflow at 14:30; hands-on begins at 14:50 with a fourth,
  open track; the day closes with an open discussion on responsible AI
  use instead of the slide-based closing block. New READING_LIST.md:
  an annotated reading list behind that discussion (deskilling and
  cognitive offloading, AI-text detection, dependence and affective
  use, responsible research use), which also travels with the follow-up
  package. Handout and programme updated to the new schedule.
- **v0.2.0** (13 August 2026) -- full materials build-out: OS-specific
  install guides (account, Desktop app, CLI, git, uv); the complete
  morning walkthrough handout and the swiss-rents toy project (skills,
  rule, subagents, two datasets with offline fallbacks, five licensed
  open-access papers); workshop editions of the run-pipeline,
  harden-pipeline, and literature-pipeline skills with self-contained
  sample projects and the Zotero extension guide; the literature
  try-out package; programme updated to the agreed run of show. All
  materials verified by isolated end-to-end dry runs.
- **v0.1.0** (12 August 2026) -- repository skeleton: folder layout,
  programme, quick-start instructions, and stub files for the install
  guides, walkthrough, demos, and try-out packages.

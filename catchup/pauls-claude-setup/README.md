# Paul's Claude Code setup

This folder holds a working selection of my own Claude Code configuration: an
example `CLAUDE.md`, rule files, skills, subagents, and an output style. I use
them daily for research, writing, and teaching. Everything personal (paths,
projects, accounts) has been removed or replaced by placeholders, so each file
needs a short read and some adapting before it fits your work.

The folder mirrors the layout of `~/.claude/`, the user-level configuration
directory Claude Code reads in every project (`C:\Users\<you>\.claude\` on
Windows, `/Users/<you>/.claude/` on macOS).

```text
CLAUDE.md        example global instructions, with placeholders
rules/           conventions that load automatically for matching files
skills/          one folder per skill (SKILL.md, plus scripts where needed)
agents/          custom subagent definitions
output-styles/   the output style I work with
```

## How to install

Take only what you need; the parts are independent.

1. Copy a skill folder into `~/.claude/skills/`, an agent file into
   `~/.claude/agents/`, a rule into `~/.claude/rules/`, and the output style
   into `~/.claude/output-styles/`. To use something in one project only, copy
   it into that project's `.claude/` folder instead.
2. For `CLAUDE.md`: if you already have a `~/.claude/CLAUDE.md`, merge the
   sections you want into it; otherwise copy the file and fill in the bracketed
   placeholders.
3. Restart Claude Code. Skills appear under `/` (e.g. `/grill-me`), agents under
   `/agents`, and the output style under `/output-style`.
4. Read each file you install. Skills and rules are instructions to the agent,
   and you should know what you are telling it to do.

Alternatively, point Claude Code at this folder and ask it to install the parts
you want and adapt them to your setup.

## What is in here

### CLAUDE.md and rules

| File | What it does |
|---|---|
| `CLAUDE.md` | Global instructions: who you are, where your files live, backups before risky edits, how to edit and document, commit policy |
| `rules/data-analysis.md` | Analysis conventions for notebooks and scripts: never drop rows silently, document missing-data handling, fixed seeds, stop at methodological forks, prefer the simpler model |
| `rules/python-conventions.md` | `uv` as package manager, PEP 8, explicit UTF-8 file encoding |
| `rules/markdown-style.md` | A minimal rule file: line length, headings, code fences |

A rule with a `paths:` block in its header loads only when Claude works on
matching files; a rule without one loads in every session.

### Output style

`output-styles/research-assistant.md` sets the register (formal, direct, no
filler), prose rules, number and date formatting, and how Claude delegates work
to subagents and which model each subagent gets. Activate it with
`/output-style`. The number and date formats are my conventions; change them to
yours.

### Skills: research tools

These four skills drive open-source tools I wrote for historical and
social-science source work. Each tool is a separate repository; the skill
tells Claude how to run it.

| Skill | Tool |
|---|---|
| `chronodownloader` | Batch download of digitized sources from digital libraries: [ChronoDownloader](https://github.com/Paullllllllllllllllll/ChronoDownloader) |
| `chronotranscriber` | Transcription of PDFs, scans, and audio via OCR and LLMs: [ChronoTranscriber](https://github.com/Paullllllllllllllllll/ChronoTranscriber) |
| `chronominer` | Schema-based extraction of structured data from texts, images, and PDFs: [ChronoMiner](https://github.com/Paullllllllllllllllll/ChronoMiner) |
| `autoexcerpter` | Transcription and structured summaries of academic PDFs: [AutoExcerpter](https://github.com/Paullllllllllllllllll/AutoExcerpter) |

First-time use: clone the tool's repository, run `uv sync` in it as described
in the skill's "First-time setup" section, set an API key for your LLM provider
(e.g. `OPENAI_API_KEY`), and replace the placeholder (e.g. `<CHRONOMINER_DIR>`)
in the skill folder with the path of your clone. The tools call paid APIs;
check the cost settings in each tool's configuration before a large run.

### Skills: literature and Zotero

| Skill | What it does |
|---|---|
| `find-literature` | Searches your Zotero library and returns citations (Chicago, BibTeX, CSL-JSON) and PDF paths; read-only |
| `zotero-curator` | Cleans up a Zotero library: duplicates, wrong or missing metadata, tagging with a controlled vocabulary, and importing loose PDFs |

Both need Zotero running with its local API enabled (Zotero 7: Settings,
Advanced, "Allow other applications on this computer to communicate with
Zotero"). Each skill folder is a small `uv` project; run `uv sync` in it once.
`zotero_doc.md` in each folder has the details.

`zotero-curator` never writes to the Zotero database directly. It generates a
JavaScript snippet that you review and run yourself in Zotero (Tools,
Developer, Run JavaScript), so back up your Zotero data folder before applying
it. Edit `tag_vocabulary.yaml` before the tagging mode; the shipped values are
examples. The import mode is only for libraries that keep PDFs as linked files
in a folder outside Zotero; it needs the `LIT_ROOT` environment variable set to
that folder.

### Skills: writing, code, and working with Claude

| Skill | What it does |
|---|---|
| `grill-me` | Claude interviews you about a plan or design, one question at a time, until the open decisions are settled |
| `handoff` | Writes a handoff document so a fresh session can continue the current task |
| `writing-great-skills` | Reference for writing your own skills |
| `unslop` | Checklist that removes AI-typical phrasing and mannered prose from a draft |
| `declutter` | Removes dead code, tangents, and needless complexity from a notebook or module |
| `commit-rules` | Conventions for commits, pushes, versioning, and changelogs |
| `documentation-reorganization` | Audits and consolidates a project's CLAUDE.md, README, and docs |
| `flashcards` | Turns any source into Anki-importable flashcards |

### Agents

| Agent | What it does |
|---|---|
| `literature-reader` | Reads an academic text closely and returns a structured research summary |
| `peer-reviewer` | Writes an independent referee report on a manuscript; read-only |
| `flashcard-maker` | Produces Anki decks; used by the `flashcards` skill |
| `translator` | Translates historical texts and academic prose, with philological notes |

Each agent file names the model it runs on (`sonnet` or `opus`). Change it to
match your plan and budget.

## Attribution

`grill-me`, `handoff`, and `writing-great-skills` are adapted from Matt
Pocock's skills collection: [github.com/mattpocock/skills](https://github.com/mattpocock/skills)
(website: [aihero.dev](https://www.aihero.dev)). `writing-great-skills` has
since been renamed `writing-for-agents` there. His repository is published
under the MIT License:

> Copyright (c) 2026 Matt Pocock
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in
> all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

# Global Rules

Example of a user-level `CLAUDE.md` (`~/.claude/CLAUDE.md`). Claude Code loads it
into every session, in every project. Replace everything in square brackets with
your own details and delete the sections you do not need.

## 1. About me

- [Position, discipline, and institution; e.g. doctoral student in sociology,
  University of X.]
- [Research focus in one or two lines: topics, periods, methods.]
- [Tools you work with: e.g. R and Stata for analysis, Zotero for references,
  LaTeX or Word for writing.]
- [Anything that changes how Claude should help you: e.g. "I am new to Python;
  explain code you write in one or two sentences."]

## 2. Where things live

Each location has its own `CLAUDE.md` with further detail.

```text
[~/Projects/]            one folder per research project
  {Project}/             CLAUDE.md, data/, notebooks/ or scripts/, paper/, backup/
[~/Literature/]          PDFs, linked from Zotero
[~/Data/]                shared raw data (READ-ONLY)
[~/Teaching/]            course materials
```

### Conventions

- **Raw data:** read and copy freely from the shared data folder; never add,
  modify, or delete files there without my explicit permission.
- **Project CLAUDE.md files** are short indexes of the folder layout and the
  commands to run. Update them when the folder layout changes.

## 3. Backups

Before changing a dataset, a paper draft, or another file that cannot easily be
regenerated and is not tracked by git, back it up to a `backup/` folder at the
project root as a `.zip` archive:

- Filename: `<original_filename>_DD_MM_YYYY_v1.zip`, then `_v2`, and so on. For
  several files at once, use a short bundle name such as the project name.
- Never overwrite an existing backup; check for existing versions first and
  create the next number.
- Keep a short `backup_doc.md` in the backup folder that lists what each archive
  contains.
- Exclude regenerable artifacts (`.venv`, `__pycache__`, caches, build outputs).
- Ask me before creating a backup larger than about 1 GB.

## 4. Reading, writing, and editing

### Writing and editing documents

- Before working with Office files, use the matching skill if installed
  (`docx`, `xlsx`, `pptx`, `pdf`). For citations and references, use
  `find-literature`.
- After drafting any substantial prose (paper sections, abstracts, reports,
  emails, documentation), run the `unslop` skill on the draft.
- Documentation (CLAUDE.md files, READMEs): keep it concise and describe the
  current state only. No notes on superseded versions, no narrative of completed
  work; version history belongs in a `## Changelog` section of the README.

### Editing files

- Edit surgically: make a targeted edit rather than rewriting a whole file,
  unless the file is short or most of it changes.
- Keep changes to what the task needs. Report a pre-existing bug or an unrelated
  problem as a follow-up in your summary instead of fixing it in the same change.
- Where a task is ambiguous, implement the reading its wording most directly
  supports and state that assumption.
- Scratch scripts and quick checks need not be kept.

### Formatting

- Line length: 88 characters for Python and Markdown files (code blocks and
  tables are exempt).

## 5. Python and tools

- Package manager: `uv`. Create environments with `uv sync`, run code with
  `uv run python`.
- [Notebook framework, e.g. Jupyter or marimo.]
- [Operating system and shell, e.g. Windows 11 with PowerShell, or macOS with
  zsh.]
- Use the dedicated Read, Edit, and Write tools for files; use the shell to run
  programs, not to rewrite files.

## 6. Subagents

If you are a subagent, do the task yourself and return the result; do not spawn
further subagents unless your orchestrator allows it.

## 7. Commits and pushes

Use the `commit-rules` skill before any commit or push. Never push without my
explicit go-ahead.

## 8. Feedback on skills and documentation

If a skill, script, or documentation file (CLAUDE.md, README) fails or proves
outdated during a session, report it at the end: name the file, describe what
failed, give the likely cause, and propose a fix. Do not edit it unprompted.

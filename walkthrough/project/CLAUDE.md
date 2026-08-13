# Swiss Rents: A Toy Research Project

## Research Question

How do average rents vary across Swiss cantons, and how robust is the
pattern to outlier cantons and to the period considered?

## Folder Layout

```text
project/
  CLAUDE.md        project memory, loaded at session start
  pyproject.toml   uv-managed Python environment
  data/            two rent datasets + README with sources and licenses
  papers/          five open-access papers + README with citations
  .claude/
    skills/        procedures the agent can invoke
    rules/         constraints that always apply
    agents/        subagent definitions for delegated tasks
```

Start the agent inside this folder so that `.claude/` loads correctly.
If you copied the folder out of the workshop repository first, you are
using it as intended.

## Working Conventions

Run Python through uv: `uv sync` once, then `uv run python <script>`.

Document every analysis script when you write or change it. The
`document-analysis` skill specifies what to record.

Cite the data source for every number, figure, or table. Sources and
licenses are listed in `data/README.md`; do not invent others.

Do not edit the files in `data/` by hand. Perform all cleaning in
scripts.

## Skills, Rules, and Agents

The project provides three skills, one rule, and two agents:

- `fetch-swiss-rents` (skill): downloads the two rent datasets from
  their public APIs, with local fallback.
- `document-analysis` (skill): documents any analysis script after you
  write or change it.
- `grill-me` (skill): interviews the user about their analysis plan,
  one question at a time, until the design holds.
- `reproducibility` (rule): requires that figures and tables be
  reproducible from scripts, with no manual data edits.
- `paper-reader` (agent): reads one paper from `papers/` and returns a
  structured summary.
- `skeptic-reviewer` (agent): reviews a finished analysis or summary
  adversarially and returns a verdict.

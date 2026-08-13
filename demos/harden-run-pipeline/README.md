# Demo: run-pipeline + harden-pipeline (workshop edition)

This demo shows a reproducibility workflow in two steps. The `/run-pipeline`
skill runs a project's producer notebooks to completion against the manifest
in `configs/manifest.yaml`, which declares the notebooks, their run order, and
the artifacts each one must write. The `/harden-pipeline` skill then acts as
an auditor: it regenerates the outputs, dispatches a subagent to hunt for
defects against the project's method specification in `docs/Blueprint.md`,
fixes any problems it finds at their root, and re-runs the quality gate until
the outputs pass. We use `sample_project/` as the demo target, a small
synthetic commune-rents pipeline that runs in seconds and needs no network
access.

## Two-line starter

The version you could run on your own project today, no skills required:

```text
Run the notebooks listed in configs/manifest.yaml in order until every declared
artifact is on disk; then audit the outputs against docs/Blueprint.md, fix any
defect at its root, and repeat until pytest, ruff, and mypy all pass.
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/) on the PATH. Without uv, the pip fallback in
  `sample_project/README.md` works too.
- Claude Code, started from the project copy's root.
- git (optional but recommended; the harden skill can then commit its fixes).

## Run the demo

Work on a copy of `sample_project/`, not on the clone, so experiments stay out
of the shared repository and the harden skill's commits do not land in it.

1. Copy the whole `sample_project/` folder to a location outside the cloned
   workshop repository.
2. Initialize the copy as its own repository, so the harden skill can commit
   the fixes it makes:

   ```bash
   cd path/to/your/copy
   git init
   git add .
   git commit -m "Initial state of the workshop sample project"
   ```

3. Install the workshop skills into the copy (see the next section).
4. Start Claude Code in the copy's root and run `/run-pipeline`, then
   `/harden-pipeline`.

When the demo finishes, `/run-pipeline` should report that both notebooks have
completed and all three declared artifacts are on disk, and
`/harden-pipeline` should report at least one hardening round that ends with
a passing quality gate (`pytest`, `ruff check`, `mypy`).

## Installing the skills

The two skills are project-level: copy the folders inside this demo's
`skills/` directory into the project copy's `.claude/skills/` folder, so that
these two files exist:

```text
your-copy/.claude/skills/run-pipeline/SKILL.md
your-copy/.claude/skills/harden-pipeline/SKILL.md
```

Restart Claude Code in the copy's root; `/run-pipeline` and `/harden-pipeline`
then appear as slash commands in that session.

## Cross-platform note

Run notebooks by their literal filenames (`notebooks/01_prepare.py`), never by
glob patterns such as `notebooks/01_*.py`: PowerShell does not expand globs in
arguments the way POSIX shells do. Environment-variable syntax also differs
between shells:

```powershell
$env:PYTHONUTF8 = "1"; uv run python notebooks/01_prepare.py
```

```bash
PYTHONUTF8=1 uv run python notebooks/01_prepare.py
```

The workshop editions of both skills already phrase their run commands this
way.

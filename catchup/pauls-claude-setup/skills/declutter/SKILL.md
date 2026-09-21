---
name: declutter
description: Declutter notebook or module — remove dead code, tangents, unneeded complexity.
disable-model-invocation: false
argument-hint: "<path> [--mode notebook|code]"
---

# Declutter

Remove what the analysis no longer needs: dead code, exploratory tangents,
redundant visualizations, over-engineering, debug residue. Three phases:
**analyze -> reconcile -> plan**. Nothing is removed or rewritten until the
user has approved a plan.

Unlike the built-in `/simplify` (which reviews only the current diff and
applies fixes automatically), this skill audits a whole artifact and waits for
approval before touching anything.

## Mode

- `--mode notebook` (default when the target is a `.py` under `notebooks/` or a
  `.ipynb`): operate at cell granularity.
- `--mode code` (default when the target is a `src/` module or package):
  operate at function/block granularity.

If the target is a project directory, list candidate targets with sizes and
one-line descriptions and ask which to declutter.

## Phase 1 -- Analyze

Read the target and its project context (`CLAUDE.md`, any README, and any
research-design or planning document the project keeps) to understand what
it *should* do versus what it *currently* does.
Extract the goals, hypotheses, and expected outputs (tables, figures,
datasets, public API).

In `--mode code`, gather tool evidence before building the audit table, using
vulture (unused code), `radon cc` (cyclomatic complexity), and jscpd
(copy-paste detection) on the target (skip silently if a tool is unavailable). Map the results onto the flags below:
vulture → `dead`, radon → `overengineered`, jscpd → `redundant` /
`src-duplicate`. Treat each as a lead, not a verdict; confirm against the
source before flagging.

Inventory each unit (notebook cell, or function/block in code mode):

- Index or name and first meaningful line.
- Purpose: data loading, transformation, analysis, visualization,
  documentation, utility, or public interface.
- Upstream dependencies consumed; downstream dependents produced.
- Link to a goal: which hypothesis, table, figure, or caller it serves. Mark
  units with no clear link as **unlinked**.

Flag each unit:

| Flag | Description |
|------|-------------|
| `dead` | Output unused; no downstream dependents |
| `tangent` | Exploratory work unlinked to the goal |
| `redundant-viz` | Near-duplicate of another visualization |
| `overengineered` | Replaceable by a simpler expression or an existing `src/` utility |
| `debug` | Print, shape check, or intermediate output from development |
| `src-duplicate` | Logic already in the project's `src/` package |
| `extractable` | Reusable logic that belongs in `src/` |

Present an audit table (unit; purpose; goal link; flag; note) and totals (N
units, M flagged, K unlinked). Do NOT propose changes yet.

## Phase 2 -- Reconcile

Walk through flagged units by category. For each candidate, state what would
be removed, merged, or rewritten; why (which goal it does not serve, or which
simpler alternative exists); and the risk (downstream breakage, loss of useful
exploration, reproducibility context). Use AskUserQuestion to confirm, amend,
or reject each. Typical questions: keep any `tangent` for an appendix? move
`extractable` logic into `src/` now or simplify it in place? retain any `debug`
unit as a sanity check? Do not proceed until the user responds.

## Phase 3 -- Plan

Enter plan mode and write a per-unit plan from the agreed changes. For each
unit to modify: the action (remove, merge, rewrite, extract to `src/`), the
rationale, and any dependency adjustment needed to keep the artifact runnable.
Order removals before rewrites; extraction to `src/` last. Include a validation
step.

## Notebook mode -- cell mechanics

Respect while decluttering:

- Marimo is a reactive DAG; trace dependencies via cell parameters and return
  tuples, not cell order. Cell returns are unique across the notebook (MB002);
  cell-local intermediates use `_`-prefixed names.
- All top-level imports live in the first cell with `import marimo as mo`.
- Validate with `uv run notebook.py` (exit 0) and `marimo check --fix <file>`.
- Jupyter legacy: sequential cell numbers instead of the DAG; validate via
  Restart & Run All.

## Code mode -- module mechanics

- Trace callers before removing a function; a public-API symbol re-exported
  from `__init__.py` is never "dead" without first checking external consumers.
- Prefer rehoming `extractable` / `src-duplicate` logic to the right module
  over deleting it; follow `rules/python-conventions.md`.
- Validate with `uv run python -m pytest`.

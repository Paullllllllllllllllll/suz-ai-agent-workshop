---
name: harden-pipeline
description: Harden the current analysis project's producer notebooks until all manifest-registered outputs are defect-free (iterative verification loop).
disable-model-invocation: true
argument-hint: "(run from the project root)"
---

# Production-Ready Notebook Hardening Loop

Operate on the analysis project in the current working directory (its root
holds `configs/manifest.yaml`, `notebooks/`, `src/`, and `data/`; the method
specification lives in `docs/Blueprint.md` at the project root). If the
working directory is not such a project root, stop and say so.

Harden the project until the datasets produced by EVERY notebook registered in
`configs/manifest.yaml` are defect-free at any scale. Target is PIPELINE
CORRECTNESS CONVERGENCE: a future full-scale run would produce defect-free
data.

This skill carries the procedure; run its loop until the end state holds.

> **Workshop demo scope:** in the live demo, run exactly ONE hardening round
> (steps 1-5 below once), then report. The full convergence loop — repeat
> until two consecutive clean rounds — is for real projects, not the room.

## Each round, in order, surfacing all results in the conversation

1. Read `configs/manifest.yaml` and `docs/Blueprint.md`; enumerate every
   producer notebook and its declared artifacts (grain, schema, consumers).
   Regenerate outputs by running notebooks in manifest DAG order, each by its
   literal filename:
   `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 uv run python notebooks/<file>.py`
   (PowerShell: set `$env:PYTHONUTF8 = "1"` first).
2. Launch ONE subagent for a broad production-readiness sweep over the whole
   dataset, anchored to Blueprint + manifest, NOT scoped to known fixes. In
   later rounds, also have it confirm that prior fixes hold and hunt NEW logic
   defects. Verify its findings for correctness before acting.
3. Fix real defects at root, simplest effective solution; do not overengineer.
4. Re-gate and report exit status: `uv run pytest -q`, `uv run ruff check .`,
   `uv run mypy .` (88-char limit). Add a regression test for every fix.
5. Optional — only if the project is a git repository: commit the round's
   fixes with a message naming the defect. State in the transcript whether
   this round found a new defect.

## Constraints that must hold

- Run the loop at a SMALL budget if a cost knob exists (LLM/API/sampling cap).
  Do NOT run the full-scale / unlimited-budget production pass. The goal is a
  state where running it would not produce defective data.
- IGNORE budget artifacts (few rows enriched, many skipped, sparse coverage);
  they are expected, not defects. Reason about full-scale behavior from the
  CODE, not the small-budget sample. FIX logic defects that corrupt output at
  ANY scale.
- Mutate only this project's own `data/` and the notebooks/src that produce
  it; never touch data sources outside the project.
- After two consecutive clean rounds and before finishing, launch ONE more
  broad subagent that, in addition to a fresh whole-dataset readiness sweep,
  actually performs a subset of the quantitative analyses outlined in the
  Blueprint against the regenerated data and reports whether results are
  coherent and defect-free. Treat any defect it finds as a new defect: fix it
  and resume the loop (the two-consecutive-clean count resets).

## Finishing

When the end state holds: run the quality gate once more (`uv run pytest -q`,
`uv run ruff check .`, `uv run mypy .`), summarize all rounds — defects found,
fixes applied, final gate status — and stop. Do NOT run the full-scale
production pass.

## Report format

Report each round as: "Round N -- gate: pytest <pass/fail>, ruff <clean/n>,
mypy <clean/n>; new defects: <list or none>; consecutive-clean count: <k>."

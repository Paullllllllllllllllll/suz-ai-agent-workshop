---
name: run-pipeline
description: Run the current analysis project's producer notebooks in order until every manifest-declared artifact is on disk.
disable-model-invocation: true
argument-hint: "(run from the project root)"
---

# Run Pipeline to Completion

Operate on the analysis project in the current working directory (its root
holds `configs/manifest.yaml`, `notebooks/`, `src/`, and `data/`). If the
working directory is not such a project root, stop and say so.

Assume the user has already pre-configured everything the run needs (API keys,
credentials, run settings, budget knobs). Do NOT change configuration. Your job
is to run the notebooks and get every dataset they produce onto disk.

## Starting position

1. Read `configs/manifest.yaml` to enumerate the producer notebooks, the order
   they must run in (DAG / numeric prefix), and the artifacts each one is
   expected to write.
2. List the notebooks in `notebooks/` and note their literal filenames.
   Confirm the run order and note, per notebook, the rough expected execution
   length (cheap/in-memory vs. long because of network or API calls). Use this
   to set monitoring cadence later.
3. Check which expected artifacts already exist on disk so you know the end
   state to converge on.

## Running

Run notebooks ONE AT A TIME, in order, each as a background process. Always
run by literal filename, never by glob pattern — glob expansion in arguments
is shell-dependent (PowerShell does not expand them). Environment-variable
syntax also differs by shell:

```bash
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 uv run python notebooks/01_prepare.py
```

```powershell
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
uv run python notebooks/01_prepare.py
```

For each notebook:

- Start it in the background and watch its output/logs.
- Poll progress at intervals matched to the notebook's expected length: short
  intervals for quick notebooks, long intervals (minutes) for ones dominated
  by network or API calls. Do not poll tighter than necessary.
- LONG RUNTIMES ARE EXPECTED and are NOT a failure. A notebook steadily making
  API calls is healthy even if it runs for a long time. Let it run.
- Advance to the next notebook only once the current one exits cleanly AND its
  manifest-declared artifacts are on disk.

## When to intervene

Intervene ONLY if a notebook is genuinely stuck or broken:

- STALL: no new output, no progress, and no active API/CPU work for a stretch
  well beyond its normal cadence.
- ERROR: it exits non-zero, raises, or writes a malformed/empty artifact.

When you intervene: diagnose the root cause, apply the simplest fix to the
notebook or the `src/` code it calls (do NOT touch user configuration), then
re-run that notebook and resume.

## Done

The pipeline is complete when every notebook has run to a clean exit and every
artifact declared in `configs/manifest.yaml` exists on disk. Report a short
per-notebook summary (status, runtime, artifacts written).

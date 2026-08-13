# Sample Project: Commune Rents

A small, fully synthetic data-analysis pipeline used as the live target for the
workshop demos. It reads a fictional dataset of Swiss communes, cleans it, and
produces a canton-level rent table and chart. All data are invented; no real
communes, no real rents, no network access anywhere in the code.

The project follows the manifest convention: `configs/manifest.yaml` lists the
producer notebooks in run order and the artifacts each one writes. The method
specification lives in `docs/Blueprint.md`.

## Get your own copy

The sample project ships inside the workshop repository. Work on a copy rather
than the clone, so your experiments stay out of the shared repository and you
avoid a nested-repo mess.

1. Copy the whole `sample_project` folder to a location outside the cloned
   workshop repository (for example, your usual projects directory).
2. Inside the copy, initialize a fresh repository:

   ```bash
   git init
   git add .
   git commit -m "Initial state of the workshop sample project"
   ```

## Run the pipeline

Both notebooks finish in seconds; there are no long-running or paid steps.

1. Install the environment:

   ```bash
   uv sync
   ```

   Expected output ends with an `Installed N packages` line and leaves a
   `.venv/` folder in the project root.

2. Run the prepare step:

   ```bash
   uv run python notebooks/01_prepare.py
   ```

   Expected output:

   ```text
   01_prepare: 121 raw rows -> 118 clean rows
   01_prepare: wrote ...\data\processed\communes_clean.csv
   ```

3. Run the analyze step:

   ```bash
   uv run python notebooks/02_analyze.py
   ```

   Expected output:

   ```text
   02_analyze: wrote ...\outputs\canton_rents.csv
   02_analyze: wrote ...\outputs\canton_rents.png
   ```

4. Run the quality gate:

   ```bash
   uv run pytest -q
   uv run ruff check .
   uv run mypy .
   ```

   Expected output: `8 passed`, `All checks passed!`, and
   `Success: no issues found`.

Without uv, use pip and a virtual environment instead:

```bash
python -m venv .venv && .venv\Scripts\activate   # macOS/Linux: source .venv/bin/activate
pip install -e . pytest ruff mypy
python notebooks/01_prepare.py && python notebooks/02_analyze.py
```

## Cross-platform note

The commands above work in Windows PowerShell and in macOS/Linux shells alike.
Run the notebooks by their literal filenames (`notebooks/01_prepare.py`), not
by glob patterns such as `notebooks/01_*.py`; PowerShell does not expand globs
in arguments the way POSIX shells do.

## Layout

```text
configs/manifest.yaml        notebooks in run order plus declared artifacts
data/raw/communes.csv        synthetic seed data (committed)
data/processed/              written by 01_prepare.py
notebooks/01_prepare.py      clean the raw data
notebooks/02_analyze.py      canton-level statistics and chart
outputs/                     written by 02_analyze.py
src/sample_project/          shared load/clean/aggregation functions
tests/                       pytest suite for the src functions
docs/Blueprint.md            purpose, data dictionary, method specification
```

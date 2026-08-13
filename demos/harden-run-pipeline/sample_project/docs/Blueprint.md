# Sample Project Blueprint

## Purpose

The project measures how average residential rents differ across cantons in a
synthetic population of Swiss communes. The raw file mimics a typical municipal
statistics extract: one row per commune, with population, average rent, and the
share of recently constructed buildings. The pipeline cleans the raw extract
and aggregates it to one summary row per canton; the canton table and its chart
are the deliverables that downstream consumers (slides, reports) rely on.

All values are invented. The dataset exists only to give the pipeline realistic
shape: a few large, expensive cities per canton alongside many small communes.

## Data dictionary

`data/raw/communes.csv`, one row per commune:

| Column               | Type  | Description                                       |
| -------------------- | ----- | ------------------------------------------------- |
| commune              | str   | Fictional commune name; may carry stray whitespace |
| canton               | str   | Two-letter canton code (ZH, BE, LU, SG, VD, TI)   |
| population           | int   | Residents; non-positive values are invalid        |
| average_rent_chf     | float | Average monthly rent in CHF; may be missing       |
| share_new_buildings  | float | Share of buildings built recently, in [0, 1]      |

`data/processed/communes_clean.csv` keeps the same columns after cleaning:
names stripped, rows without rent or with non-positive population dropped,
duplicate commune-canton pairs removed, shares clipped to [0, 1].

## Method specification

`outputs/canton_rents.csv` holds one row per canton with these definitions:

- `mean_rent_chf`: the canton-level average rent, computed as the
  population-weighted mean of commune rents. Each commune contributes in
  proportion to its residents; a city of 300,000 must move the canton average
  far more than a village of 800. An unweighted commune average is not an
  acceptable substitute, since it describes the typical commune rather than
  the rent faced by the typical resident.
- `median_rent_chf`: the unweighted median of commune rents, reported as a
  robustness companion that describes the typical commune.
- `population`: the sum of commune populations in the canton.
- `n_communes`: the number of communes entering the aggregation.

`outputs/canton_rents.png` charts `mean_rent_chf` per canton as a bar chart.

## Quality gate

`uv run pytest -q`, `uv run ruff check .`, and `uv run mypy .` must pass before
any change ships. Tests cover the shared functions in `src/sample_project/`.

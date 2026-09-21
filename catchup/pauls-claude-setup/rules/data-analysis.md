---
paths:
  - "**/notebooks/**"
  - "**/src/**"
  - "**/*.ipynb"
---

# Data Analysis Conventions

Methodology and library conventions for research projects. The globs above
are deliberately narrowed to `notebooks/` and `src/` folders and to Jupyter
notebooks, so these conventions never fire on `paper/` or `docs/` work.

## Preferred Stack

- Primary: `pandas`, `numpy`, `statsmodels`, `linearmodels`,
  `matplotlib`, `seaborn`, `pyreadstat`, `scipy`; `scikit-learn`
  only for non-econometric ML tasks.
- Supplementary where they improve the analysis: `pyfixest`
  (high-dimensional FE, event studies); `pandera` (DataFrame
  schema validation); `pydantic`/`instructor` (structured LLM
  outputs); `sentence-transformers`/`BERTopic` (NLP/embeddings);
  `plotnine` (grammar-of-graphics); `missingno` (missing-data
  diagnostics); `polars` (large-DataFrame performance). Not
  exhaustive; consult the user for substantially non-standard
  choices.

## DataFrame Conventions

- Explicit, descriptive column names in `snake_case`.
- Avoid `inplace=True` where reassignment is equally clear;
  prefer method chaining only when it improves readability.
- Never silently drop observations; log removed rows with a
  count and stated reason.
- Missing data: document handling decisions explicitly (listwise
  deletion, imputation, flagging). Do not assume NaN means zero.

## Diagnostics and Reproducibility

- Print intermediate diagnostics (shape, dtypes, value counts,
  summary statistics) at key transformation steps.
- Fixed random seeds wherever stochasticity is involved. Set
  seeds at the top of the script or notebook cell, not inline.
- Figures: always set figure size explicitly; label all axes with
  units; save at 300 DPI minimum for publication.

## Methodological Vigilance

Do not silently proceed past unexpected results or consequential
methodological decisions (distributional anomalies, unexpected
missingness, unverifiable identification assumptions, forks where
defensible approaches diverge). Pause, flag the issue, and
present options with trade-offs.

## Model Parsimony

Prefer the simplest specification that answers the question. Reach for a
plain OLS or a descriptive summary before an elaborate causal-inference
design; adopt heavier identification strategies (IV, DiD, event study,
matching) only when the question demands them, the data quality supports
them, and the user has asked for that level of rigor. When tempted toward a
complex design, flag the trade-off and confirm rather than building it
unprompted.

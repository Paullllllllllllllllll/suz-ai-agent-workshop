# Try-out: quantitative analysis, option B (historical panel)

A self-contained 60-90 minute task for the quant track (option B), for participants
who brought no material of their own. It runs the same way in Claude Code
(CLI) and the Claude Desktop app.

## Start here

Run `uv sync` in this folder, then paste:

```text
Read analysis.py and data/README.md. Run the script with uv run python
analysis.py, tell me what it estimates, and list everything about it
that would make you nervous if this were headed for a paper.
```

## Material

`analysis.py` is a realistic "quick look" script: it merges Allen's real
wages, Buringh's urban population, a Protestant dummy, and CLIO Infra
national indicators for ten European regions, 1500-1875, then regresses
log craftsmen wages on log urban population, the dummy, and log
population. It runs, and it is wrong in several places: a forward fill
that fabricates half the urban-population values, a merge that silently
drops rows, an interpolated regressor treated as observed, no standard
errors, no tests, and outputs written next to the code. `data/README.md`
documents the four datasets and names the traps.

## Task ladder

Work through the rungs in order. Rung 1 alone is a complete result.
Rung 3 feeds the closing block at 16:30.

### Rung 1: audit (about 20 minutes)

1. Have the agent run the script and explain what it estimates.
2. Ask for a numbered list of problems, each tied to a line number.
3. Check the list against `data/README.md`. Did it catch the forward
   fill and the row loss? Did it invent problems that are not there?

Done when `audit.md` exists with the agent's list and your own marks
for "confirmed", "wrong", and "missed".

### Rung 2: pipeline (about 30 minutes)

1. Ask the agent to turn the script into a small package with two
   steps: `prepare` (merge, writing `data/processed/panel.csv` and a
   log of rows in and out per file) and `analyze` (estimate with
   standard errors, writing `outputs/coefficients.csv`), plus one
   pytest test per step that checks row counts and column names.
2. Insist on a `README.md` stating how to rerun everything with one
   command and what each output file contains.
3. Delete `data/processed/` and `outputs/`, rerun, and confirm the
   numbers reproduce.

Done when one command regenerates every output and the tests pass.

### Rung 3: robustness (mandatory if reached, about 20-30 minutes)

1. Ask the agent to add a robustness table: the baseline, then the
   regression (a) using only periods with observed urban population,
   (b) using labourers instead of craftsmen, (c) restricted to
   1500-1800, and (d) with region fixed effects.
2. Have a subagent review the robustness code blind, with only the
   code and `data/README.md`, and report whether each variant does
   what its label says.
3. Write three to five lines in `verification.md`: which variant moved
   the coefficient most, what the blind review caught, and whether you
   would report this regression at all.

Done when `verification.md` exists and names one concrete finding for
16:30.

## Practical notes

Do not edit the files in `data/`; write derived data to
`data/processed/`. If the agent proposes statsmodels or linearmodels,
let it add the dependency with `uv add`, not by hand-editing.

## Attribution and availability

The files in `data/` are provided for the workshop day only and will be
removed from the repository afterwards; they are not public-domain
releases. Any output that uses them must credit the originals:

- Allen, Robert C. 2001. "The Great Divergence in European Wages and
  Prices from the Middle Ages to the First World War." *Explorations in
  Economic History* 38 (4): 411-447.
- Buringh, Eltjo, and Jan Luiten van Zanden. "European Urban Population,
  700-2000" (dataset, IISH Data Collection).
- CLIO Infra (clio-infra.eu), indicator files as named in
  `data/README.md`.
- Derived panels and religion coding: Paul Götz, Sociological Institute,
  University of Zurich, research data bank (unpublished working files).

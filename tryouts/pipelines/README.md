# Try-out: pipelines and automation

A self-contained 60-90 minute task for the pipelines track, for
participants who brought no material of their own. It runs the same way
in Claude Code (CLI) and the Claude Desktop app.

## Start here

Paste the following to begin:

```text
Look at the four files in inputs/ and tell me, before writing any code,
what it would take to combine them into one tidy country-by-year panel
for 1500-1860. List every mismatch in units, labels, and time grids.
```

## Material

Four small historical datasets from a working research data bank (see
`inputs/README.md` for columns and known traps): Allen's real-wage
panel by country and 25-year period, a regional urban-population panel
at 50-year benchmarks, and a religious classification by country and
20-year step, once as labels and once as a 0/1 dummy. They were built
at different times for different projects and do not agree on country
names, country codes, or years. That disagreement is the task.

## Task ladder

Work through the rungs in order. Rung 1 alone is a complete result.
Rung 3 feeds the closing block at 16:30.

### Rung 1: inventory (about 20 minutes)

1. Have the agent inspect every file and write `inventory.md`: for each
   file its unit of observation, time grid, country identifiers, and
   every value that looks suspicious.
2. Check three of its claims yourself against the raw files.

Done when `inventory.md` exists and you have marked one claim as wrong
or unverifiable, or confirmed all three.

### Rung 2: build (about 30 minutes)

1. Ask for a script `build_panel.py` that reads `inputs/`, harmonizes
   country codes to ISO-2 and years to the 50-year benchmark grid
   (the rule for the 20- and 25-year data goes in a docstring), and
   writes `outputs/panel.csv` plus `outputs/build_log.txt` listing rows
   read, matched, and dropped per file.
2. Require a `countries.csv` crosswalk file rather than a dictionary
   buried in code.
3. Have the agent add a check that fails loudly if any country loses
   more than a quarter of its rows in a merge.

Done when `python build_panel.py` regenerates the panel and the log
reports the drop counts.

### Rung 3: harden (mandatory if reached, about 20-30 minutes)

1. Ask for pytest tests covering the crosswalk, the year snapping, and
   the merge counts, then a `README.md` for the pipeline.
2. Hand `build_panel.py` and `inputs/README.md` to a subagent with no
   other context and ask it to find one way the script could silently
   produce wrong numbers.
3. Write three to five lines in `verification.md`: what the review
   found, whether you fixed it, and one thing you would still not trust.

Done when `verification.md` exists and names one concrete finding for
16:30.

## Practical notes

Treat `inputs/` as read-only. For the scraping flavor, add a fourth
rung: have the agent fetch the CLIO Infra urbanization table from
`clio-infra.eu` and reconcile it with `national_urb_ratio` in the urban
panel.

## Attribution and availability

The files in `inputs/` are provided for the workshop day only and will
be removed from the repository afterwards; they are not public-domain
releases. Any output that uses them must credit the originals:

- Allen, Robert C. 2001. "The Great Divergence in European Wages and
  Prices from the Middle Ages to the First World War." *Explorations in
  Economic History* 38 (4): 411-447.
- Buringh, Eltjo, and Jan Luiten van Zanden. "European Urban Population,
  700-2000" (dataset, IISH Data Collection).
- CLIO Infra (clio-infra.eu), Urbanization Ratio and Total Population
  indicators (Fink-Jensen 2015 and successors).
- Derived panels and religion coding: Paul Götz, Sociological Institute,
  University of Zurich, research data bank (unpublished working files).

# Inputs

Four small historical datasets, provided for the duration of the workshop
only. They are working files from Paul Goetz's research data bank, built
at different times for different projects, and derived from published
sources that must be cited in any output. See the attribution section
in `../README.md`; the files will be removed from the repository after
the workshop.

| File | Unit | Years | Content and source |
|---|---|---|---|
| `allen_wages_region_panel.csv` | country x 25-year period | 1500-1860 | Real wages (silver, deflated by a consumer basket) and welfare ratios for craftsmen and labourers, averaged over cities per country. Allen, R. C. (2001), *Explorations in Economic History* 38: 411-447. |
| `nuts2_urban_panel.csv` | NUTS-2 region x benchmark year | 1500-1900, 50-year steps | `urban_pop_10k` = population (thousands) in cities of 10,000+; `n_cities_10k`; `national_urb_ratio`; `total_pop_est_k` (rough proxy). Derived from Buringh & Van Zanden, "European urban population, 700-2000", and CLIO Infra national urbanization ratios and totals. |
| `religious_classification_1500_1860.csv` | country x 20-year step | 1500-1860 | Dominant confession coded Catholic / Protestant / Mixed for six countries. Project coding. |
| `protestant_dummy_1500_1860.csv` | country x 20-year step | 1500-1860 | The same coding as a 0/1 dummy (Mixed = 0). |

Known traps:

- Three different country labels: `England_Britain` / `ENG` in the wage
  file, ISO-2 codes (`UK`, `DE`, ...) in the urban panel, English names
  as column headers in the religion files.
- Three different time grids: 25-year periods, 50-year benchmarks,
  20-year steps.
- `total_pop_est_k` overestimates capital regions (Ile-de-France 1800 is
  about 4.4 million) because a very urban region is divided by a low
  national ratio. Prefer `urban_pop_10k`.
- The religion files cover six countries; the wage panel covers ten.
- `confidence` in the urban panel flags rows with no city of 10,000+.

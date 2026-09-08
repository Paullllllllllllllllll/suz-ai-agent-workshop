# Data

Four harmonized country-level panels for ten European regions (Austria,
Belgium, Britain, France, Germany, Italy, Netherlands, Portugal, Spain,
Switzerland) at 25-year periods, 1500-1875. They share the key columns
`region`, `region_abbrev`, `period`, `period_start`, `period_mid`, and
`stratum_abbrev`, so they merge without further work. They are derived
panels from Paul Goetz's research data bank (What's for Dinner? project);
cite the original sources, not this folder.

| File | Content | Original source |
|---|---|---|
| `allen_wages_region_panel.csv` | Real wages and welfare ratios of labourers (`lab_*`) and craftsmen (`craft_*`), city-level series averaged per region; `*_n_cities` gives the number of cities behind each mean. | Allen, R. C. (2001), "The Great Divergence in European Wages and Prices from the Middle Ages to the First World War", *Explorations in Economic History* 38: 411-447. |
| `buringh_urban_pop_panel.csv` | `total_urban_pop` (thousands) in cities of the Buringh roster, `n_cities`, `mean_city_pop`. | Buringh, E. and J. L. van Zanden, "European urban population, 700-2000" (dataset). |
| `religion_panel.csv` | `protestant_dummy`: 1 if the region counts as Protestant in that period, 0 otherwise. Coarse coding; Mixed cases are 0. | Project coding. |
| `clio_infra_panel.csv` | National indicators interpolated to the period grid: `urbanization_ratio_mean`, `total_population_mean`, `gdp_per_capita_mean`, `avg_years_education_mean`, `numeracy_mean`, and others. Each `*_mean` has a matching `*_obs` count of underlying yearly observations. | CLIO Infra (clio-infra.eu), various indicator files. |

Traps worth knowing before you trust any regression:

- Buringh's city roster is only observed at benchmark years, so
  `buringh_urban_pop_panel.csv` is empty in every second period.
- `total_population_mean` and `urbanization_ratio_mean` in the CLIO
  panel are interpolated; an `*_obs` of 0 means no underlying
  observation in that period.
- Allen's wage means rest on one or two cities for most regions. Check
  `craft_real_wage_n_cities` before treating a value as national.
- Britain's abbreviation is `EB`, not `GB` or `UK`.
- The Protestant dummy is 0 for "Mixed" regions such as Germany after
  1540, which lumps them with the Catholic south.

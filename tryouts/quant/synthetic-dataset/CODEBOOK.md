# Codebook — Synthetic Dataset
## "Origin, Education and Occupational Attainment"

> The specification this dataset was generated from. Section
> numbering follows the original, so §4 is still §4; the omitted
> sections were workshop facilitation notes, not documentation.

## 2. Scope, and what this data is not

Every number in this file is **invented for teaching.** The variables are named
after real constructs and the structure is sociologically plausible, but no
parameter here is an estimate of anything. Nothing in this dataset may be quoted,
cited, or reported as a finding about Switzerland, about migrants, about women, or
about anyone at all. It is a clean, shareable, freely-breakable object for
learning a workflow on — that is its whole purpose and its only claim.

Say this out loud. Synthetic data is honest *because* it is labelled, and the
moment it circulates unlabelled it becomes a liability rather than a safeguard.

**Design constraint from the poll (n = 12):** automating robustness checks was the
single strongest item, 10 of 12. This dataset is built so that robustness checks
have something to *find* — a dataset where every alternative specification returns
the same answer teaches nothing except false comfort.

---

## 3. Sample definition

| | |
|---|---|
| Unit of observation | Individual respondent |
| Design | Synthetic cross-sectional survey, single wave |
| Reference year | 2026 |
| n | **2,400** |
| Population frame | Residents aged 30–65 |
| Weights | None. Treat as a simple random sample. |
| File | `mobility_2026.csv`, UTF-8, comma-separated, `NA` for missing |

n = 2,400 is chosen deliberately: large enough that subgroup and interaction
models are estimable, small enough that the file generates in under a second
and opens instantly in anything.

---

## 4. Variable list

Levels are given in coding order. `NA` is the missing code throughout.

### Identifiers and demographics

| Name | Type | Values / range | Description |
|---|---|---|---|
| `id` | integer | 1 … 2400 | Respondent identifier, unique |
| `birth_year` | integer | 1961 … 1996 | Year of birth |
| `age` | integer | 30 … 65 | Derived: `2026 - birth_year` |
| `cohort` | factor | `older` (b. 1961–1975), `middle` (b. 1976–1985), `younger` (b. 1986–1996) | Derived from `birth_year` |
| `gender` | factor | `male`, `female`, `other` | Self-reported |
| `region` | factor | `de`, `fr`, `it` | Language region of residence |

### Social origin

| Name | Type | Values / range | Description |
|---|---|---|---|
| `migration_bg` | factor | `none`, `second_gen`, `first_gen` | Migration background |
| `parent_edu` | factor | `compulsory`, `upper_sec`, `tertiary` | Highest education of either parent |
| `parent_isei` | integer | 16 … 90 | Parental occupational status, ISEI-type scale, higher = higher status |
| `books_home_15` | ordinal | 1 … 5 | Books in the parental home at age 15: 1 = 0–10, 2 = 11–25, 3 = 26–100, 4 = 101–200, 5 = 200+ |
| `urban_origin` | binary | 0, 1 | Lived in an urban municipality at age 15 |

### Own attainment

| Name | Type | Values / range | Description |
|---|---|---|---|
| `edu` | factor | `compulsory`, `vet`, `matura_hv`, `tertiary` | Highest education attained. `vet` = vocational apprenticeship; `matura_hv` = matura or higher vocational |
| `edu_years` | numeric | 8.5 … 18.5 | Years of schooling implied by `edu`, with jitter. **An alternative operationalisation of the same construct** |
| `first_job_isei` | integer | 16 … 90 | Occupational status of first job after leaving education |
| `current_isei` | integer | 16 … 90 | **Primary outcome.** Occupational status of current job. `NA` if not employed |

### Household and labour supply

| Name | Type | Values / range | Description |
|---|---|---|---|
| `n_children` | integer | 0 … 4 | Number of own children in the household |
| `employed` | binary | 0, 1 | In paid employment at time of survey |
| `work_hours` | numeric | 4 … 60 | Usual weekly hours. `NA` if `employed == 0` |

**19 variables, 4 of them derived.** The derived ones (`age`, `cohort`,
`edu_years`, and the `NA` structure) are there on purpose: they give any
block something to reconstruct, and they let a participant check whether the agent
recomputed a variable correctly instead of trusting it.

---

## 5. Target marginal distributions

The generator must land close to these. They are what the validation step in §9
checks against.

| Variable | Target |
|---|---|
| `gender` | male .50, female .49, other .01 |
| `region` | de .70, fr .23, it .07 |
| `cohort` | older ≈ .42, middle ≈ .28, younger ≈ .30 (follows uniform `birth_year`) |
| `migration_bg` | none .62, second_gen .21, first_gen .17 |
| `parent_edu` | compulsory ≈ .28, upper_sec ≈ .48, tertiary ≈ .24 |
| `parent_isei` | mean ≈ 44, sd ≈ 16.4 |
| `edu` | compulsory ≈ .12, vet ≈ .42, matura_hv ≈ .22, tertiary ≈ .24 |
| `edu_years` | mean ≈ 13.5, sd ≈ 2.8 |
| `first_job_isei` | mean ≈ 44, sd ≈ 13 |
| `current_isei` | mean ≈ 47, sd ≈ 16.5 |
| `n_children` | mean ≈ 1.3 |
| `employed` | ≈ .93 |
| `work_hours` | mean ≈ 36.9, sd ≈ 9.5 |

**Measured, not derived** (run of 2026-08-17, seed 20260908). The morning's draft
guessed five of these and got four wrong — the ISEI standard deviations were all
too low and `work_hours` was three hours out. The categorical marginals above are
hit *exactly*, because the ordered variables are cut at empirical quantiles of
their latent index (see §6); that is a deliberate choice, and it means the
coefficients in §6 are left to do the only job that matters here — setting the
structure, not the margins.

The `work_hours` mean of ~37 deserves a sentence: it is low because
half the sample is women and Swiss women work part-time. That is not a bug in the
generator, it is the single most consequential fact in the dataset, and it is
what §8.2 turns on.

> **These are the illustrative margins.** If a real BFS marginal is easy to
> drop in for any of them, do it and cite it — this is the one place this
> document invents numbers it did not have to invent.

---

## 6. The generating process

Sampled **sequentially** in the order below; each step may use only variables
already drawn. `z()` is standardisation to mean 0, sd 1 over the generated sample.
`N(m, s)` is normal with that mean and standard deviation.

**6.1 `birth_year`** ~ Uniform integer on [1961, 1996]. Derive `age` and `cohort`.

**6.2 `gender`** ~ Categorical(male .50, female .49, other .01), independent of everything.

**6.3 `region`** ~ Categorical(de .70, fr .23, it .07), independent of everything.

**6.4 `migration_bg`** ~ Categorical(none .62, second_gen .21, first_gen .17), independent of everything.

**6.5 Latent origin `O`** — not written to the file.

```
O = N(0, 1) + (-0.35 if first_gen else -0.15 if second_gen else 0)
```

**6.6 `parent_edu`** — ordered probit on

```
eta = 0.95*O + 0.30*(cohort == younger) - 0.25*(cohort == older)
```

with thresholds chosen to hit the §5 marginals (≈ -0.55 and ≈ 0.72 on the
standardised `eta`). The cohort term is educational expansion: younger
respondents' parents were themselves better educated.

**6.7 `parent_isei`**

```
parent_isei = 42 + 11*O + 6*(parent_edu == tertiary) + N(0, 11)
```

clipped to [16, 90] and rounded.

**6.8 `books_home_15`** — ordered on `0.60*O + 0.30*z(parent_isei) + N(0, 1)`,
cut into 5 categories at the quintiles of that index shifted to give a
right-skewed distribution (targets ≈ .18 / .24 / .28 / .18 / .12).

**6.9 `urban_origin`** ~ Bernoulli(logit⁻¹(`-0.25 + 0.35*O + 0.20*(region == de)`)).

**6.10 `edu`** — ordered probit on

```
eta = 0.42*z(parent_edu_numeric)
    + 0.30*z(parent_isei_true)          # the TRUE value, before §7 missingness
    + 0.22*z(books_home_15)
    + 0.18*urban_origin
    + 0.15*(cohort == middle) + 0.45*(cohort == younger)     # expansion
    + 0.12*(gender == female)
    + 0.28*(gender == female)*(cohort == younger)            # reversal of the gap
    - 0.20*(migration_bg == first_gen)
    + N(0, 1)
```

thresholds set to the §5 marginals. **Note the two female terms.** In the younger
cohort women are the better-educated group; this is deliberate and it is what
makes §8's headline non-trivial.

**6.11 `edu_years`** — deterministic map plus jitter:

```
compulsory 9.0 | vet 12.0 | matura_hv 14.5 | tertiary 17.5
edu_years = base + Uniform(-1.0, +1.0)
```

**6.12 `n_children`** ~ Poisson(λ), capped at 4, with
λ = 1.6 (older), 1.4 (middle), 0.8 (younger).

**6.13 `first_job_isei`**

```
first_job_isei = 12 + 1.9*edu_years + 0.14*parent_isei_true + 2.2*O + N(0, 10)
```

clipped to [16, 90] and rounded.

**6.14 `employed`** ~ Bernoulli(logit⁻¹(
`2.8 - 0.35*(gender == female)*n_children - 0.50*(edu == compulsory)`)).

**6.15 `work_hours`** — for the employed only; `NA` otherwise.

```
work_hours = 42.5
           - 3.5*(gender == female)
           - 6.0*(gender == female)*n_children
           - 0.9*(gender == male)*n_children
           + 1.2*(edu == tertiary)
           + N(0, 6.5)
```

clipped to [4, 60]. Implied: men ≈ 41 hours, women ≈ 31, women with two children
≈ 27. **These are large and they are not exaggerated** — Swiss women's average
weekly hours really do sit near 30 because part-time is the norm. The morning's
draft used timid values (−1.0 and −4.5) and the result was that §8.2's bad
control moved almost nothing. Realism and pedagogy pulled the same direction
here, which does not always happen.

**6.16 `current_isei`** — the outcome. For the employed only; `NA` otherwise.

```
current_isei = 0.55*first_job_isei
             + 1.60*edu_years
             + 0.10*parent_isei_true
             + 0.17*(age - 45)
             + GENDER_TERM
             + 0.30*(work_hours - 40)
             - 3.5*(migration_bg == first_gen)
             + N(0, 11)
```

where

```
GENDER_TERM (for gender == female, else 0):
    cohort == older    ->  -5.0
    cohort == middle   ->  -3.0
    cohort == younger  ->  +1.5
GENDER_TERM (for gender == other): -3.5, all cohorts
```

clipped to [16, 90] and rounded.

**These are DIRECT effects, net of the pathway through `work_hours`.** The gap a
sociologist actually reports is the **total** — direct plus hours — and the two
differ by roughly 3.5 points, because §6.15's hours gap is large. Do not confuse
the two when reading §8: the numbers in §8.1 are totals.

**Note the younger cohort's direct effect is positive.** Net of hours and
education, young women hold slightly higher-status jobs; their *total* gap is
nonetheless near zero, because the hours pathway cancels it. That is not a fudge
to make the demo work — it is what makes §8.1 and §8.2 interlock instead of
compete, and it licenses the strongest available reading: **the
youngest cohort's apparent gap is a working-hours composition effect and nothing
else.**

**This block is the whole design.** Everything in §8 falls out of it.

---

## 7. Missingness — deliberately not uniform

Applied **after** all variables are generated, so the true values exist and the
generator can optionally write a `_truth.csv` alongside the public file.

| Variable | Mechanism | Rate | Rule |
|---|---|---|---|
| `parent_isei` | **MAR** | ≈ 17% | P(missing) = logit⁻¹(`-2.4 + 1.6*first_gen + 0.9*second_gen - 0.45*(books_home_15 - 3)`) |
| `books_home_15` | **MCAR** | ≈ 3% | uniform |
| `work_hours` | structural | ≈ 7% | `NA` iff `employed == 0` |
| `current_isei` | structural | ≈ 7% | `NA` iff `employed == 0` |

**The MAR rule was wrong in the morning's draft and the error is worth keeping in
view.** It made `P(missing parent_isei)` depend on `parent_isei`'s own value —
which is **MNAR, not MAR.** The distinction is not pedantry: multiple imputation
is justified under MAR and not under MNAR, so a block built on the old rule would
have demonstrated imputation "working" on a mechanism where it has no licence to.
The rule now depends only on `migration_bg` and `books_home_15`, both fully
observed. Because books correlates with parental status at about .54, the rows
that go missing are still disproportionately low-origin — the bite survives, and
the imputation story is now actually true.

Observed rates: 17.3% overall, and by group **35% of first-generation
respondents, 24% second-generation, 10% with no migration background.** That is
a strong mechanism on purpose; a 5% one is invisible in a two-hour block.

Three mechanisms in one file, labelled, is the cheapest possible teaching of a
distinction that usually costs a whole session — and one of them is a live
example of getting the label wrong, which is worth admitting.

---

## 8. What is planted in this data

> This section documents the structure that was deliberately built into the
> data. Synthetic data only has structure if you put it there on purpose, and
> writing down which structure — and why — is what separates a dataset you can
> argue with from a pile of plausible rows.

### 8.1 The headline, and why it is a trap

Fit the obvious model:

```
current_isei ~ female + edu_years + parent_isei
```

`female` comes back at **−5.21, t = −8.9.** The natural sentence is "a persistent
occupational status penalty for women." **That is where most analyses would
stop.**

Now fit it by cohort (separately, so every standard error is honest):

| cohort | n | coef | se | t |
|---|---|---|---|---|
| older | 731 | **−8.46** | 0.91 | −9.3 |
| middle | 533 | **−5.61** | 1.09 | −5.2 |
| younger | 572 | **−0.66** | 1.05 | **−0.6** |

The single number splits, and the story is no longer a penalty; it is a gap that
has closed. **The pooled coefficient describes nobody in the sample** — it is
1.6× too small for the oldest cohort and eight times too large for the youngest.

**The punchline is the last row.** The pooled model reports a penalty at t = −8.9,
and for the youngest third of the sample **you cannot reject zero.** Verified
across eight seeds: `|t| < 1.96` for the younger cohort in **8 of 8**, with the
younger gap ranging −1.88 to +0.69 while the older gap never leaves −6.5 to −9.3.
The claim is robust, not a seed artefact.

This is the reason this theme was chosen over the alternatives: everyone in that
room knows what a status-attainment model looks like, so a robustness check that
*moves the story* lands instead of washing over them.

### 8.2 The bad control

| model | female coef | se | t |
|---|---|---|---|
| baseline | −5.21 | 0.58 | −8.9 |
| + `work_hours` | **−2.49** | 0.69 | −3.6 |
| + `first_job_isei` | −2.61 | 0.60 | −4.3 |

Adding `work_hours` cuts the gap by **52%** (mean 57% across eight seeds, never
below 43%). It looks like an explanation. It is not: in §6.15 hours are a
*consequence* of gender and children, so conditioning on them removes part of the
very effect being estimated. A participant who reports the smaller number as "the
gap, adjusted for hours worked" has controlled away their own finding. The same
trap sits one step further out in `first_job_isei`, which is a mediator of
education.

**This interlocks with §8.1 and the pairing is the best thing in the dataset.**
The variable that halves the pooled gap is the same variable that accounts for
the entire younger-cohort gap. Both facts are true; they support opposite
sentences; and which one you say depends on whether you wanted the total effect
or the direct one — a question no software will ask you.

### 8.3 The missingness bite — in the sample, before the slope

The planted `first_gen` effect is **−3.5** (§6.16). What complete-case analysis
does to it is *not* the lesson, and the morning's draft was wrong to promise it
was: the coefficient moves from −2.62 to −2.42, comfortably inside its own
standard error of 0.87. **Do not claim a coefficient shift this data will not
reliably deliver.**

What always holds, and is the better lesson, is **composition**:

| | full | complete case | shift |
|---|---|---|---|
| n | 2400 | 1836 | **−23.5%** |
| `first_gen` share | .176 | .136 | −.040 |
| mean `books_home_15` | 2.83 | 2.96 | +0.13 |
| mean *true* `parent_isei` | 42.8 | 44.1 | **+1.36** |

Listwise deletion throws away **a quarter of the sample, non-randomly**, and what
comes back is a richer, better-educated, less migrant population than the one that
was sampled. Every descriptive statistic reported from the complete cases is a
true statement about a population nobody chose to study. **The bias shows up in
description long before it shows up in a slope** — which is precisely why it
survives peer review.

Two defensible pipelines, two samples, and only one of them is the one in the
methods section.

### 8.4 Cultural capital versus structure

`books_home_15` is strongly associated with `edu` on its own and loses much of
that association once `parent_edu` and `parent_isei` enter — predicting
`edu_years`, the books coefficient falls from **0.90 to 0.34, a 62% drop** —
because in §6.8 the books variable is itself generated from origin. Whether it is
"cultural capital" or "a proxy for parental status" is exactly the argument the
room will have, and here the answer is in §6.

### 8.5 Age, period, cohort — deliberately not identified

`age` and `cohort` are two functions of the same `birth_year` in a single
cross-section, so the maturation term in §6.16 and the cohort-varying gender term
cannot be separated by any model fitted to this file. This is a genuine feature,
not an oversight. If someone spots it during 3c, that is the best possible
outcome of the afternoon.

### 8.6 Operationalisation

`edu` and `edu_years` encode the same construct categorically and continuously.
Swapping one for the other is the cheapest robustness check available and a good
first thing to hand an agent.

### 8.7 Selection, for the advanced

`current_isei` is observed only for the employed, and §6.14 makes employment
depend on gender and children. The analytic sample is therefore selected on
something correlated with the outcome. Not a required exercise; a good answer if
someone asks why the gap looks different when they subset.

---

## 9. Validation the generator must pass

The live block does not end when the file appears. It ends when the generator
**checks its own output** — which mirrors the audit move participants run in Part
3c and echoes the harden-pipeline arc from Part 3a.

The generator writes a `validate` step reporting:

1. **Structural** — n = 2400; `id` unique; no value outside the ranges in §4; no
   unexpected `NA`; `age == 2026 - birth_year` for every row; `cohort` consistent
   with `birth_year`; `work_hours`/`current_isei` `NA` exactly where `employed == 0`.
2. **Marginals** — every entry in §5, printed next to its target.
3. **Structure** — the correlation matrix of
   (`parent_isei`, `books_home_15`, `edu_years`, `first_job_isei`, `current_isei`),
   all of which must be positive and ordered as expected. **This is also the
   artefact to hold up against the lower rungs' correlation matrices** — same
   five variables, one stable across seeds and one not. (`rung2_grounded.py`
   gives the grounded-margins comparison: largest off-diagonal 0.051 against
   0.663 here.)
4. **Recovery** — refit §8.1 by cohort. **This is the real test**, and it is
   stated as three *qualitative* conditions rather than three point values,
   because the point values move by ±1.5 across seeds while the conditions do
   not:
   - the gaps are **ordered** `older < middle < younger`;
   - the **older** coefficient is below −5 and significant;
   - the **younger** coefficient has `|t| < 1.96` — it is not distinguishable
     from zero.

   Verified across eight seeds: ordering held every time, younger `|t| < 1.96`
   in **8 of 8**. Note these are **total** effects and therefore sit about 3.5
   points below §6.16's direct coefficients; that gap is §8.2 made numerical and
   is not an error.

   This one is printed only with `--reveal`, since it restates §8 directly.
5. **Missingness** — the three rates in §7, and a check that `parent_isei`
   missingness is higher among `first_gen` than `none`.

If check 4 fails, the dataset is wrong no matter how good the marginals look.

**Reproducibility:** a fixed seed, written into the generator and printed in its
output. Same codebook, same seed, same file on any machine. A dataset asked
for directly in a prompt cannot make that promise at all.

---

## 10. Machine-readable spec

> Restates §6–§7. **If it disagrees with the prose, the prose is right.**
> This is the block the agent is pointed at when it writes the generator.

```yaml
dataset:
  name: mobility_2026
  n: 2400
  seed: 20260908
  reference_year: 2026
  output: mobility_2026.csv
  truth_output: mobility_2026_truth.csv   # the same rows pre-missingness

draw_order:
  - birth_year:   {dist: uniform_int, min: 1961, max: 1996}
  - age:          {derived: "2026 - birth_year"}
  - cohort:       {derived_bins: {older: [1961, 1975], middle: [1976, 1985], younger: [1986, 1996]}, on: birth_year}
  - gender:       {dist: categorical, levels: {male: 0.50, female: 0.49, other: 0.01}}
  - region:       {dist: categorical, levels: {de: 0.70, fr: 0.23, it: 0.07}}
  - migration_bg: {dist: categorical, levels: {none: 0.62, second_gen: 0.21, first_gen: 0.17}}

  - O:
      latent: true
      dist: normal
      mean: "0 - 0.35*(migration_bg=='first_gen') - 0.15*(migration_bg=='second_gen')"
      sd: 1

  - parent_edu:
      dist: ordered_probit
      eta: "0.95*O + 0.30*(cohort=='younger') - 0.25*(cohort=='older')"
      levels: [compulsory, upper_sec, tertiary]
      target_marginals: [0.28, 0.48, 0.24]

  - parent_isei:
      formula: "42 + 11*O + 6*(parent_edu=='tertiary') + normal(0, 11)"
      clip: [16, 90]
      round: 0

  - books_home_15:
      dist: ordered
      index: "0.60*O + 0.30*z(parent_isei) + normal(0, 1)"
      levels: [1, 2, 3, 4, 5]
      target_marginals: [0.18, 0.24, 0.28, 0.18, 0.12]

  - urban_origin:
      dist: bernoulli
      logit: "-0.25 + 0.35*O + 0.20*(region=='de')"

  - edu:
      dist: ordered_probit
      eta: >
        0.42*z(parent_edu_numeric) + 0.30*z(parent_isei_true)
        + 0.22*z(books_home_15) + 0.18*urban_origin
        + 0.15*(cohort=='middle') + 0.45*(cohort=='younger')
        + 0.12*(gender=='female')
        + 0.28*((gender=='female') & (cohort=='younger'))
        - 0.20*(migration_bg=='first_gen')
        + normal(0, 1)
      levels: [compulsory, vet, matura_hv, tertiary]
      target_marginals: [0.12, 0.42, 0.22, 0.24]

  - edu_years:
      map: {compulsory: 9.0, vet: 12.0, matura_hv: 14.5, tertiary: 17.5}
      on: edu
      jitter: {dist: uniform, min: -1.0, max: 1.0}

  - n_children:
      dist: poisson
      lambda_by: {cohort: {older: 1.6, middle: 1.4, younger: 0.8}}
      cap: 4

  - first_job_isei:
      formula: "12 + 1.9*edu_years + 0.14*parent_isei_true + 2.2*O + normal(0, 10)"
      clip: [16, 90]
      round: 0

  - employed:
      dist: bernoulli
      logit: "2.8 - 0.35*(gender=='female')*n_children - 0.50*(edu=='compulsory')"

  - work_hours:
      only_if: "employed == 1"
      formula: >
        42.5 - 3.5*(gender=='female') - 6.0*(gender=='female')*n_children
        - 0.9*(gender=='male')*n_children + 1.2*(edu=='tertiary') + normal(0, 6.5)
      clip: [4, 60]
      else: NA

  - current_isei:
      only_if: "employed == 1"
      formula: >
        0.55*first_job_isei + 1.60*edu_years + 0.10*parent_isei_true
        + 0.17*(age - 45) + gender_term
        + 0.30*(work_hours - 40)
        - 3.5*(migration_bg=='first_gen') + normal(0, 11)
      # DIRECT effects, net of the work_hours pathway. Totals sit ~3.5 lower.
      gender_term:
        female: {older: -5.0, middle: -3.0, younger: 1.5}
        other:  {older: -3.5, middle: -3.5, younger: -3.5}
        male:   {older: 0, middle: 0, younger: 0}
      clip: [16, 90]
      round: 0
      else: NA

missingness:
  parent_isei:
    # MAR proper: depends only on OBSERVED variables. An earlier draft made this
    # depend on parent_isei itself, which is MNAR and would have made the
    # imputation lesson false. See section 7.
    mechanism: MAR
    logit: "-2.4 + 1.6*(migration_bg=='first_gen') + 0.9*(migration_bg=='second_gen') - 0.45*(books_home_15 - 3)"
    expected_rate: 0.17
  books_home_15:
    mechanism: MCAR
    rate: 0.03
  work_hours:    {mechanism: structural, rule: "employed == 0"}
  current_isei:  {mechanism: structural, rule: "employed == 0"}

validation:
  structural: [n, unique_id, ranges, derived_consistency, na_pattern]
  marginals: see_section_5
  correlations_positive: [parent_isei, books_home_15, edu_years, first_job_isei, current_isei]
  recovery:
    model: "current_isei ~ female + edu_years + parent_isei, fitted per cohort"
    # Qualitative, not point values: the points move ~1.5 across seeds, these do not.
    expect_ordering: "older < middle < younger"
    expect_older_below: -5.0
    expect_younger_abs_t_below: 1.96
    print_to: log_only        # restates §8; shown only with --reveal
  missingness_rates: {parent_isei: 0.17, books_home_15: 0.03, structural: 0.07}
  stability:
    seeds: 8
    must_hold: [ordering, younger_not_significant, bad_control_shrink_above_0.4]
```

---

"""
Synthetic dataset generator — "Origin, Education and Occupational Attainment"

Runs FROM the codebook (Codebook_Synthetic_Mobility_v2.md), not from any real
data. Every parameter below is a transcription of codebook section 6 and 7.
If this script and the codebook disagree, the codebook is right.

SUZ AI Agent Workshop, Part 3b.

Usage
-----
    python generate_mobility.py                     # generate + validate
    python generate_mobility.py --n 500 --seed 7    # your own draw
    python generate_mobility.py --no-validate       # just the file
    python generate_mobility.py --reveal            # print the recovery check

Dependencies: numpy, pandas. Nothing else, on purpose — this has to run on a
participant's laptop without an install session.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Codebook constants (section 6). Change these and the world changes with them.
# --------------------------------------------------------------------------

REFERENCE_YEAR = 2026
BIRTH_MIN, BIRTH_MAX = 1961, 1996

COHORT_BINS = {"older": (1961, 1975), "middle": (1976, 1985), "younger": (1986, 1996)}

GENDER_P = {"male": 0.50, "female": 0.49, "other": 0.01}
REGION_P = {"de": 0.70, "fr": 0.23, "it": 0.07}
MIGRATION_P = {"none": 0.62, "second_gen": 0.21, "first_gen": 0.17}

PARENT_EDU_LEVELS = ["compulsory", "upper_sec", "tertiary"]
PARENT_EDU_TARGET = [0.28, 0.48, 0.24]

BOOKS_LEVELS = [1, 2, 3, 4, 5]
BOOKS_TARGET = [0.18, 0.24, 0.28, 0.18, 0.12]

EDU_LEVELS = ["compulsory", "vet", "matura_hv", "tertiary"]
EDU_TARGET = [0.12, 0.42, 0.22, 0.24]
EDU_YEARS_MAP = {"compulsory": 9.0, "vet": 12.0, "matura_hv": 14.5, "tertiary": 17.5}

CHILDREN_LAMBDA = {"older": 1.6, "middle": 1.4, "younger": 0.8}
CHILDREN_CAP = 4

# Section 6.16 — the planted structure. This is the thing the validation
# recovery check exists to find. See codebook section 8.1.
# These are DIRECT effects, net of the pathway through work_hours. The gap a
# sociologist actually reports is the TOTAL — direct plus hours — and the two
# differ by about 3.5 points because Swiss women's hours are what they are.
# Note the younger cohort's direct effect is POSITIVE: net of hours and
# education, young women hold slightly higher-status jobs. Their observed
# total gap is therefore near zero and statistically indistinguishable from
# it, which is the whole point of 8.1 — and the reason it is worth saying that
# the youngest cohort's raw gap is a working-hours composition effect and
# nothing else.
GENDER_TERM = {
    "female": {"older": -5.0, "middle": -3.0, "younger": 1.5},
    "other": {"older": -3.5, "middle": -3.5, "younger": -3.5},
    "male": {"older": 0.0, "middle": 0.0, "younger": 0.0},
}

ISEI_MIN, ISEI_MAX = 16, 90


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def z(x: np.ndarray) -> np.ndarray:
    """Standardise to mean 0, sd 1 over the generated sample."""
    x = np.asarray(x, dtype=float)
    sd = x.std()
    return (x - x.mean()) / sd if sd > 0 else np.zeros_like(x)


def inv_logit(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def ordered_cut(index: np.ndarray, target_probs, labels):
    """Cut a latent index into ordered categories hitting `target_probs` exactly.

    The codebook describes an ordered probit with thresholds "chosen to hit the
    marginals". Cutting at the empirical quantiles of the index does exactly
    that, and does it exactly rather than in expectation — which is what you
    want for a teaching dataset, because the marginals then stop being a source
    of run-to-run noise and the coefficients in `index` are left to do the only
    job that matters here: setting the structure.
    """
    cuts = np.cumsum(target_probs)[:-1]
    thresholds = np.quantile(index, cuts)
    codes = np.searchsorted(thresholds, index, side="right")
    return np.asarray(labels, dtype=object)[codes]


def clip_round(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return np.clip(np.round(x), lo, hi).astype(int)


def draw_categorical(rng, probs: dict, n: int) -> np.ndarray:
    keys = list(probs)
    return rng.choice(keys, size=n, p=[probs[k] for k in keys])


def ols(y: np.ndarray, X: np.ndarray, names: list[str]) -> pd.DataFrame:
    """Least squares with standard errors. numpy only — no statsmodels needed."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    sigma2 = resid @ resid / dof
    xtx_inv = np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(sigma2 * xtx_inv))
    return pd.DataFrame({"coef": beta, "se": se, "t": beta / se}, index=names)


# --------------------------------------------------------------------------
# The generating process — codebook section 6, in order
# --------------------------------------------------------------------------


def generate(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    d = pd.DataFrame({"id": np.arange(1, n + 1)})

    # 6.1 birth_year, and the two variables derived from it
    d["birth_year"] = rng.integers(BIRTH_MIN, BIRTH_MAX + 1, size=n)
    d["age"] = REFERENCE_YEAR - d["birth_year"]
    d["cohort"] = pd.cut(
        d["birth_year"],
        bins=[1960, 1975, 1985, 1996],
        labels=["older", "middle", "younger"],
    ).astype(str)

    # 6.2 - 6.4 independent demographics
    d["gender"] = draw_categorical(rng, GENDER_P, n)
    d["region"] = draw_categorical(rng, REGION_P, n)
    d["migration_bg"] = draw_categorical(rng, MIGRATION_P, n)

    first_gen = (d["migration_bg"] == "first_gen").to_numpy()
    second_gen = (d["migration_bg"] == "second_gen").to_numpy()
    female = (d["gender"] == "female").to_numpy()
    male = (d["gender"] == "male").to_numpy()
    older = (d["cohort"] == "older").to_numpy()
    middle = (d["cohort"] == "middle").to_numpy()
    younger = (d["cohort"] == "younger").to_numpy()

    # 6.5 latent origin — never written to the public file
    O = rng.normal(0, 1, n) - 0.35 * first_gen - 0.15 * second_gen

    # 6.6 parent_edu
    eta_pe = 0.95 * O + 0.30 * younger - 0.25 * older
    d["parent_edu"] = ordered_cut(eta_pe, PARENT_EDU_TARGET, PARENT_EDU_LEVELS)
    parent_edu_num = pd.Series(d["parent_edu"]).map(
        {lvl: i for i, lvl in enumerate(PARENT_EDU_LEVELS)}
    ).to_numpy(dtype=float)

    # 6.7 parent_isei — the TRUE value; missingness comes later
    parent_isei_true = clip_round(
        42 + 11 * O + 6 * (parent_edu_num == 2) + rng.normal(0, 11, n),
        ISEI_MIN,
        ISEI_MAX,
    )
    d["parent_isei"] = parent_isei_true

    # 6.8 books_home_15
    books_index = 0.60 * O + 0.30 * z(parent_isei_true) + rng.normal(0, 1, n)
    d["books_home_15"] = ordered_cut(books_index, BOOKS_TARGET, BOOKS_LEVELS).astype(int)

    # 6.9 urban_origin
    p_urban = inv_logit(-0.25 + 0.35 * O + 0.20 * (d["region"] == "de").to_numpy())
    d["urban_origin"] = (rng.random(n) < p_urban).astype(int)

    # 6.10 edu — note the two female terms
    eta_edu = (
        0.42 * z(parent_edu_num)
        + 0.30 * z(parent_isei_true)
        + 0.22 * z(d["books_home_15"].to_numpy())
        + 0.18 * d["urban_origin"].to_numpy()
        + 0.15 * middle
        + 0.45 * younger
        + 0.12 * female
        + 0.28 * (female & younger)
        - 0.20 * first_gen
        + rng.normal(0, 1, n)
    )
    d["edu"] = ordered_cut(eta_edu, EDU_TARGET, EDU_LEVELS)

    # 6.11 edu_years — the same construct, continuously
    d["edu_years"] = (
        pd.Series(d["edu"]).map(EDU_YEARS_MAP).to_numpy() + rng.uniform(-1.0, 1.0, n)
    ).round(2)

    # 6.12 n_children
    lam = pd.Series(d["cohort"]).map(CHILDREN_LAMBDA).to_numpy()
    d["n_children"] = np.minimum(rng.poisson(lam), CHILDREN_CAP)

    # 6.13 first_job_isei
    d["first_job_isei"] = clip_round(
        12
        + 1.9 * d["edu_years"].to_numpy()
        + 0.14 * parent_isei_true
        + 2.2 * O
        + rng.normal(0, 10, n),
        ISEI_MIN,
        ISEI_MAX,
    )

    # 6.14 employed
    p_emp = inv_logit(
        2.8
        - 0.35 * female * d["n_children"].to_numpy()
        - 0.50 * (d["edu"] == "compulsory").to_numpy()
    )
    d["employed"] = (rng.random(n) < p_emp).astype(int)
    emp = d["employed"].to_numpy() == 1

    # 6.15 work_hours — employed only.
    # The female terms are large on purpose and they are not exaggerated:
    # Swiss women's average weekly hours really do sit near 30 because part-time
    # is the norm, especially with children. This is also what gives 8.2 its
    # bite — a bad control is only instructive if controlling actually moves
    # something.
    hours = (
        42.5
        - 3.5 * female
        - 6.0 * female * d["n_children"].to_numpy()
        - 0.9 * male * d["n_children"].to_numpy()
        + 1.2 * (d["edu"] == "tertiary").to_numpy()
        + rng.normal(0, 6.5, n)
    )
    hours = np.clip(hours, 4, 60).round(1)
    d["work_hours"] = np.where(emp, hours, np.nan)

    # 6.16 current_isei — the outcome, employed only
    gterm = np.array(
        [GENDER_TERM[g][c] for g, c in zip(d["gender"], d["cohort"])], dtype=float
    )
    isei = (
        0.55 * d["first_job_isei"].to_numpy()
        + 1.60 * d["edu_years"].to_numpy()
        + 0.10 * parent_isei_true
        + 0.17 * (d["age"].to_numpy() - 45)
        + gterm
        + 0.30 * (hours - 40)
        - 3.5 * first_gen
        + rng.normal(0, 11, n)
    )
    isei = np.clip(np.round(isei), ISEI_MIN, ISEI_MAX)
    d["current_isei"] = np.where(emp, isei, np.nan)

    # Kept for the truth file only
    d["_O"] = O
    d["_parent_isei_true"] = parent_isei_true

    return d


# --------------------------------------------------------------------------
# Missingness — codebook section 7. Applied AFTER generation, so the truth
# file still has the values that were taken away.
# --------------------------------------------------------------------------


def apply_missingness(d: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 1)
    out = d.copy()
    n = len(out)

    # MAR — and it has to be MAR properly, which the first draft got wrong.
    #
    # Missingness must depend only on OBSERVED variables. An earlier version
    # made P(missing parent_isei) depend on parent_isei's own value, which is
    # MNAR, not MAR — and the distinction is not pedantry: multiple imputation
    # is justified under MAR and not under MNAR, so the wrong mechanism would
    # have taught the wrong lesson with a straight face.
    #
    # So: missingness depends on migration_bg and books_home_15, both fully
    # observed. Because books correlates with parental status (r ~ .55), the
    # rows that go missing are still disproportionately low-origin — the bite
    # survives, and now the imputation story is actually true.
    p_miss = inv_logit(
        -2.4
        + 1.6 * (out["migration_bg"] == "first_gen").to_numpy()
        + 0.9 * (out["migration_bg"] == "second_gen").to_numpy()
        - 0.45 * (out["books_home_15"].to_numpy() - 3)
    )
    out.loc[rng.random(n) < p_miss, "parent_isei"] = np.nan

    # MCAR
    out.loc[rng.random(n) < 0.03, "books_home_15"] = np.nan

    # Structural missingness is already in place from 6.15 / 6.16.
    return out


# --------------------------------------------------------------------------
# Validation — codebook section 9. The generator checks its own work.
# --------------------------------------------------------------------------

# Corrected 2026-08-17 against an actual run. The v2 codebook derived these by
# hand and was wrong on four of them — parent_isei sd, first_job_isei sd,
# current_isei sd and both work_hours moments. Hand-derived moments are a
# guess; these are measured.
TARGETS = {
    "parent_isei mean": 44,
    "parent_isei sd": 16.4,
    "edu_years mean": 13.5,
    "edu_years sd": 2.8,
    "first_job_isei mean": 44,
    "first_job_isei sd": 13,
    "current_isei mean": 47,
    "current_isei sd": 16.5,
    "n_children mean": 1.3,
    "employed share": 0.93,
    "work_hours mean": 36.9,
    "work_hours sd": 9.5,
}

CORR_VARS = [
    "parent_isei",
    "books_home_15",
    "edu_years",
    "first_job_isei",
    "current_isei",
]


def check_structural(d: pd.DataFrame, n: int) -> list[str]:
    problems = []
    if len(d) != n:
        problems.append(f"n is {len(d)}, expected {n}")
    if d["id"].duplicated().any():
        problems.append("duplicate ids")
    if not (d["age"] == REFERENCE_YEAR - d["birth_year"]).all():
        problems.append("age does not equal reference_year - birth_year")
    for col, lo, hi in [
        ("parent_isei", ISEI_MIN, ISEI_MAX),
        ("first_job_isei", ISEI_MIN, ISEI_MAX),
        ("current_isei", ISEI_MIN, ISEI_MAX),
        ("work_hours", 4, 60),
        ("edu_years", 8.0, 18.5),
        ("n_children", 0, CHILDREN_CAP),
    ]:
        s = d[col].dropna()
        if len(s) and (s.min() < lo or s.max() > hi):
            problems.append(f"{col} out of range [{lo}, {hi}]: {s.min()}-{s.max()}")
    not_emp = d["employed"] == 0
    if d.loc[not_emp, "work_hours"].notna().any():
        problems.append("work_hours present for a non-employed respondent")
    if d.loc[not_emp, "current_isei"].notna().any():
        problems.append("current_isei present for a non-employed respondent")
    if d.loc[~not_emp, "current_isei"].isna().any():
        problems.append("current_isei missing for an employed respondent")
    return problems


def recovery_check(d: pd.DataFrame) -> pd.DataFrame:
    """Refit codebook 8.1 and see what the planted structure looks like from
    the outside. NOTE: this estimates the TOTAL gender effect, which includes
    the pathway through work_hours — deliberately not controlled, because
    hours are a consequence, not a confounder (codebook 8.2). So these numbers
    are expected to sit BELOW the raw section 6.16 coefficients, and the gap
    between them is section 8.2 made numerical."""
    m = d.dropna(subset=["current_isei", "parent_isei"]).copy()
    female = (m["gender"] == "female").to_numpy(dtype=float)
    mid = (m["cohort"] == "middle").to_numpy(dtype=float)
    yng = (m["cohort"] == "younger").to_numpy(dtype=float)

    X = np.column_stack(
        [
            np.ones(len(m)),
            female,
            mid,
            yng,
            female * mid,
            female * yng,
            m["edu_years"].to_numpy(),
            m["parent_isei"].to_numpy(),
        ]
    )
    names = [
        "intercept",
        "female",
        "middle",
        "younger",
        "female:middle",
        "female:younger",
        "edu_years",
        "parent_isei",
    ]
    fit = ols(m["current_isei"].to_numpy(dtype=float), X, names)

    b = fit["coef"]
    return pd.DataFrame(
        {
            "planted (6.16)": [
                GENDER_TERM["female"]["older"],
                GENDER_TERM["female"]["middle"],
                GENDER_TERM["female"]["younger"],
            ],
            "recovered (total)": [
                b["female"],
                b["female"] + b["female:middle"],
                b["female"] + b["female:younger"],
            ],
        },
        index=["older", "middle", "younger"],
    )


def pooled_headline(d: pd.DataFrame) -> pd.DataFrame:
    """The obvious model: the one most people would fit first."""
    m = d.dropna(subset=["current_isei", "parent_isei"]).copy()
    X = np.column_stack(
        [
            np.ones(len(m)),
            (m["gender"] == "female").to_numpy(dtype=float),
            m["edu_years"].to_numpy(),
            m["parent_isei"].to_numpy(),
        ]
    )
    return ols(
        m["current_isei"].to_numpy(dtype=float),
        X,
        ["intercept", "female", "edu_years", "parent_isei"],
    )


def validate(d: pd.DataFrame, n: int, seed: int, reveal: bool) -> int:
    print("=" * 70)
    print(f"VALIDATION   n={len(d)}   seed={seed}")
    print("=" * 70)

    print("\n[1] Structural")
    problems = check_structural(d, n)
    if problems:
        for p in problems:
            print(f"    FAIL  {p}")
    else:
        print("    ok — ids unique, ranges respected, derived vars consistent,")
        print("         NA pattern matches employment exactly")

    print("\n[2] Marginals (categorical)")
    for col in ["gender", "region", "migration_bg", "cohort", "parent_edu", "edu"]:
        shares = d[col].value_counts(normalize=True).sort_index()
        pretty = "  ".join(f"{k}={v:.3f}" for k, v in shares.items())
        print(f"    {col:14s} {pretty}")

    print("\n[3] Marginals (continuous) — observed vs codebook section 5 target")
    rows = []
    for col in [
        "parent_isei",
        "edu_years",
        "first_job_isei",
        "current_isei",
        "n_children",
        "work_hours",
    ]:
        s = d[col].dropna()
        rows.append((f"{col} mean", s.mean(), TARGETS.get(f"{col} mean")))
        rows.append((f"{col} sd", s.std(), TARGETS.get(f"{col} sd")))
    rows.append(("employed share", d["employed"].mean(), TARGETS["employed share"]))
    for label, obs, tgt in rows:
        if tgt is None:
            print(f"    {label:22s} {obs:7.2f}")
        else:
            flag = "" if abs(obs - tgt) <= max(0.1 * abs(tgt), 0.5) else "   <-- off"
            print(f"    {label:22s} {obs:7.2f}   target {tgt:6.2f}{flag}")

    print("\n[4] Structure — correlations (all should be positive)")
    print(d[CORR_VARS].corr().round(3).to_string())
    print("    ^ this is the matrix to hold up against the rung 2 one.")
    print("      Re-run with the same seed and it is identical. That is the point.")

    print("\n[5] Missingness")
    for col in ["parent_isei", "books_home_15", "work_hours", "current_isei"]:
        print(f"    {col:16s} {d[col].isna().mean():.3f}")
    by_mig = d.groupby("migration_bg")["parent_isei"].apply(lambda s: s.isna().mean())
    print("    parent_isei missing by migration_bg:")
    for k, v in by_mig.items():
        print(f"        {k:12s} {v:.3f}")
    ok_mar = by_mig.get("first_gen", 0) > by_mig.get("none", 1)
    print(f"    MAR direction {'ok' if ok_mar else 'FAIL'} (first_gen > none)")

    print("\n[6] The headline — the model most people would fit first")
    print(pooled_headline(d).round(3).to_string())

    if reveal:
        print("\n[7] RECOVERY — does the structure in codebook §8 come back out?")
        print(recovery_check(d).round(2).to_string())
    else:
        print("\n[7] Recovery check not shown. Re-run with --reveal for it.")
        print("    (It refits the model by cohort and recovers §8.1.)")

    print()
    return 1 if problems else 0


# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=2400)
    ap.add_argument("--seed", type=int, default=20260908)
    ap.add_argument("--out", default="mobility_2026.csv")
    ap.add_argument("--truth-out", default="mobility_2026_truth.csv")
    ap.add_argument("--no-validate", action="store_true")
    ap.add_argument(
        "--reveal",
        action="store_true",
        help="print the recovery check (spoils codebook section 8)",
    )
    args = ap.parse_args()

    full = generate(args.n, args.seed)
    public = apply_missingness(full, args.seed)

    truth_cols = [c for c in public.columns]
    full[truth_cols].assign(
        _O=full["_O"].round(4), _parent_isei_true=full["_parent_isei_true"]
    ).to_csv(args.truth_out, index=False)

    public.drop(columns=["_O", "_parent_isei_true"]).to_csv(args.out, index=False)

    print(f"wrote {args.out}          ({args.n} rows, seed {args.seed})")
    print(f"wrote {args.truth_out}    (the same rows before missingness was applied)")

    if args.no_validate:
        return 0
    return validate(
        public.drop(columns=["_O", "_parent_isei_true"]), args.n, args.seed, args.reveal
    )


if __name__ == "__main__":
    sys.exit(main())

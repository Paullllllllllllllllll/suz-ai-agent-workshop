"""Tests for the canton-level aggregation."""

import pandas as pd

from sample_project import canton_rent_summary


def commune_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "commune": ["Oberwil", "Talbach", "Seeberg", "Hofikon", "Grundegg"],
            "canton": ["ZH", "ZH", "BE", "BE", "BE"],
            "population": [120000, 1500, 900, 2200, 45000],
            "average_rent_chf": [2600.0, 1400.0, 1000.0, 1250.0, 1900.0],
            "share_new_buildings": [0.10, 0.04, 0.02, 0.06, 0.15],
        }
    )


def test_summary_has_one_row_per_canton() -> None:
    summary = canton_rent_summary(commune_frame())
    assert list(summary["canton"]) == ["BE", "ZH"]
    assert list(summary.columns) == [
        "canton",
        "mean_rent_chf",
        "median_rent_chf",
        "population",
        "n_communes",
    ]


def test_summary_counts_and_population_totals() -> None:
    summary = canton_rent_summary(commune_frame()).set_index("canton")
    assert summary.loc["ZH", "n_communes"] == 2
    assert summary.loc["BE", "n_communes"] == 3
    assert summary.loc["ZH", "population"] == 121500
    assert summary.loc["BE", "population"] == 48100


def test_summary_rents_within_commune_range() -> None:
    df = commune_frame()
    summary = canton_rent_summary(df).set_index("canton")
    for canton, group in df.groupby("canton"):
        rents = group["average_rent_chf"]
        assert rents.min() <= summary.loc[canton, "mean_rent_chf"] <= rents.max()
        assert rents.min() <= summary.loc[canton, "median_rent_chf"] <= rents.max()

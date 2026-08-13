"""Load, clean, and aggregate the synthetic commune dataset."""

from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "commune",
    "canton",
    "population",
    "average_rent_chf",
    "share_new_buildings",
]


def load_communes(path: Path) -> pd.DataFrame:
    """Read the raw commune CSV and validate its column layout."""
    df = pd.read_csv(path)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"raw file {path} is missing columns: {missing}")
    return df[EXPECTED_COLUMNS]


def clean_communes(df: pd.DataFrame) -> pd.DataFrame:
    """Drop unusable rows and normalise types and text fields.

    Rules: strip whitespace from commune names, drop rows without a rent
    value or with a non-positive population, drop duplicate communes within
    a canton, and clip the new-building share to [0, 1].
    """
    out = df.copy()
    out["commune"] = out["commune"].str.strip()
    out = out.dropna(subset=["average_rent_chf"])
    out = out[out["population"] > 0]
    out = out.drop_duplicates(subset=["commune", "canton"])
    out["population"] = out["population"].astype(int)
    out["average_rent_chf"] = out["average_rent_chf"].astype(float)
    out["share_new_buildings"] = out["share_new_buildings"].clip(0.0, 1.0)
    return out.reset_index(drop=True)


def canton_rent_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate cleaned commune rows to one summary row per canton."""
    grouped = df.groupby("canton")
    summary = pd.DataFrame(
        {
            "mean_rent_chf": grouped["average_rent_chf"].mean(),
            "median_rent_chf": grouped["average_rent_chf"].median(),
            "population": grouped["population"].sum(),
            "n_communes": grouped.size(),
        }
    )
    summary = summary.round(2).sort_index()
    return summary.reset_index()

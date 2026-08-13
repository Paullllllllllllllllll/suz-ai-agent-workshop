"""Tests for loading and cleaning the raw commune data."""

from pathlib import Path

import pandas as pd
import pytest

from sample_project import clean_communes, load_communes

ROOT = Path(__file__).resolve().parents[1]


def dirty_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "commune": ["  Oberwil  ", "Talbach", "Talbach", "Seeberg", "Hofikon"],
            "canton": ["ZH", "BE", "BE", "LU", "ZH"],
            "population": [1200, 800, 800, 0, 4500],
            "average_rent_chf": [1500.0, 1100.0, 1100.0, 900.0, None],
            "share_new_buildings": [0.05, 0.12, 0.12, 0.08, 1.4],
        }
    )


def test_load_communes_reads_raw_file() -> None:
    df = load_communes(ROOT / "data" / "raw" / "communes.csv")
    assert list(df.columns) == [
        "commune",
        "canton",
        "population",
        "average_rent_chf",
        "share_new_buildings",
    ]
    assert len(df) > 100


def test_load_communes_rejects_missing_columns(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text("commune,canton\nOberwil,ZH\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        load_communes(bad)


def test_clean_strips_names_and_drops_bad_rows() -> None:
    clean = clean_communes(dirty_frame())
    assert list(clean["commune"]) == ["Oberwil", "Talbach"]
    assert clean["population"].dtype.kind == "i"
    assert (clean["population"] > 0).all()
    assert clean["average_rent_chf"].notna().all()


def test_clean_clips_new_building_share() -> None:
    df = dirty_frame()
    df.loc[4, "average_rent_chf"] = 2000.0
    clean = clean_communes(df)
    assert clean["share_new_buildings"].between(0.0, 1.0).all()


def test_clean_is_idempotent() -> None:
    once = clean_communes(dirty_frame())
    twice = clean_communes(once)
    pd.testing.assert_frame_equal(once, twice)

"""Prepare step: read raw commune data, clean it, write the processed table."""

from pathlib import Path

from sample_project import clean_communes, load_communes

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    raw = load_communes(ROOT / "data" / "raw" / "communes.csv")
    clean = clean_communes(raw)
    out_path = ROOT / "data" / "processed" / "communes_clean.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(out_path, index=False)
    print(f"01_prepare: {len(raw)} raw rows -> {len(clean)} clean rows")
    print(f"01_prepare: wrote {out_path}")


if __name__ == "__main__":
    main()

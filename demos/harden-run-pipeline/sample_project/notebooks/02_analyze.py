"""Analyze step: canton-level rent statistics table and bar chart."""

from pathlib import Path

import matplotlib
import pandas as pd

from sample_project import canton_rent_summary

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    communes = pd.read_csv(ROOT / "data" / "processed" / "communes_clean.csv")
    summary = canton_rent_summary(communes)

    out_dir = ROOT / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "canton_rents.csv"
    summary.to_csv(csv_path, index=False)
    print(f"02_analyze: wrote {csv_path}")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(summary["canton"], summary["mean_rent_chf"], color="#4c72b0")
    ax.set_xlabel("Canton")
    ax.set_ylabel("Average rent (CHF)")
    ax.set_title("Canton-level average rent")
    fig.tight_layout()

    png_path = out_dir / "canton_rents.png"
    fig.savefig(png_path, dpi=150)
    plt.close(fig)
    print(f"02_analyze: wrote {png_path}")


if __name__ == "__main__":
    main()

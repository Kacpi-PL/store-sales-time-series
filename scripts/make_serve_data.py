"""Build a small serving dataset from data/raw.

Keeps only the tail of the big date-indexed files plus the small support files,
so the API runs the real pipeline without shipping the full 117 MB train.csv.
Run from the repo root: python -m scripts.make_serve_data
"""

import shutil

import pandas as pd

from src.config import cfg

TAIL_DAYS = 90  # >= cfg.lag_history_days (60), with margin

cfg.serve_data_dir.mkdir(parents=True, exist_ok=True)

for name in ["test.csv", "oil.csv", "holidays_events.csv", "stores.csv"]:
    shutil.copy(cfg.raw_data_dir / name, cfg.serve_data_dir / name)

for name in ["train.csv", "transactions.csv"]:
    df = pd.read_csv(cfg.raw_data_dir / name, parse_dates=["date"])
    cutoff = df["date"].max() - pd.Timedelta(days=TAIL_DAYS)
    df[df["date"] >= cutoff].to_csv(cfg.serve_data_dir / name, index=False)

print(f"wrote serving data to {cfg.serve_data_dir}")

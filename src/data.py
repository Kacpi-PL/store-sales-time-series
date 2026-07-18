import pandas as pd

from src.config import cfg


def load_raw(data_dir=cfg.raw_data_dir) -> dict:
    return {
        "holidays": pd.read_csv(data_dir / "holidays_events.csv", parse_dates=["date"]),
        "oil": pd.read_csv(data_dir / "oil.csv", parse_dates=["date"]),
        "stores": pd.read_csv(data_dir / "stores.csv"),
        "test": pd.read_csv(data_dir / "test.csv", parse_dates=["date"]),
        "train": pd.read_csv(data_dir / "train.csv", parse_dates=["date"]),
        "transactions": pd.read_csv(data_dir / "transactions.csv", parse_dates=["date"]),
    }

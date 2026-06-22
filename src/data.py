import pandas as pd
from src.config import cfg



def load_raw() -> dict:

    raw_data = {
        "holidays" : pd.read_csv(cfg.raw_data_dir / "holidays_events.csv", parse_dates=['date']),
        "oil" : pd.read_csv(cfg.raw_data_dir / "oil.csv", parse_dates=['date']),
        "stores" : pd.read_csv(cfg.raw_data_dir / "stores.csv"),
        "test" : pd.read_csv(cfg.raw_data_dir / "test.csv", parse_dates=['date']),
        "train" : pd.read_csv(cfg.raw_data_dir / "train.csv", parse_dates=['date']),
        "transactions" : pd.read_csv(cfg.raw_data_dir / "transactions.csv", parse_dates=['date'])
    }
    return raw_data


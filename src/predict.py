import json

import numpy as np
import pandas as pd
import xgboost as xgb

from src.config import cfg
from src.data import load_raw
from src.features import build_test_features


def main():
    with open(cfg.models_dir / "feature_columns.json") as f:
        feature_cols = json.load(f)

    model = xgb.XGBRegressor()
    model.load_model(cfg.models_dir / "model.json")

    raw = load_raw()
    X_test, ids = build_test_features(raw, feature_cols)

    log_pred = model.predict(X_test)
    sales = np.clip(np.expm1(log_pred), 0, None)

    submission = pd.DataFrame({"id": ids, "sales": sales})
    submission.to_csv(cfg.submission_path, index=False)
    print(f"wrote {len(submission):,} rows to {cfg.submission_path}")


if __name__ == "__main__":
    main()

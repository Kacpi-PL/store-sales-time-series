import json

import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error

from src.config import cfg
from src.data import load_raw
from src.features import build_train_features


def main():
    raw = load_raw()
    X, y, dates, feature_cols = build_train_features(raw)

    mask = dates < cfg.cutoff_date
    X_train, X_val = X[mask], X[~mask]
    y_train, y_val = y[mask], y[~mask]
    print(f"train rows: {len(X_train):,} | val rows: {len(X_val):,}")

    model = xgb.XGBRegressor(
        **cfg.xgb_params(),
        early_stopping_rounds=cfg.early_stopping_rounds,
    )
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=50)

    val_pred = model.predict(X_val)
    rmsle = np.sqrt(mean_squared_error(y_val, val_pred))
    print(f"best iteration: {model.best_iteration} | validation RMSLE: {rmsle:.5f}")

    cfg.models_dir.mkdir(parents=True, exist_ok=True)
    model.save_model(cfg.models_dir / "model.json")
    with open(cfg.models_dir / "feature_columns.json", "w") as f:
        json.dump(feature_cols, f)
    print(f"saved model + feature_columns to {cfg.models_dir}")


if __name__ == "__main__":
    main()

"""FastAPI service serving 16-day sales forecasts from the trained model."""

import json

import numpy as np
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, HTTPException

from src.config import cfg
from src.data import load_raw
from src.features import build_test_features

with open(cfg.models_dir / "feature_columns.json") as f:
    feature_cols = json.load(f)

model = xgb.XGBRegressor()
model.load_model(cfg.models_dir / "model.json")

# run the real pipeline once at startup on the small serving data, then cache
raw = load_raw(cfg.serve_data_dir)
X, ids = build_test_features(raw, feature_cols)
preds = np.clip(np.expm1(model.predict(X)), 0, None)
forecast = raw["test"][["id", "store_nbr", "family", "date"]].merge(
    pd.DataFrame({"id": ids.values, "predicted_sales": preds}), on="id"
)

app = FastAPI(title="Store Sales Forecast API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/forecast")
def get_forecast(store_nbr: int, family: str):
    rows = forecast[(forecast.store_nbr == store_nbr) & (forecast.family == family)]
    if rows.empty:
        raise HTTPException(404, "unknown store_nbr / family")
    rows = rows.sort_values("date")
    return [
        {"date": d.strftime("%Y-%m-%d"), "predicted_sales": float(s)}
        for d, s in zip(rows.date, rows.predicted_sales)
    ]

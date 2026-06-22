# Store Sales - Time Series Forecasting

Forecasting daily sales per store and product family for the Ecuadorian retailer
Corporacion Favorita, using gradient-boosted trees (XGBoost).

Kaggle competition: <https://www.kaggle.com/competitions/store-sales-time-series-forecasting>

Best public leaderboard score so far: **0.45824 RMSLE**.

## Problem

Predict `sales` for each `(store_nbr, family, date)` over a 16-day horizon. The metric is
RMSLE, so the target is trained in log space (`log1p`) and predictions are inverted with
`expm1` and clipped at 0.

## Data

The CSVs are not included in this repo (gitignored). Download the dataset from the
[competition Data tab](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data)
and unzip the six files into `data/raw/`:

| File | What it holds |
|------|---------------|
| `train.csv` / `test.csv` | daily sales history / rows to forecast |
| `stores.csv` | store metadata (city, state, type, cluster) |
| `oil.csv` | daily oil price |
| `holidays_events.csv` | national / regional / local holidays |
| `transactions.csv` | daily transaction counts (currently unused) |

## Structure

```
data/raw/       competition CSVs (download yourself, gitignored)
models/         saved model.json and feature_columns.json
src/
  config.py     all paths, dates, lags and hyperparameters
  data.py       load the raw CSVs
  features.py   feature engineering, shared by train and predict
  train.py      time split, fit with early stopping, save the model
  predict.py    build test features, write submission.csv
requirements.txt
README.md
```

Run modules from the repo root as `python -m src.<module>`.

## Setup

Python 3.12, dependencies pinned in `requirements.txt`.

```
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Usage

```
python -m src.train      # fit, print validation RMSLE, save models/
python -m src.predict    # write submission.csv
```

## Results

RMSLE, lower is better. Validation is a single time-based holdout on/after 2017-07-31; the
Kaggle leaderboard is the honest number.

| Step | Val | Kaggle LB |
|------|-----|-----------|
| original notebook | - | 0.49076 |
| src baseline (500 trees) | 0.44276 | - |
| early stopping + LR tuning | 0.42665 | 0.47040 |
| + rolling-mean features | 0.42207 | 0.46470 |
| + calendar features | 0.41539 | 0.45824 |

The pattern so far: feature engineering moves the score far more than hyperparameter
tuning.

## Roadmap

This started as a single notebook and is being rebuilt into a structured, reproducible,
tested project. Planned next steps:

- `onpromotion` lags and rolling features
- TimeSeriesSplit cross-validation instead of a single holdout
- MLflow for experiment tracking
- pytest tests and schema validation on the raw data
- GitHub Actions CI (lint and tests)
- Dockerfile and a Makefile for one-command setup / train / predict
- FastAPI `/predict` endpoint and a cloud-deployed demo

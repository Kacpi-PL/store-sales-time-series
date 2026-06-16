# Store Sales — Time Series Forecasting

Forecasting daily sales per store and product family for the Ecuadorian retailer
**Corporación Favorita**, using gradient-boosted trees (XGBoost).

Kaggle competition: <https://www.kaggle.com/competitions/store-sales-time-series-forecasting>

> ML / DevOps portfolio project. Started as a single exploratory notebook and is being
> rebuilt into a structured, reproducible, tested pipeline. See [ROADMAP.md](ROADMAP.md).

## Problem

Predict `sales` for each `(store_nbr, family, date)` over a 16-day horizon. The
competition is scored with **RMSLE** (Root Mean Squared Logarithmic Error), so the
target is trained in log space (`log1p`) and predictions are inverted with `expm1`.

## Data

Download from the [competition page](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data)
and place the CSVs in `data/raw/` (gitignored).

| File | Description |
|------|-------------|
| `train.csv` | Daily sales history, with `onpromotion`. |
| `test.csv` | Rows to forecast (16-day horizon). |
| `stores.csv` | Store metadata (city, state, type, cluster). |
| `oil.csv` | Daily oil price — Ecuador's economy is oil-dependent. |
| `holidays_events.csv` | National / regional / local holidays and events. |
| `transactions.csv` | Daily transaction counts per store. |

## Project structure

<!-- TODO: fill in as modules are built (see ROADMAP.md Phase 1) -->
```
data/        # raw/ and processed/ (gitignored)
notebooks/   # EDA
src/         # config, data, features, train, predict
tests/
```

## Setup

<!-- TODO: update once requirements.txt exists (ROADMAP.md Phase 0) -->
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Unix: source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

<!-- TODO: update once train.py / predict.py exist (ROADMAP.md Phase 1) -->
```bash
python -m src.train      # fit model, log metrics, save artifacts
python -m src.predict    # generate submission.csv
```

## Results

<!-- TODO: record validation RMSLE per experiment (ROADMAP.md Phase 2-3) -->
| Experiment | Validation RMSLE | Notes |
|------------|------------------|-------|
| baseline   | _TBD_            | _TBD_ |

## License

<!-- TODO -->

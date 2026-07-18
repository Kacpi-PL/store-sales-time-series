# Store Sales – Time Series Forecasting

[![CI](https://github.com/Kacpi-PL/store-sales-time-series/actions/workflows/ci.yml/badge.svg)](https://github.com/Kacpi-PL/store-sales-time-series/actions/workflows/ci.yml)

Forecasting daily sales per store and product family for the Ecuadorian retailer
Corporación Favorita, using gradient-boosted trees (XGBoost).

> ### You are on the `feat/api-cloud` branch
> On **`main`**, this project is a *script*: you run it once and it writes a file full of
> predictions. On **this branch** the same model becomes a **live web service** — a running
> program that other apps (or a simple web address) can ask for a forecast and get an answer
> back instantly. It is packed into a **container** (a standard "box" that runs the same on
> any computer or cloud) and is **deployed live on AWS**, reachable over HTTPS.
>
> Same model, same numbers — a new, usable way to deliver it.

## Why this branch exists

`main` already does the hard machine-learning part well. But a file of predictions on one
laptop is not something a company can actually *use*. This branch is about the engineering
around the model — turning it into a small service that could run in the cloud with its own
web address. It doubles as a hands-on way to practise the tools a Cloud/DevOps role uses:
**API, Docker, and Infrastructure-as-Code (Terraform) on AWS.**

## What is different from `main`

| | `main` | this branch (`feat/api-cloud`) |
|---|---|---|
| **What you get** | a file of predictions (`submission.csv`) | a live service (an **API**) |
| **How you use it** | run a script once | ask a question, get an answer back |
| **Packaging** | runs on your machine | **container** (Docker) **deployed on AWS** via Terraform |
| **Data needed** | the full 117 MB dataset | a small 8 MB slice, bundled in |
| **Libraries** | everything (training + tracking) | only the few needed to answer requests |

Nothing from `main` was broken — the original script still works. This branch only **adds**
the service layer on top.

## What the service answers

You ask it for one store and one product family, and it returns the **next 16 days** of
predicted sales. (16 days is exactly the task the model was built for — the days right after
the last date in the data.)

```
GET /forecast?store_nbr=1&family=GROCERY I

[
  { "date": "2017-08-16", "predicted_sales": 2817.17 },
  { "date": "2017-08-17", "predicted_sales": 2471.51 },
  ...  16 days total  ...
]
```

There is also a `GET /health` check that simply confirms the service is up.

## Trade-offs we made (and why)

Real engineering is about sensible compromises. The main ones here, in plain terms:

1. **We ship a small slice of the data, not all of it.** The full history is 117 MB — too
   big for GitHub and too heavy for a cloud container. The service only needs the last ~90
   days of history to build its forecast, so we bundle just that (8 MB). **The predictions
   come out identical** — the rest of the data only matters when *training* the model, not
   when *using* it.

2. **The container installs only the libraries it needs.** Training uses heavy tools
   (experiment tracking, etc.); answering a request does not. Keeping the service lean makes
   the container small and quick to start.

3. **The forecast is a fixed 16-day window.** That is what the model was designed for, so the
   service answers "the next 16 days for this store and product", not any arbitrary future
   date.

4. **We work on a branch, not on `main`.** `main` stays clean and always working; the cloud
   experiments live here until they are ready to merge.

## How it is deployed (AWS)

The container is deployed to AWS entirely through **Terraform** (Infrastructure-as-Code) — no
clicking in the console. The flow:

```
docker build  →  Amazon ECR (image registry)  →  Amazon ECS Express Mode  →  public HTTPS URL
```

The ECR repository, the IAM roles, and the container service all live in `infra/main.tf`, so
the whole stack can be created or torn down with one command (`terraform apply` /
`terraform destroy`).

**A migration along the way:** it first ran on AWS App Runner, but App Runner is being retired
(no new customers from April 2026), so it was moved to **Amazon ECS Express Mode** — the
current recommended service — in a single `terraform apply`. The Docker image, ECR, and IAM
work all carried over unchanged; only the runtime swapped. That is exactly why infrastructure
is defined as code.

## Run the API locally

```
pip install -r requirements-api.txt
uvicorn src.api:app --reload
```

Then open **http://localhost:8000/docs** — an auto-generated page where you can try the
`/forecast` endpoint with a click.

`data/serve/` (the 8 MB slice) is already in the repo, so this works out of the box. To
rebuild that slice from the full dataset: `python -m scripts.make_serve_data`.

## Run the original batch pipeline (same as `main`)

The full CSVs are not in the repo. Download them from the
[competition Data tab](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data)
into `data/raw/`, then:

```
pip install -r requirements.txt
python -m src.train      # fit the model, save it to models/
python -m src.predict    # write submission.csv
```

## Results (accuracy)

RMSLE, lower is better. Validation is a time-based holdout; the Kaggle leaderboard is the
honest number.

| Step | Val | Kaggle LB |
|------|-----|-----------|
| original notebook | – | 0.49076 |
| structured baseline | 0.44276 | – |
| early stopping + tuning | 0.42665 | 0.47040 |
| + rolling-mean features | 0.42207 | 0.46470 |
| + calendar features | 0.41539 | **0.45824** |

## Status of this branch

| Step | State |
|------|-------|
| API – live `/forecast` service on the bundled data | done |
| Docker – container image, pushed to Amazon ECR | done |
| AWS deploy – ECS Express Mode via Terraform, public HTTPS URL | done |
| CI/CD – build, push and deploy automatically on every change | planned |

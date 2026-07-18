"""Single source of config for the pipeline. Import the `cfg` instance."""

from dataclasses import dataclass
from pathlib import Path

# repo root, two levels up from this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    # paths
    mlflow_db: Path = PROJECT_ROOT / "mlflow.db"
    experiment_name: str = "store-sales"
    raw_data_dir: Path = PROJECT_ROOT / "data" / "raw"
    serve_data_dir: Path = PROJECT_ROOT / "data" / "serve"
    processed_data_dir: Path = PROJECT_ROOT / "data" / "processed"
    models_dir: Path = PROJECT_ROOT / "models"
    submission_path: Path = PROJECT_ROOT / "submission.csv"

    # features
    # 16 = test horizon; shorter lags don't exist at prediction time
    lags: tuple[int, ...] = (16, 21, 30)
    # windows end min(lags) days back, so they only use sales known at inference
    roll_windows: tuple[int, ...] = (7, 14, 28)
    # test bridge history; must cover min(lags) + max(roll_windows) = 44, plus margin
    lag_history_days: int = 60

    # train/val split, time-based, never shuffled
    cutoff_date: str = "2017-07-31"  # before -> train, on/after -> val

    # model; n_estimators is a cap, early stopping picks the real tree count
    n_estimators: int = 12000
    learning_rate: float = 0.025
    early_stopping_rounds: int = 100
    random_state: int = 42
    n_jobs: int = -1  # -1 = all cores

    def xgb_params(self) -> dict:
        return {
            "n_estimators": self.n_estimators,
            "learning_rate": self.learning_rate,
            "random_state": self.random_state,
            "n_jobs": self.n_jobs,
        }


cfg = Config()

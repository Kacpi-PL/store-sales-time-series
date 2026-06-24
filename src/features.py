import numpy as np
import pandas as pd
from src.config import cfg


def preprocess_holidays(holidays) -> pd.DataFrame:
    # Locale -> one-hot (Local / National / Regional)
    holidays = pd.get_dummies(holidays, columns=["locale"], dtype=int)

    # Event flags from the description text
    holidays['is_earthquake'] = holidays['description'].str.contains('Terremoto').astype(int)
    holidays['is_christmas'] = holidays['description'].str.contains('Navidad').astype(int)
    holidays['is_carnaval'] = holidays['description'].str.contains('Carnaval').astype(int)

    # Type -> one-hot; drop the raw description
    holidays = pd.get_dummies(holidays, columns=["type"], dtype=int)
    holidays = holidays.drop(columns='description')

    # Transferred holidays didn't happen on this date -> zero their flags
    holiday_columns = ['type_Holiday', 'type_Event', 'locale_Local', 'locale_National', 'is_christmas', 'is_carnaval']
    holidays.loc[holidays['transferred'] == True, holiday_columns] = 0
    holidays = holidays.drop(columns=['transferred'])

    # Collapse to one row per date so the merge onto sales stays 1-to-1
    agg = {c: 'max' for c in holidays.columns if c not in ('date', 'locale_name')}
    agg['locale_name'] = 'first'
    holidays = holidays.groupby('date', as_index=False).agg(agg)

    return holidays


def add_sales_history_features(df) -> pd.DataFrame:
    # shared by train and the test bridge; caller must sort rows per (store_nbr, family)
    base = min(cfg.lags)
    g = df.groupby(["store_nbr", "family"])["sales"]

    # Sales lags
    for lag in cfg.lags:
        df[f"sales_lag_{lag}"] = g.shift(lag)

    # Rolling means, window ending `base` days back
    for w in cfg.roll_windows:
        df[f"sales_roll_mean_{w}"] = g.transform(lambda s: s.shift(base).rolling(w).mean())
    return df


def add_sales_lags_train(train) -> pd.DataFrame:
    train = train.sort_values(["store_nbr", "family", "date"])
    return add_sales_history_features(train)


def add_sales_lags_test(test, train) -> pd.DataFrame:
    # Tail of real train history (covers the deepest lookback)
    history_data = train[train['date'] >= (train['date'].max() - pd.Timedelta(days=cfg.lag_history_days))]
    history_data = history_data[['date', 'store_nbr', 'family', 'sales']]

    # Test rows with unknown sales
    test_skeleton = test[['date', 'store_nbr', 'family']].copy()
    test_skeleton['sales'] = np.nan

    # Bridge: build lags on history + test together, then keep only test rows
    bridge = pd.concat([history_data, test_skeleton], axis=0)
    bridge = bridge.sort_values(['store_nbr', 'family', 'date'])
    bridge = add_sales_history_features(bridge)
    test_with_lags = bridge[bridge['sales'].isna()].drop(columns=['sales'])

    test = pd.merge(test, test_with_lags, on=['date', 'store_nbr', 'family'], how='left')
    return test


def add_holiday_distance(df, holidays_raw) -> pd.DataFrame:
    # National days off only; a transferred holiday moves to a 'Transfer' row, so keep those
    nat = holidays_raw[(holidays_raw['locale'] == 'National') &
                       (holidays_raw['transferred'] == False) &
                       (holidays_raw['type'].isin(['Holiday', 'Transfer', 'Additional', 'Bridge']))]
    hol = pd.DataFrame({'date': sorted(nat['date'].unique())})
    hol['hol_date'] = hol['date']
    cal = pd.DataFrame({'date': sorted(df['date'].unique())})

    # Nearest holiday before and after each date
    prev = pd.merge_asof(cal, hol, on='date', direction='backward')
    nxt = pd.merge_asof(cal, hol, on='date', direction='forward')
    dist = pd.DataFrame({
        'date': cal['date'],
        'days_since_holiday': (cal['date'] - prev['hol_date']).dt.days,
        'days_until_holiday': (nxt['hol_date'] - cal['date']).dt.days,
    })
    # edge dates have no match; sentinel keeps them out of dropna instead of NaN
    dist = dist.fillna(999)
    return df.merge(dist, on='date', how='left')


def _merge_stores(df, raw) -> pd.DataFrame:
    df = pd.merge(df, raw['stores'], on='store_nbr', how='left')
    df = pd.get_dummies(df, columns=['type', 'store_nbr'], dtype=int)
    return df


def _merge_holidays(df, raw) -> pd.DataFrame:
    holidays = preprocess_holidays(raw['holidays'])
    df = pd.merge(df, holidays, on='date', how='left')
    flag_cols = [c for c in holidays.columns if c not in ('date', 'locale_name')]
    df[flag_cols] = df[flag_cols].fillna(0)
    return df


def _flag_real_holiday(df) -> pd.DataFrame:
    conditions = [
        df["locale_National"] == 1,
        (df["locale_Regional"] == 1) & (df["state"] == df["locale_name"]),
        (df["locale_Local"] == 1) & (df["city"] == df["locale_name"]),
    ]
    df["is_real_holiday"] = np.select(conditions, [1, 1, 1], default=0)
    return df


def _one_hot_famil(df) -> pd.DataFrame:
    df = pd.get_dummies(df, columns=["family"], dtype=int)
    return df


def _merge_oil(df, raw) -> pd.DataFrame:
    # Oil has gaps (weekends); reindex to a daily calendar and fill before merging
    calendar = pd.DataFrame({'date': pd.date_range(start=df['date'].min(), end=df['date'].max())})
    oil_full = pd.merge(calendar, raw['oil'], on='date', how='left')
    oil_full['dcoilwtico'] = oil_full['dcoilwtico'].ffill().bfill()
    df = pd.merge(df, oil_full, on='date', how='left')
    return df


def _calendar_features(df, raw) -> pd.DataFrame:
    df['dayofweek'] = df['date'].dt.dayofweek  # 0=Mon, 6=Sun
    df = pd.get_dummies(df, columns=['dayofweek'], dtype=int)
    # Ecuador pays public wages on the 15th and month-end
    df['is_payday'] = ((df['date'].dt.day == 15) | df['date'].dt.is_month_end).astype(int)
    df = add_holiday_distance(df, raw['holidays'])
    return df


def _drop_helper(df) -> pd.DataFrame:
    df = df.drop(columns=['city', 'state', 'locale_name'])
    return df


def add_static_features(df, raw) -> pd.DataFrame:
    df = _merge_stores(df, raw)
    df = _merge_holidays(df, raw)
    df = _flag_real_holiday(df)
    df = _one_hot_famil(df)
    df = _merge_oil(df, raw)
    df = _calendar_features(df, raw)
    df = _drop_helper(df)
    return df


def build_train_features(raw) -> tuple:
    # Build features; dropna removes early rows without lag history
    df = add_sales_lags_train(raw['train'])
    df = add_static_features(df, raw)
    df = df.dropna()

    # X / y split; target in log space for RMSLE
    dates = df['date']
    y = np.log1p(df['sales'])
    X = df.drop(columns=['date', 'sales', 'id'])
    feature_cols = X.columns.tolist()
    return X, y, dates, feature_cols


def build_test_features(raw, feature_cols) -> tuple:
    df = add_sales_lags_test(raw['test'], raw['train'])
    df = add_static_features(df, raw)

    # Align test columns to the trained feature list (missing one-hots -> 0)
    ids = df['id']
    X = df.reindex(columns=feature_cols, fill_value=0)
    return X, ids

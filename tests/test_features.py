import pandas as pd
from src.features import preprocess_holidays, add_sales_history_features


def test_preprocess_holidays():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2017-12-25", "2017-12-25", "2016-05-01"]),
        "type": ["Holiday", "Event", "Holiday"],
        "locale": ["National", "Local", "National"],
        "locale_name": ["Ecuador", "Quito", "Ecuador"],
        "description": ["Navidad", "Fiesta Quito", "Dia del Trabajo"],
        "transferred": [False, False, True]
    })
    out = preprocess_holidays(df)
    assert out["date"].is_unique
    assert out.loc[out["date"] == "2017-12-25", "is_christmas"].iloc[0] == 1
    assert out.loc[out["date"] == "2016-05-01", "type_Holiday"].iloc[0] == 0

def test_add_sales_history_features():
    n = 50
    df = pd.DataFrame({
        "store_nbr": [1] * n,
        "family": ['BREAD'] * n,
        "sales": range(n),
    })
    out = add_sales_history_features(df)


    df2 = pd.DataFrame({
        "store_nbr": [1] * n + [2] * n,
        "family": ['BREAD'] * n * 2,
        "sales": list(range(n)) * 2,

    })
    out2 = add_sales_history_features(df2)

    assert out["sales_lag_16"].iloc[20] == 20 - 16
    assert out["sales_lag_16"].iloc[:16].isna().all()
    assert out["sales_roll_mean_7"].iloc[30] == 11

    assert out2["sales_lag_16"].iloc[50:66].isna().all()
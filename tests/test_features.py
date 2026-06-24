import pandas as pd
from src.features import preprocess_holidays


def test_preprocess_holidays():
    df = pd.DataFrame({
        "date" : pd.to_datetime(["2017-12-25", "2017-12-25", "2016-05-01"]),
        "type" : ["Holiday", "Event", "Holiday"],
        "locale" : ["National", "Local", "National"],
        "locale_name" : ["Ecuador", "Quito", "Ecuador"],
        "description" : ["Navidad", "Fiesta Quito", "Dia del Trabajo"],
        "transferred" : [False, False, True]
    })
    out = preprocess_holidays(df)
    assert out["date"].is_unique
    assert out.loc[out["date"] == "2017-12-25", "is_christmas"].iloc[0] == 1
    assert out.loc[out["date"] == "2016-05-01", "type_Holiday"].iloc[0] == 0
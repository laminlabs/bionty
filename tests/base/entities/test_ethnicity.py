import bionty.base as bt_base
import pandas as pd


def test_hancestro_ethnicity_inspect_name():
    df = pd.DataFrame(
        index=[
            "Mende",
            "European",
            "South Asian",
            "Arab",
            "This ethnicity does not exist",
        ]
    )

    et = bt_base.Ethnicity(source="hancestro")
    inspected_df = et.inspect(df.index, field=et.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)

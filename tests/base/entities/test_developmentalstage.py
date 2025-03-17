import bionty.base as bt_base
import pandas as pd


def test_hsapdv_developmentalstage_inspect_name():
    df = pd.DataFrame(
        index=[
            "blastula stage",
            "Carnegie stage 03",
            "neurula stage",
            "organogenesis stage",
            "This developmental stage does not exist",
        ]
    )

    ds = bt_base.DevelopmentalStage(source="hsapdv")
    inspected_df = ds.inspect(df.index, field=ds.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)

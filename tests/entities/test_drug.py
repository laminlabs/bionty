import bionty.base as bt
import pandas as pd


def test_dron_drug_inspect_name():
    df = pd.DataFrame(
        index=[
            "LILIUM LONGIFLORIUM",
            "citrus bioflavonoids",
            "Ornithine, (L)-Isomer",
            "Hyoscyamus extract",
            "This drug does not exist",
        ]
    )

    dt = bt.Drug(source="dron")
    inspected_df = dt.inspect(df.index, field=dt.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)

import bionty.base as bt
import pandas as pd


def test_cl_celltype_inspect_name():
    df = pd.DataFrame(
        index=[
            "Boettcher cell",
            "bone marrow cell",
            "interstitial cell of ovary",
            "pancreatic ductal cell",
            "This cell type does not exist",
        ]
    )

    print(bt.settings.current_sources)
    assert bt.settings.current_sources.exists()

    ct = bt.CellType(source="cl")
    inspected_df = ct.inspect(df.index, field=ct.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)

import bionty.base as bt_base
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

    ct = bt_base.CellType(source="cl")
    inspected_df = ct.inspect(df.index, field=ct.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_cl_celltype_version():
    # old version, not in s3://bionty-assets
    ct = bt_base.CellType(version="2020-05-20")
    assert ct.df().shape[0] == 2355

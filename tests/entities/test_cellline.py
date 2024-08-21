import bionty.base as bt_base
import pandas as pd


def test_clo_cellline_inspect_name():
    df = pd.DataFrame(
        index=[
            "253D cell",
            "HEK293",
            "2C1H7 cell",
            "283TAg cell",
            "This cell line does not exist",
        ]
    )

    cl = bt_base.CellLine(source="clo")
    inspected_df = cl.inspect(df.index, field=cl.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_depmap_cellline_inspect_name():
    df = pd.DataFrame(
        index=[
            "NIH:OVCAR-3",
            "NRH-LMS1",
            "HEL",
            "HEL 92.1.7",
            "This cell line does not exist",
        ]
    )

    cl = bt_base.CellLine(source="depmap")
    inspected_df = cl.inspect(df.index, field=cl.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)

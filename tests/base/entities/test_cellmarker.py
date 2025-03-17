import bionty.base as bt_base
import pandas as pd


def test_cellmarker_cellmarker_inspect_name_human():
    df = pd.DataFrame(
        index=["CCR7", "CD69", "CD8", "CD45RA", "This protein does not exist"]
    )

    cm = bt_base.CellMarker(source="cellmarker")
    curated = cm.inspect(df.index, field=cm.name)

    assert curated["validated"] == ["CD69", "CD8", "CD45RA"]
    assert curated["non_validated"] == ["CCR7", "This protein does not exist"]


def test_cellmarker_cellmarker_inspect_name_mouse():
    df = pd.DataFrame(
        index=["Tcf4", "Cd36", "Cd34", "Lgr6", "This protein does not exist"]
    )

    cm = bt_base.CellMarker(source="cellmarker", organism="mouse")
    inspected_df = cm.inspect(df.index, field=cm.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, False, True, True, False])

    assert inspect.equals(expected_series)

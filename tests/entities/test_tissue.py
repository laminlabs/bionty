import bionty.base as bt_base
import pandas as pd


def test_uberon_tissue_inspect_ontology_id():
    df = pd.DataFrame(
        index=[
            "UBERON:0000000",
            "UBERON:0000005",
            "UBERON:8600001",
            "UBERON:8600002",
            "This tissue does not exist",
        ]
    )

    ts = bt_base.Tissue(source="uberon")
    inspected_df = ts.inspect(df.index, ts.ontology_id, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)

import bionty.base as bt_base
import pandas as pd


def test_uniprot_protein_inspect_uniprotkb_id():
    df = pd.DataFrame(
        index=[
            "A0A024QZ08",  # no longer exist in 2024-03 version
            "X6RLV5",
            "X6RM24",
            "A0A024QZQ1",  # no longer exist in 2024-03 version
            "This protein does not exist",
        ]
    )

    pr = bt_base.Protein(source="uniprot")
    inspected_df = pr.inspect(df.index, pr.uniprotkb_id, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([False, True, True, False, False])

    assert inspect.equals(expected_series)

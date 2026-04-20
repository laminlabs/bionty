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


def test_uniprot_protein_organism_from_scientific_name():
    TEST_PROTEINS = {
        "mouse-ear cress": "A0A022RI21",
        "bovine": "A0A023J7X0",
        "dog": "A0A023SFI1",
        "chinese hamster": "A0A061HTA4",
        "e. coli": "A0A023I6S3",
        "long-tailed macaque": "A0A023JBW5",
        "saccharomyces cerevisiae s288c": "A0A023IRJ6",
        "pig": "A0A023I2Y2",
    }
    for organism, valid_id in TEST_PROTEINS.items():
        pr = bt_base.Protein(organism=organism, source="uniprot")

        inspected_df = pr.inspect(
            [valid_id, "This does not exist"], "uniprotkb_id", return_df=True
        )
        inspect = inspected_df["__validated__"].reset_index(drop=True)
        expected = pd.Series([True, False])

        assert inspect.equals(expected), f"❌ Failed for {organism} ({valid_id})"

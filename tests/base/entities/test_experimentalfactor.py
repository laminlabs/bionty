import bionty.base as bt_base
import pandas as pd


def test_efo_experimental_factor_inspect_ontology_id():
    df = pd.DataFrame(
        index=[
            "EFO:1002048",
            "EFO:1002050",
            "EFO:1002047",
            "EFO:1002049",
            "This readout does not exist",
        ]
    )

    ro = bt_base.ExperimentalFactor(source="efo")
    inspected_df = ro.inspect(df.index, ro.ontology_id, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_efo_shape():
    """We observed issues with new EFO versions not including all records."""
    # 3.78.0 is the latest version where had initially observed this issue
    # If this works well, we may unpin the fixed version
    assert bt_base.ExperimentalFactor(version="3.78.0").to_dataframe().shape[0] > 18000

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

    efo = bt_base.ExperimentalFactor(source="efo")
    assert efo.df().shape[0] > 18000  # sanity check
    inspected_df = efo.inspect(df.index, efo.ontology_id, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)

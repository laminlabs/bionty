import bionty.base as bt_base
import pandas as pd
from bionty.base.entities._experimentalfactor import _parse_efo_term


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


def test_parse_efo_term():
    ro = bt_base.ExperimentalFactor(source="efo")
    ontology = ro.to_pronto()
    res = _parse_efo_term(term_id="EFO:0008913", ontology=ontology)

    assert res == {
        "ontology_id": "EFO:0008913",
        "name": "single-cell RNA sequencing",
        "molecule": "RNA assay",
        "instrument": "single cell sequencing",
        "measurement": None,
    }

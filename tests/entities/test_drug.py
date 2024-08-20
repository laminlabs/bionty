import bionty.base as bt_base
import pandas as pd


def test_dron_drug_inspect_name():
    df = pd.DataFrame(
        index=[
            "triflusal",
            "citrus bioflavonoids",
            "Candida albicans",
            "Hyoscyamus extract",
            "This drug does not exist",
        ]
    )

    dt = bt_base.Drug(source="dron")
    inspected_df = dt.inspect(df.index, field=dt.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_chebi_drug_inspect_name():
    df = pd.DataFrame(
        index=[
            "navitoclax",
            "Vismione D",
            "(+)-Atherospermoline",
            "N-[(2R,3S,6R)-2-(hydroxymethyl)-6-[2-[[oxo-[4-(trifluoromethyl)anilino]methyl]amino]ethyl]-3-oxanyl]-3-pyridinecarboxamide",
            "This drug does not exist",
        ]
    )

    dt = bt_base.Drug(source="chebi")
    inspected_df = dt.inspect(df.index, field=dt.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_chebi_chembl_id():
    dt = bt_base.Drug(source="chebi")
    assert "CHEMBL500609" in dt.df()["chembl_id"].values

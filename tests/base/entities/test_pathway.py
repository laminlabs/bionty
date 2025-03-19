import bionty.base as bt_base
import pandas as pd


def test_pw_go_inspect_ontology_id():
    df = pd.DataFrame(
        index=[
            "GO:1905210",
            "GO:1905211",
            "GO:1905212",
            "GO:1905208",
            "This pathway does not exist",
        ]
    )

    pw = bt_base.Pathway(source="go")
    inspected_df = pw.inspect(df.index, pw.ontology_id, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_pw_pathway_inspect_name():
    df = pd.DataFrame(
        index=[
            "Toll-like receptor 9 signaling pathway",
            "Toll-like receptor TLR1:TLR2 signaling pathway",
            "classic metabolic pathway",
            "regulatory pathway",
            "This pathway does not exist",
        ]
    )

    pw = bt_base.Pathway(source="pw")
    inspected_df = pw.inspect(df.index, field=pw.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)

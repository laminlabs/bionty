import bionty.base as bt
import pandas as pd


def test_ensembl_organism_inspect_name():
    df = pd.DataFrame(
        index=[
            "spiny chromis",
            "silver-eye",
            "platyfish",
            "california sea lion",
            "This organism does not exist",
        ]
    )

    sp = bt.Organism(source="ensembl")
    inspected_df = sp.inspect(df.index, field=sp.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_ensembl_organism_organism():
    for sp in ["bacteria", "plants", "fungi", "metazoa"]:
        df = bt.Organism(organism=sp).df()
        assert df.shape[0] > 10


def test_ncbitaxon_organism():
    df = bt.Organism(source="ncbitaxon").df()
    assert df.shape[0] > 10

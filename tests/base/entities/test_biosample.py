import bionty.base as bt_base


def test_ncbi_biosample():
    bs = bt_base.BioSample(source="ncbi")
    df = bs.df()
    assert "edta_inhibitor_tested" in df.abbr.tolist()

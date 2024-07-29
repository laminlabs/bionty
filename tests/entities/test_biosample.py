import bionty.base as bt


def test_ncbi_biosample():
    bs = bt.BioSample(source="ncbi")
    df = bs.df()
    assert "edta_inhibitor_tested" in df.abbr.tolist()

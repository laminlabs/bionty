import bionty as bt
import lamindb as ln
import lamindb_setup as ln_setup
import pytest


@pytest.fixture(scope="module")
def setup_instance():
    ln_setup.init(storage="./testdb", modules="bionty")
    yield
    ln_setup.delete("testdb", force=True)


def test_add_source(setup_instance):
    chebi_source = ln.Source.get(name="chebi", version="2024-07-27")
    new_source = bt.Phenotype.add_source(chebi_source)
    assert new_source.name == "chebi"
    assert new_source.version == "2024-07-27"
    assert new_source.dataframe_artifact.exists()

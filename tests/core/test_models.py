import bionty as bt
import lamindb_setup as ln_setup
import pytest


@pytest.fixture(scope="module")
def setup_instance():
    ln_setup.init(storage="./testdb", modules="bionty")
    yield
    ln_setup.delete("testdb", force=True)


def test_add_source(setup_instance):
    chebi_source = bt.Source.get(name="chebi", version="2024-07-27")
    new_source = bt.Phenotype.add_source(chebi_source)
    assert new_source.name == "chebi"
    assert new_source.version == "2024-07-27"
    assert new_source.dataframe_artifact is not None


def test_source_uids(setup_instance):
    disease_ontology = bt.Source(
        entity="bionty.Disease",
        name="mondo",
        version="2023-04-04",
        _skip_validation=True,
    )
    assert disease_ontology.uid == "Hgw08Vk3"
    phenotype_ontology = bt.Source(
        entity="bionty.Phenotype",
        name="hp",
        version="2023-06-17",
        organism="human",
        _skip_validation=True,
    )
    assert phenotype_ontology.uid == "451W7iJS"

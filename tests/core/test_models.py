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


def test_encode_uids(setup_instance):
    gene = bt.Gene(
        ensembl_gene_id="ENSG00000081059",
        symbol="TCF7",
        _skip_validation=True,
    )
    assert gene.uid == "7IkHKPl0ScQR"

    cell_type = bt.CellType(
        ontology_id="CL:0000084",
        _skip_validation=True,
    )
    assert cell_type.uid == "22LvKd01"

    organism = bt.Organism(
        ontology_id="NCBITaxon:9606",
        name="human",
        _skip_validation=True,
    )
    assert organism.uid == "1dpCL6Td"

    bt.settings.organism = "human"
    cell_marker = bt.CellMarker(
        name="test",
        organism=bt.settings.organism,
        _skip_validation=True,
    )
    assert cell_marker.uid == "2dZ52W9noUDK"

    disease = bt.Source(
        entity="bionty.Disease",
        name="mondo",
        version="2023-04-04",
        _skip_validation=True,
    )
    assert disease.uid == "Hgw08Vk3"

    phenotype = bt.Source(
        entity="bionty.Phenotype",
        name="hp",
        version="2023-06-17",
        organism="human",
        _skip_validation=True,
    )
    assert phenotype.uid == "451W7iJS"

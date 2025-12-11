import bionty as bt


def test_public_synonym_mapping():
    bt_result = bt.Gene.public(organism="human").inspect(
        ["ABC1", "TNFRSF4"], field="symbol"
    )
    assert bt_result.synonyms_mapper == {"ABC1": "HEATR6"}

    bt_result = bt.Gene.public(organism="human").inspect(
        ["ABC1", "TNFRSF4"], field="symbol", inspect_synonyms=False
    )
    assert bt_result.synonyms_mapper == {}


def test_encode_uids():
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

    gene = bt.Gene(
        ensembl_gene_id="ENSG00000081059",
        symbol="TCF7",
        organism=bt.settings.organism,  # required
        _skip_validation=True,
    )
    assert gene.uid == "7IkHKPl0ScQR"

    disease = bt.Source(
        entity="bionty.Disease",
        name="mondo",
        version="2023-04-04",
        organism="all",
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

import bionty as bt


def test_public_synonym_mapping():
    bt_result = bt.Gene.public(organism="human").inspect(
        ["ABC1", "TNFRSF4"], field="symbol"
    )
    # ABC1 is a synonym for both ABCA1 and HEATR6; accept either
    assert "ABC1" in bt_result.synonyms_mapper
    assert bt_result.synonyms_mapper["ABC1"] in ("ABCA1", "HEATR6")

    bt_result = bt.Gene.public(organism="human").inspect(
        ["ABC1", "TNFRSF4"], field="symbol", standardize=False
    )
    assert bt_result.synonyms_mapper == {}


def test_encode_uids():
    cell_type = bt.CellType(
        ontology_id="CL:0000084",
        _skip_validation=True,
    )
    assert cell_type.uid == "22LvKd01YyNA1a"

    organism = bt.Organism(
        ontology_id="NCBITaxon:9606",
        name="human",
        _skip_validation=True,
    )
    assert organism.uid == "1dpCL6TduFJ3AP"

    human = bt.Organism.from_source(name="human").save()
    cell_marker = bt.CellMarker(
        name="test",
        organism=human,
        _skip_validation=True,
    )
    assert cell_marker.uid == "2dZ52W9noUDKVE"

    gene = bt.Gene(
        ensembl_gene_id="ENSG00000081059",
        symbol="TCF7",
        organism=human,  # required
        _skip_validation=True,
    )
    assert gene.uid == "7IkHKPl0ScQRSB"

    source = bt.Source(
        entity="bionty.Disease",
        name="mondo",
        version="2023-04-04",
        organism="all",
        _skip_validation=True,
    )
    assert source.uid == "Hgw08Vk3"

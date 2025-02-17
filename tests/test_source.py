import bionty as bt


def test_source_uids():
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

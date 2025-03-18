import pytest
from bionty import Gene, settings
from bionty._organism import OrganismNotSet


def test_from_values_organism():
    settings._organism = None
    with pytest.raises(OrganismNotSet):
        Gene.from_values(["ABC1"], Gene.symbol)
    # no organism is needed if the values are ensembl gene ids
    result = Gene.from_values(["ENSG00000068097"], Gene.ensembl_gene_id)
    assert len(result) == 1
    result = Gene.from_values(
        ["ENSMUSG00000102862", "ENSMUSG00000084826"], field=Gene.ensembl_gene_id
    )
    assert len(result) == 2
    result = Gene.from_values(
        ["HRA1", "ETS1-1"], field=Gene.stable_id, organism="saccharomyces cerevisiae"
    )
    assert len(result) == 2

    settings.organism = "human"
    values = ["ABC1"]
    standardized_values = Gene.public().standardize(values)
    records = Gene.from_values(standardized_values, Gene.symbol)
    assert records[0].ensembl_gene_id == "ENSG00000068097"

    # TODO: Gene.public() should raise error if organism is not provided
    standardized_values = Gene.public(organism="mouse").standardize(values)
    records = Gene.from_values(standardized_values, Gene.symbol, organism="mouse")
    assert records[0].ensembl_gene_id == "ENSMUSG00000015243"

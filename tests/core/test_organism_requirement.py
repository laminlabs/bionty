import bionty as bt
import pytest
from bionty._organism import OrganismNotSet


def test_from_values_organism():
    bt.settings._organism = None
    with pytest.raises(OrganismNotSet):
        bt.Gene.from_values(["ABC1"], bt.Gene.symbol)
    # no organism is needed if the values are ensembl gene ids
    result = bt.Gene.from_values(["ENSG00000068097"], bt.Gene.ensembl_gene_id)
    assert len(result) == 1
    result = bt.Gene.from_values(
        ["ENSMUSG00000102862", "ENSMUSG00000084826"], field=bt.Gene.ensembl_gene_id
    )
    assert len(result) == 2
    result = bt.Gene.from_values(
        ["HRA1", "ETS1-1"], field=bt.Gene.stable_id, organism="saccharomyces cerevisiae"
    )
    assert len(result) == 2

    bt.settings.organism = "human"
    values = ["ABC1"]
    standardized_values = bt.Gene.public().standardize(values)
    records = bt.Gene.from_values(standardized_values, bt.Gene.symbol)
    assert records[0].ensembl_gene_id == "ENSG00000068097"

    # TODO: Gene.public() should raise error if organism is not provided
    standardized_values = bt.Gene.public(organism="mouse").standardize(values)
    records = bt.Gene.from_values(standardized_values, bt.Gene.symbol, organism="mouse")
    assert records[0].ensembl_gene_id == "ENSMUSG00000015243"

    # clean up
    bt.settings._organism = None
    bt.Organism.filter().delete()
    bt.Gene.filter().delete()

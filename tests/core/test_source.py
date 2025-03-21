import bionty as bt
import pytest
from bionty._organism import OrganismNotSet


def test_add_source():
    import wetlab as wl

    with pytest.raises(ValueError):
        wl.Compound.import_source()
    chebi_source = bt.Source.get(name="chebi", version="2024-07-27")
    new_source = wl.Compound.add_source(chebi_source)
    assert new_source.entity == "wetlab.Compound"
    assert new_source.name == "chebi"
    assert new_source.version == "2024-07-27"
    assert new_source.dataframe_artifact is not None


def test_import_source():
    # when adding a single record, it's parents are also added
    record = bt.Ethnicity.from_source(ontology_id="HANCESTRO:0005").save()
    parent = bt.Ethnicity.get(ontology_id="HANCESTRO:0004")
    assert parent in record.parents.list()

    # bulk import should fill in gaps of missing parents
    parent.delete()
    bt.Ethnicity.import_source()
    parent = bt.Ethnicity.get(ontology_id="HANCESTRO:0004")
    assert parent in record.parents.list()
    record = bt.Ethnicity.get("7RNCY3yC")
    assert record.parents.all().one().name == "South East Asian"
    # the source.in_db should be set to True since we imported all the records
    assert record.source.in_db is True

    # organism is required
    bt.settings._organism = None
    with pytest.raises(OrganismNotSet):
        bt.CellMarker.import_source()
    bt.CellMarker.import_source(organism="mouse")
    assert bt.CellMarker.filter(organism__name="mouse").exists()

    # import source with stable_id
    bt.Gene.import_source(organism="saccharomyces cerevisiae")
    assert bt.Gene.filter(organism__name="saccharomyces cerevisiae").exists()

    # import source with public df having extra columns than model fields
    bt.CellLine.import_source(source=bt.Source.get(name="depmap", version="2024-Q2"))
    assert bt.CellLine.filter(source__name="depmap").count() == 1959


def test_add_ontology_from_values():
    bt.Ethnicity.filter().delete()
    # .save() calls add_ontology() under the hood
    bt.Ethnicity.from_values(
        [
            "HANCESTRO:0597",
            "HANCESTRO:0006",
        ],
        field=bt.Ethnicity.ontology_id,
    ).save()
    record = bt.Ethnicity.get("7RNCY3yC")
    assert record.parents.all().one().name == "South East Asian"
    # the source.in_db should be set back to False since we deleted all records
    assert record.source.in_db is False


def test_sync_public_sources():
    bt.Source.get(name="ensembl", version="release-112", organism="mouse").delete()
    source_gene_release_111 = bt.Source.get(
        name="ensembl", version="release-111", organism="mouse"
    )
    source_gene_release_111.currently_used = True
    source_gene_release_111.save()
    bt.Source.get(name="cl", version="2024-08-16").delete()
    source_ct_2024_05_15 = bt.Source.get(name="cl", version="2024-05-15")
    source_ct_2024_05_15.currently_used = True
    source_ct_2024_05_15.save()

    # update_currently_used=False
    bt.core.sync_public_sources()
    source_gene_release_112 = bt.Source.get(
        name="ensembl", version="release-112", organism="mouse"
    )
    assert not source_gene_release_112.currently_used
    assert source_gene_release_111.currently_used
    source_ct_2024_08_16 = bt.Source.get(name="cl", version="2024-08-16")
    assert not source_ct_2024_08_16.currently_used
    assert source_ct_2024_05_15.currently_used

    # update_currently_used=True
    bt.core.sync_public_sources(update_currently_used=True)
    source_gene_release_112 = bt.Source.filter(
        name="ensembl", version="release-112", organism="mouse"
    ).one_or_none()
    source_gene_release_111 = bt.Source.filter(
        name="ensembl", version="release-111", organism="mouse"
    ).one_or_none()
    assert source_gene_release_112.currently_used
    assert not source_gene_release_111.currently_used

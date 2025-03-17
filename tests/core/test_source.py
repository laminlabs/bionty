import bionty as bt


def test_add_source():
    chebi_source = bt.Source.get(name="chebi", version="2024-07-27")
    new_source = bt.Phenotype.add_source(chebi_source)
    assert new_source.name == "chebi"
    assert new_source.version == "2024-07-27"
    assert new_source.dataframe_artifact is not None


def test_import_source():
    record = bt.Ethnicity.from_source(ontology_id="HANCESTRO:0005").save()
    parent = bt.Ethnicity.get(ontology_id="HANCESTRO:0004")
    assert parent in record.parents.list()
    parent.delete()

    bt.Ethnicity.import_source()
    parent = bt.Ethnicity.get(ontology_id="HANCESTRO:0004")
    assert parent in record.parents.list()
    record = bt.Ethnicity.get("7RNCY3yC")
    assert record.parents.all().one().name == "South East Asian"
    # the source.in_db should be set to True since we imported all the records
    assert record.source.in_db is True


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

import bionty as bt
import pandas as pd
import pytest
from bionty._organism import OrganismNotSet
from bionty.models import DoesNotExist, InvalidArgument


def test_from_source():
    # test passing organism
    record = bt.Gene.from_source(symbol="BRCA2", organism="human")
    assert record.ensembl_gene_id == "ENSG00000139618"

    # name is not found
    with pytest.raises(
        DoesNotExist,
        match=r"no CellType found in source for the given field value: name='T-cellx'",
    ):
        bt.CellType.from_source(name="T-cellx")

    # multiple fields passed
    with pytest.raises(
        InvalidArgument,
        match=r"Only one field can be passed to generate records from source",
    ):
        bt.CellType.from_source(name="T cell", ontology_id="CL:0000084")

    # no field passed
    with pytest.raises(
        InvalidArgument, match=r"No field passed to generate records from source"
    ):
        bt.CellType.from_source()

    # passing a synonym via name= doesn't work
    with pytest.raises(
        DoesNotExist,
        match=r"no CellType found in source for the given field value: name='T-cell'",
    ):
        bt.CellType.from_source(name="T-cell")

    # passing a synonym as positional argument works
    bt.CellType.from_source("T-cell")


def test_get_source_record():
    from bionty._source import get_source_record

    source = get_source_record(bt.Phenotype, organism="human")
    assert source.organism == "human"

    source = get_source_record(bt.Phenotype)
    assert source.organism == "all"

    source = get_source_record(bt.Gene, organism="mouse")
    assert source.organism == "mouse"


def test_add_source():
    import wetlab as wl

    # pass a source record from another entity
    with pytest.raises(ValueError):
        wl.Compound.import_source()
    chebi_source = bt.Source.get(name="chebi", version="2024-07-27")
    new_source = wl.Compound.add_source(chebi_source)
    assert new_source.entity == "wetlab.Compound"
    assert new_source.name == "chebi"
    assert new_source.version == "2024-07-27"
    assert new_source.dataframe_artifact is not None
    public_ontology = wl.Compound.public()
    assert public_ontology.__class__.__name__ == "StaticReference"

    # pass a PublicOntology object
    public_ontology_ct_2024_05_15 = bt.base.CellType(source="cl", version="2024-05-15")
    new_source = bt.CellType.add_source(public_ontology_ct_2024_05_15)
    assert new_source.entity == "bionty.CellType"
    assert new_source.name == "cl"
    assert new_source.version == "2024-05-15"
    assert new_source.dataframe_artifact is not None

    # pass a source name and/ or version
    new_source = bt.Phenotype.add_source("oba")
    assert new_source.entity == "bionty.Phenotype"
    assert new_source.name == "oba"
    assert bt.Phenotype.add_source("oba", version=new_source.version) == new_source
    public_df = bt.Phenotype.public(source=new_source).to_dataframe()
    assert all(public_df.index.str.startswith("OBA:"))  # restrict_to_prefix


def test_base_gene_register_source_in_lamindb():
    bt.Organism.filter().delete(permanent=True)
    assert not bt.Source.filter(organism="rabbit").exists()
    gene = bt.base.Gene(source="ensembl", organism="rabbit", version="release-112")
    assert gene.to_dataframe().shape[0] > 10000
    gene.register_source_in_lamindb()
    assert bt.Organism.filter(name="rabbit").exists()
    rabbit_gene_source = bt.Source.get(organism="rabbit")
    assert rabbit_gene_source.entity == "bionty.Gene"
    assert rabbit_gene_source.name == "ensembl"
    assert rabbit_gene_source.version == "release-112"
    assert rabbit_gene_source.organism == "rabbit"


def test_import_source():
    # when adding a single record, it's parents are also added
    record = bt.Ethnicity.from_source(ontology_id="HANCESTRO:0005").save()
    parent = bt.Ethnicity.get(ontology_id="HANCESTRO:0004")
    assert parent in record.parents.filter().to_list()

    # bulk import should fill in gaps of missing parents
    parent.delete(permanent=True)
    bt.Ethnicity.import_source()
    parent = bt.Ethnicity.get(ontology_id="HANCESTRO:0004")
    assert parent in record.parents.filter().to_list()
    record = bt.Ethnicity.get("7RNCY3yC")
    assert record.parents.count() > 0
    # the source.in_db should be set to True since we imported all the records
    assert record.source.in_db is True

    # organism is required
    bt.settings._organism = None
    with pytest.raises(
        OrganismNotSet,
        match=r"CellMarker requires to specify a organism name via `organism=` or `bionty\.settings\.organism=`!",
    ):
        bt.CellMarker.import_source()
    bt.CellMarker.import_source(organism="mouse")
    assert bt.CellMarker.filter(organism__name="mouse").exists()

    # import source with stable_id
    bt.Gene.import_source(organism="saccharomyces cerevisiae")
    assert bt.Gene.filter(organism__name="saccharomyces cerevisiae").exists()

    # import organism data without 'parents' column (should not crash with KeyError)
    bt.Organism.import_source()
    assert bt.Organism.filter().count() > 0

    # strings are not supported (only Sources) and should raise a TypeError
    with pytest.raises(
        TypeError, match=r"import_source\(\) expects a `bt\.Source` object, not a str"
    ):
        bt.CellLine.import_source(source="depmap")

    # test that ICD Source does not crash
    source = bt.Disease.add_source(source="icd", version="icd-11-2023")
    bt.Disease.import_source(source=source)

    # import source with public df having extra columns than model fields
    bt.CellLine.import_source(source=bt.Source.get(name="depmap", version="2024-Q2"))
    assert bt.CellLine.filter(source__name="depmap").count() == 1959


def test_add_ontology_from_values():
    bt.Ethnicity.filter().delete(permanent=True)
    # .save() calls add_ontology() under the hood
    bt.Ethnicity.from_values(
        [
            "HANCESTRO:0597",
            "HANCESTRO:0006",
        ],
        field=bt.Ethnicity.ontology_id,
    ).save()
    record = bt.Ethnicity.get("7RNCY3yC")
    assert record.parents.count() > 0
    # the source.in_db should be set back to False since we deleted all records
    assert record.source.in_db is False


def test_add_custom_source():
    internal_source = bt.Source(
        entity="bionty.Gene",
        name="internal",
        version="0.0.1",
        organism="rabbit",
        description="internal gene reference",
    ).save()

    # without a dataframe artifact
    assert bt.Gene.public(source=bt.Source.get(name="internal")).to_dataframe().empty
    records = bt.Gene.from_values(
        ["ENSOCUG00000017195"],
        field=bt.Gene.ensembl_gene_id,
        source=internal_source,
    )
    assert len(records) == 0

    # with a dataframe artifact
    df = pd.DataFrame(
        {
            "ensembl_gene_id": ["ENSOCUG00000017195"],
            "symbol": ["SEL1L3"],
            "description": ["SEL1L family member 3"],
        }
    )
    internal_source = bt.Gene.add_source(internal_source, df=df)
    records = bt.Gene.from_values(
        ["ENSOCUG00000017195"],
        field=bt.Gene.ensembl_gene_id,
        source=internal_source,
    )
    assert len(records) == 1


def test_sync_public_sources():
    source_gene_latest = bt.Source.get(
        entity="bionty.Gene", name="ensembl", organism="mouse", currently_used=True
    )
    source_gene_release_111 = bt.Gene.add_source(
        source="ensembl", organism="mouse", version="release-111"
    )
    source_gene_release_111.currently_used = True
    # .save() updates currently_used of others to False
    source_gene_release_111.save()
    assert not bt.Source.get(source_gene_latest.uid).currently_used

    bt.Source.get(entity="bionty.CellType", name="cl", currently_used=True).delete(
        permanent=True
    )
    source_ct_2024_05_15 = bt.CellType.add_source(source="cl", version="2024-05-15")
    source_ct_2024_05_15.currently_used = True
    source_ct_2024_05_15.save()

    # update_currently_used=False
    source_gene_latest.delete(permanent=True)
    bt.core.sync_public_sources()
    source_gene_latest = bt.Source.get(
        entity="bionty.Gene", name="ensembl", organism="mouse", currently_used=True
    )
    assert source_gene_latest == source_gene_release_111
    source_cl_latest = bt.Source.get(
        entity="bionty.CellType", name="cl", currently_used=True
    )
    assert source_cl_latest == source_ct_2024_05_15

    # update_currently_used=True
    bt.core.sync_public_sources(update_currently_used=True)
    source_gene_latest = bt.Source.get(
        entity="bionty.Gene", name="ensembl", organism="mouse", currently_used=True
    )
    assert source_gene_latest != source_gene_release_111
    source_cl_latest = bt.Source.get(
        entity="bionty.CellType", name="cl", currently_used=True
    )
    assert source_cl_latest != source_ct_2024_05_15


def test_import_source_update_records():
    import lamindb as ln

    source1 = bt.CellType.add_source(source="cl", version="2022-08-16")
    source2 = bt.CellType.add_source(source="cl", version="2024-08-16")
    bt.CellType.import_source(source=source1)

    artifact = ln.Artifact(
        pd.DataFrame({"a": [1, 2, 3]}), key="test-upgrade-labels.parquet"
    ).save()
    record_wo_artifact_name = bt.CellType.get(ontology_id="CL:0000409").name
    record_w_artifact = bt.CellType.get(ontology_id="CL:0000003")
    artifact.cell_types.add(record_w_artifact)

    # records with artifacts should not be upgraded
    bt.CellType.import_source(source=source2, update_records=True)
    record_w_artifact = bt.CellType.get(ontology_id="CL:0000003")
    assert record_w_artifact.source == source1

    # records without artifacts should be upgraded
    record_wo_artifact = bt.CellType.get(ontology_id="CL:0000409")
    assert record_wo_artifact.source == source2
    assert record_wo_artifact.name != record_wo_artifact_name


def test_import_source_no_prefix_filter():
    efo_public = bt.base.ExperimentalFactor(version="3.78.0")
    efo_ontology_df = efo_public.to_pronto().to_df(include_id_prefixes=None)
    assert efo_ontology_df.shape[0] == 66971
    assert efo_ontology_df.index.str.startswith("EFO:").sum() == 18229
    source = bt.ExperimentalFactor.add_source(source="efo", df=efo_ontology_df)
    bt.ExperimentalFactor.import_source(source=source)
    assert bt.ExperimentalFactor.filter().count() == 66971

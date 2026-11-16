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
    import pertdb

    # pass a source record from another entity
    with pytest.raises(ValueError):
        pertdb.Compound.import_source()
    chebi_source = bt.Source.get(name="chebi", version="2026-09-01")
    new_source = pertdb.Compound.add_source(chebi_source)
    assert new_source.entity == "pertdb.Compound"
    assert new_source.name == "chebi"
    assert new_source.version == "2026-09-01"
    assert new_source.dataframe_artifact is not None
    public_ontology = pertdb.Compound.public()
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


def test_display_currently_used_sources_detects_instance(caplog):
    from lamindb_setup import logger

    # the lamindb-setup logger doesn't propagate to the root logger
    logger.addHandler(caplog.handler)
    try:
        bt.base.display_currently_used_sources()
    finally:
        logger.removeHandler(caplog.handler)
    # the test instance is resolved through a dev-dir marker
    assert "You have a LaminDB instance loaded" in caplog.text


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
    assert bt.settings.organism is None
    with pytest.raises(
        OrganismNotSet,
        match=r"`organism` is required to get Source record for CellMarker!",
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


def test_static_reference_does_not_look_up_its_source_online(monkeypatch):
    import socket

    from bionty.core import StaticReference

    df = pd.DataFrame(
        {
            "name": ["custom cell"],
            "definition": [None],
            "synonyms": ["cc"],
            "parents": [["CL:0000000"]],
        },
        index=pd.Index(["CUSTOMCL:0000001"], name="ontology_id"),
    )
    source = bt.Source(
        entity="bionty.CellType", organism="all", name="customcl", version="1"
    )
    source = bt.CellType.add_source(source=source, df=df)

    hosts = []

    def getaddrinfo(host, *args, **kwargs):
        hosts.append(host)
        raise OSError("offline")

    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)
    public = bt.CellType.public(source=source)
    assert isinstance(public, StaticReference)
    assert hosts == []
    assert "Entity: bionty.CellType" in repr(public)
    assert (public.source, public.version, public.organism) == ("customcl", "1", "all")
    assert public.to_dataframe().index.tolist() == ["CUSTOMCL:0000001"]
    monkeypatch.undo()

    artifact = source.dataframe_artifact
    source.delete(permanent=True)
    artifact.delete(permanent=True)


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


def _ontology_frame(
    ontology_ids: list[str],
    *,
    string_na: bool,
    synonyms: list[str | None] | None = None,
    description: list[str | None] | None = None,
) -> pd.DataFrame:
    """Build a custom CellType frame, optionally with pandas 3 string NA."""
    import numpy as np

    synonyms = ["a1|a2", None] if synonyms is None else synonyms
    description = [None, "has a description"] if description is None else description
    synonym_values = pd.Series(synonyms)
    description_values = pd.Series(description)
    if string_na:
        dtype = pd.StringDtype(na_value=np.nan)
        synonym_values = synonym_values.astype(dtype)
        description_values = description_values.astype(dtype)
    return pd.DataFrame(
        {
            "ontology_id": ontology_ids,
            "name": ["cell a", "cell b"],
            "synonyms": synonym_values,
            "description": description_values,
            "parents": [[], [ontology_ids[0]]],
        }
    )


def _text_rows(source: bt.Source, ontology_ids: list[str]) -> list[tuple]:
    return list(
        bt.CellType.filter(source=source, ontology_id__in=ontology_ids)
        .order_by("ontology_id")
        .values_list("ontology_id", "synonyms", "description")
    )


def _assert_missing_text_is_null(source: bt.Source, ontology_ids: list[str]) -> None:
    assert _text_rows(source, ontology_ids) == [
        (ontology_ids[0], "a1|a2", None),
        (ontology_ids[1], None, "has a description"),
    ]
    child = bt.CellType.get(ontology_id=ontology_ids[1], source=source)
    parent = bt.CellType.get(ontology_id=ontology_ids[0], source=source)
    assert parent in child.parents.filter().to_list()


def test_missing_ontology_text_is_not_persisted_as_nan(monkeypatch):
    # Pandas 3 string columns use NaN as the missing sentinel. Record
    # construction has to persist that as NULL, for both the pandas 2 object
    # dtype and the pandas 3 string dtype, without touching parent lists.
    import lamindb as ln
    from bionty.core._add_ontology import create_records

    cases = [
        ("pandas2", False, ["CL:9100001", "CL:9100002"]),
        ("pandas3", True, ["CL:9200001", "CL:9200002"]),
    ]
    for label, string_na, ontology_ids in cases:
        frame = _ontology_frame(ontology_ids, string_na=string_na)
        source = bt.Source(
            entity="bionty.CellType",
            name=f"mycl-na-{label}",
            organism="all",
            version="1",
            currently_used=False,
            description=None,
            url=None,
            md5=None,
            source_website=None,
        ).save()
        ln.save(create_records(bt.CellType, frame.set_index("ontology_id"), source))
        assert _text_rows(source, ontology_ids) == [
            (ontology_ids[0], "a1|a2", None),
            (ontology_ids[1], None, "has a description"),
        ]
        # create_records drops parents; links are created by from_values below.
        bt.CellType.filter(ontology_id__in=ontology_ids).delete(permanent=True)

        # Store an object-dtype frame so the public reference can be read back,
        # then force the pandas 3 string-NA frame into record kwargs. Parquet
        # roundtrip on pandas 2 turns those NA values into None before bionty
        # sees them, which hides the bug.
        source = bt.CellType.add_source(
            source, df=_ontology_frame(ontology_ids, string_na=False)
        )
        if string_na:
            monkeypatch.setattr(
                "bionty._source.filter_public_df_columns",
                lambda registry, public_ontology, frame=frame: frame.copy(),
            )
        bt.CellType.from_values(
            ontology_ids,
            field=bt.CellType.ontology_id,
            source=source,
            mute=True,
        ).save()
        _assert_missing_text_is_null(source, ontology_ids)

    # Source upgrade assigns dataframe values onto existing records.
    ontology_ids = ["CL:9200001", "CL:9200002"]
    source = bt.Source.get(name="mycl-na-pandas3", version="1")
    artifact = ln.Artifact(
        pd.DataFrame({"a": [1]}), key="test-missing-na-upgrade.parquet"
    ).save()
    artifact.cell_types.add(bt.CellType.get(ontology_id=ontology_ids[0], source=source))
    upgraded = _ontology_frame(
        ontology_ids,
        string_na=True,
        synonyms=[None, "b-syn"],
        description=["now described", None],
    )
    source2 = bt.Source(
        entity="bionty.CellType",
        name="mycl-na-pandas3",
        organism="all",
        version="2",
        currently_used=False,
        description=None,
        url=None,
        md5=None,
        source_website=None,
    )
    source2 = bt.CellType.add_source(
        source2, df=_ontology_frame(ontology_ids, string_na=False)
    )
    monkeypatch.setattr(
        "bionty._source.filter_public_df_columns",
        lambda registry, public_ontology, frame=upgraded: frame.copy(),
    )
    bt.CellType.import_source(source=source2, update_records=True)
    upgraded_rows = list(
        bt.CellType.filter(ontology_id__in=ontology_ids)
        .order_by("ontology_id")
        .values_list("ontology_id", "synonyms", "description", "source_id")
    )
    assert upgraded_rows == [
        (ontology_ids[0], None, "now described", source2.id),
        (ontology_ids[1], "b-syn", None, source2.id),
    ]


def test_import_source_no_prefix_filter():
    efo_public = bt.base.ExperimentalFactor(version="3.78.0")
    efo_ontology_df = efo_public.to_pronto().to_df(include_id_prefixes=None)
    assert efo_ontology_df.shape[0] == 66971
    assert efo_ontology_df.index.str.startswith("EFO:").sum() == 18229
    source = bt.ExperimentalFactor.add_source(source="efo", df=efo_ontology_df)
    bt.ExperimentalFactor.import_source(source=source)
    assert bt.ExperimentalFactor.filter().count() == 66971

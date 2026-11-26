import bionty as bt
import pandas as pd
import pytest
from bionty._organism import OrganismNotSet
from lamindb.errors import DoesNotExist, InvalidArgument


def test_from_values_organism():
    bt.settings._organism = None
    with pytest.raises(OrganismNotSet):
        bt.Gene.from_values(["ABC1"], bt.Gene.symbol)
    # no organism is needed if the values are ensembl gene ids
    result = bt.Gene.from_values(["ENSG00000068097"], bt.Gene.ensembl_gene_id)
    assert len(result) == 1
    result = bt.Gene.from_values(
        ["ENSMUSG00000102862", "ENSMUSG00000000003"], field=bt.Gene.ensembl_gene_id
    )
    assert len(result) == 2

    result = bt.Gene.from_values(
        ["HRA1", "ETS1-1"], field=bt.Gene.stable_id, organism="saccharomyces cerevisiae"
    )
    assert len(result) == 2

    # test global organism setting
    bt.settings.organism = "human"
    values = ["ABC1"]
    standardized_values = bt.Gene.public().standardize(values)
    records = bt.Gene.from_values(standardized_values, bt.Gene.symbol)
    assert records[0].ensembl_gene_id in ("ENSG00000068097", "ENSG00000165029")
    bt.settings._organism = None

    # Gene.public() should raise error if organism is not provided
    with pytest.raises(OrganismNotSet):
        bt.Gene.public().standardize(values)
    standardized_values = bt.Gene.public(organism="mouse").standardize(values)
    records = bt.Gene.from_values(standardized_values, bt.Gene.symbol, organism="mouse")
    assert records[0].ensembl_gene_id == "ENSMUSG00000015243"

    # clean up
    bt.Gene.filter().delete(permanent=True)
    bt.Organism.filter().delete(permanent=True)


def test_organism_all():
    assert bt.CellLine.public(organism="all")


def test_infer_organism_from_ensembl_id():
    from bionty._organism import infer_organism_from_ensembl_id

    # Test with a rat Ensembl ID, which has duplicate entries in the ensembl_prefixes parquet
    # (e.g., "ENSRNOG") and would return a Series from .loc if not handled correctly.
    organism_source = bt.Source.get(name="ncbitaxon")
    bt.Organism.from_source(
        ontology_id="NCBITaxon:10116", source=organism_source
    ).save()
    organism = infer_organism_from_ensembl_id("ENSRNOG00000001284")
    assert organism is not None
    # Common names change across Ensembl/NCBITaxon versions; ontology_id does not.
    assert organism.ontology_id == "NCBITaxon:10116"


def test_pass_scientific_name_as_organism():
    bt.Organism.filter().delete(permanent=True)
    # check organism rat doesn't yet exist in the database
    assert bt.Organism.filter(scientific_name="Rattus norvegicus").one_or_none() is None
    # registering a protein with organism rat should also register the organism
    protein = bt.Protein.from_source(
        uniprotkb_id="B4F769", organism="Rattus norvegicus"
    )
    assert protein is not None
    assert protein.organism.scientific_name == "Rattus norvegicus"
    assert bt.Protein.from_source(
        uniprotkb_id="B4F769",
        organism=bt.Organism.get(scientific_name="Rattus norvegicus"),
    )


def test_protein_from_source_uniprotkb_id_without_organism():
    bt.settings._organism = None
    bt.Protein.filter().delete(permanent=True)
    bt.Organism.filter().delete(permanent=True)
    try:
        human_protein = bt.Protein.from_source(uniprotkb_id="P01112")
        assert human_protein.uniprotkb_id == "P01112"
        assert human_protein.name == "GTPase HRas"
        assert human_protein.gene_symbol == "HRAS"
        assert human_protein.organism.name == "human"
        assert human_protein.source.organism == "human"

        # Mouse HRas (Q61411): must resolve to mouse without creating human in DB
        bt.Organism.filter().delete(permanent=True)
        mouse_protein = bt.Protein.from_source(uniprotkb_id="Q61411")
        assert mouse_protein.uniprotkb_id == "Q61411"
        assert mouse_protein.name == "GTPase HRas"
        assert mouse_protein.gene_symbol == "Hras"
        assert mouse_protein.organism.name == "mouse"
        assert mouse_protein.source.organism == "mouse"
        assert bt.Organism.filter(name="human").one_or_none() is None

        # Rat protein (source.organism == "rattus norvegicus", lowercase scientific name)
        bt.Organism.filter().delete(permanent=True)
        rat_protein = bt.Protein.from_source(uniprotkb_id="B4F769")
        assert rat_protein.uniprotkb_id == "B4F769"
        assert rat_protein.organism.scientific_name == "Rattus norvegicus"
        assert rat_protein.source.organism == "rattus norvegicus"
        assert bt.Organism.filter(name="human").one_or_none() is None
        assert bt.Organism.filter(name="mouse").one_or_none() is None
    finally:
        bt.settings._organism = None
        bt.Protein.filter().delete(permanent=True)
        bt.Organism.filter().delete(permanent=True)


def test_protein_from_source_uniprotkb_id_with_different_settings_organism():
    bt.settings._organism = None
    bt.Protein.filter().delete(permanent=True)
    bt.Organism.filter().delete(permanent=True)
    try:
        bt.settings.organism = "mouse"
        human_protein = bt.Protein.from_source(uniprotkb_id="P01112")
        assert human_protein.uniprotkb_id == "P01112"
        assert human_protein.gene_symbol == "HRAS"
        assert human_protein.organism.name == "human"
        assert human_protein.source.organism == "human"
        assert bt.settings.organism.name == "mouse"

        mouse_protein = bt.Protein.from_source(uniprotkb_id="Q61411")
        assert mouse_protein.uniprotkb_id == "Q61411"
        assert mouse_protein.gene_symbol == "Hras"
        assert mouse_protein.organism.name == "mouse"
        assert mouse_protein.source.organism == "mouse"

        bt.settings.organism = "human"
        mouse_protein_2 = bt.Protein.from_source(uniprotkb_id="Q61411")
        assert mouse_protein_2.organism.name == "mouse"
        assert mouse_protein_2.source.organism == "mouse"
        assert bt.settings.organism.name == "human"
    finally:
        bt.settings._organism = None
        bt.Protein.filter().delete(permanent=True)
        bt.Organism.filter().delete(permanent=True)


def test_protein_from_source_uniprotkb_id_explicit_organism_and_source():
    bt.settings._organism = None
    bt.Protein.filter().delete(permanent=True)
    bt.Organism.filter().delete(permanent=True)
    try:
        human_src = bt.Source.get(
            entity="bionty.Protein", organism="human", currently_used=True
        )
        mouse_src = bt.Source.get(
            entity="bionty.Protein", organism="mouse", currently_used=True
        )

        # Explicit matching organism
        p_human = bt.Protein.from_source(uniprotkb_id="P01112", organism="human")
        assert p_human.organism.name == "human"
        assert p_human.source == human_src

        # Explicit mismatched organism before save -> DoesNotExist
        with pytest.raises(DoesNotExist):
            bt.Protein.from_source(uniprotkb_id="P01112", organism="mouse")

        # Invalid explicit organism -> OrganismNotSet (must not fall back across sources)
        with pytest.raises(OrganismNotSet):
            bt.Protein.from_source(
                uniprotkb_id="P01112", organism="nonexistent_organism_xyz"
            )

        # Save human record and verify DB lookup behavior
        saved = p_human.save()
        again = bt.Protein.from_source(uniprotkb_id="P01112")
        assert again.id == saved.id
        assert again.uid == saved.uid
        assert again.organism.name == "human"
        assert bt.Protein.filter(uniprotkb_id="P01112").count() == 1

        # Existing human record returned even when settings.organism is mouse
        bt.settings.organism = "mouse"
        again_diff_settings = bt.Protein.from_source(uniprotkb_id="P01112")
        assert again_diff_settings.id == saved.id
        assert again_diff_settings.organism.name == "human"
        bt.settings._organism = None

        # Explicit mismatched organism after save -> STILL DoesNotExist
        with pytest.raises(DoesNotExist):
            bt.Protein.from_source(uniprotkb_id="P01112", organism="mouse")

        # Delete saved protein to test fresh creation with explicit source=
        saved.delete(permanent=True)

        # Explicit source with settings.organism = None
        p_from_src = bt.Protein.from_source(uniprotkb_id="P01112", source=human_src)
        assert p_from_src.organism.name == "human"
        assert p_from_src.source == human_src

        # Explicit source with conflicting settings.organism = "mouse" -> must NOT corrupt
        bt.settings.organism = "mouse"
        p_from_src_diff = bt.Protein.from_source(
            uniprotkb_id="P01112", source=human_src
        )
        assert p_from_src_diff.organism.name == "human"
        assert p_from_src_diff.source == human_src
        bt.settings._organism = None

        # Explicit mismatched source -> DoesNotExist (must not scan other sources)
        with pytest.raises(DoesNotExist):
            bt.Protein.from_source(uniprotkb_id="P01112", source=mouse_src)

        # Conflicting explicit source + organism -> InvalidArgument
        with pytest.raises(InvalidArgument, match="does not match source organism"):
            bt.Protein.from_source(
                uniprotkb_id="P01112", organism="mouse", source=human_src
            )
    finally:
        bt.settings._organism = None
        bt.Protein.filter().delete(permanent=True)
        bt.Organism.filter().delete(permanent=True)


def test_protein_from_source_uniprotkb_id_unknown_and_non_unique_fields():
    bt.settings._organism = None
    bt.Protein.filter().delete(permanent=True)
    bt.Organism.filter().delete(permanent=True)
    try:
        # Unknown uniprotkb_id -> DoesNotExist (not OrganismNotSet) and no Organism side effects
        with pytest.raises(
            DoesNotExist,
            match=r"no Protein found in source for the given field value: uniprotkb_id='INVALID_999999'",
        ):
            bt.Protein.from_source(uniprotkb_id="INVALID_999999")
        assert bt.Organism.filter().count() == 0

        # Empty string -> DoesNotExist
        with pytest.raises(DoesNotExist):
            bt.Protein.from_source(uniprotkb_id="")

        # Non-unique fields without organism MUST still raise OrganismNotSet
        with pytest.raises(OrganismNotSet):
            bt.Protein.from_source(name="GTPase HRas")
        with pytest.raises(OrganismNotSet):
            bt.Protein.from_source(gene_symbol="HRAS")

        # Even after saving P01112, non-unique fields without organism MUST still raise
        bt.Protein.from_source(uniprotkb_id="P01112", mute=True).save()
        with pytest.raises(OrganismNotSet):
            bt.Protein.from_source(name="GTPase HRas")
        with pytest.raises(OrganismNotSet):
            bt.Protein.from_source(gene_symbol="HRAS")

        # Multiple fields alongside uniprotkb_id -> InvalidArgument
        with pytest.raises(
            InvalidArgument,
            match=r"Only one field can be passed to generate records from source",
        ):
            bt.Protein.from_source(uniprotkb_id="P01112", gene_symbol="HRAS")
        with pytest.raises(
            InvalidArgument,
            match=r"Only one field can be passed to generate records from source",
        ):
            bt.Protein.from_source(uniprotkb_id="P01112", gene_symbol="WRONG")
    finally:
        bt.settings._organism = None
        bt.Protein.filter().delete(permanent=True)
        bt.Organism.filter().delete(permanent=True)


def test_protein_from_source_uniprotkb_id_custom_static_sources():
    import lamindb as ln

    bt.settings._organism = None
    bt.Protein.filter().delete(permanent=True)
    bt.Organism.filter().delete(permanent=True)
    created_sources = []
    created_artifacts = []
    created_organisms = []
    try:
        org_a = bt.Organism(name="synth_species_a", _skip_validation=True).save()
        org_b = bt.Organism(name="synth_species_b", _skip_validation=True).save()
        created_organisms.extend([org_a, org_b])

        df_a = pd.DataFrame(
            {
                "uniprotkb_id": ["ZSYNTH001"],
                "name": ["Synthetic Protein A"],
                "gene_symbol": ["SYNA"],
            }
        )
        art_a = ln.Artifact.from_dataframe(df_a, key="synth_prot_a.parquet").save()
        created_artifacts.append(art_a)
        src_a = bt.Source(
            entity="bionty.Protein",
            name="synth_uniprot",
            version="1.0",
            organism="synth_species_a",
            currently_used=True,
            dataframe_artifact=art_a,
        ).save()
        created_sources.append(src_a)

        # Fallback source (currently_used=False) for an organism with no currently_used=True source
        df_b = pd.DataFrame(
            {
                "uniprotkb_id": ["ZSYNTH002"],
                "name": ["Synthetic Protein B"],
                "gene_symbol": ["SYNB"],
            }
        )
        art_b = ln.Artifact.from_dataframe(df_b, key="synth_prot_b.parquet").save()
        created_artifacts.append(art_b)
        src_b = bt.Source(
            entity="bionty.Protein",
            name="synth_uniprot",
            version="1.0",
            organism="synth_species_b",
            currently_used=False,
            dataframe_artifact=art_b,
        ).save()
        created_sources.append(src_b)

        # Deprecated (currently_used=False) source for human (which already has currently_used=True)
        df_dep = pd.DataFrame(
            {
                "uniprotkb_id": ["ZRETIRED1"],
                "name": ["Retired Human Protein"],
                "gene_symbol": ["RET1"],
            }
        )
        art_dep = ln.Artifact.from_dataframe(
            df_dep, key="synth_prot_dep.parquet"
        ).save()
        created_artifacts.append(art_dep)
        src_dep = bt.Source(
            entity="bionty.Protein",
            name="uniprot",
            version="1999-01",
            organism="human",
            currently_used=False,
            dataframe_artifact=art_dep,
        ).save()
        created_sources.append(src_dep)

        # Empty custom source without artifact/url should be skipped gracefully
        src_empty = bt.Source(
            entity="bionty.Protein",
            name="empty_custom",
            version="0.1",
            organism="synth_species_empty",
            currently_used=True,
        ).save()
        created_sources.append(src_empty)

        p_a = bt.Protein.from_source(uniprotkb_id="ZSYNTH001")
        assert p_a.name == "Synthetic Protein A"
        assert p_a.organism == org_a
        assert p_a.source == src_a

        p_b = bt.Protein.from_source(uniprotkb_id="ZSYNTH002")
        assert p_b.name == "Synthetic Protein B"
        assert p_b.organism == org_b
        assert p_b.source == src_b

        # Deprecated human source is NOT searched by default
        with pytest.raises(DoesNotExist):
            bt.Protein.from_source(uniprotkb_id="ZRETIRED1")

        # Passing deprecated source explicitly DOES find it and attaches human organism
        p_dep = bt.Protein.from_source(uniprotkb_id="ZRETIRED1", source=src_dep)
        assert p_dep.name == "Retired Human Protein"
        assert p_dep.organism.name == "human"
        assert p_dep.source == src_dep
    finally:
        bt.settings._organism = None
        bt.Protein.filter().delete(permanent=True)
        for src in created_sources:
            src.delete(permanent=True)
        for art in created_artifacts:
            art.delete(permanent=True)
        bt.Organism.filter().delete(permanent=True)


@pytest.fixture
def empty_protein_lookup_db(monkeypatch):
    monkeypatch.setattr(bt.settings, "_organism", None)
    bt.Protein.filter().delete(permanent=True)
    bt.Organism.filter().delete(permanent=True)
    try:
        yield
    finally:
        bt.Protein.filter().delete(permanent=True)
        bt.Organism.filter().delete(permanent=True)


@pytest.fixture
def stale_protein_cache(tmp_path, monkeypatch):
    import os
    import shutil

    from bionty.base import _public_ontology

    cache = tmp_path / "cache"
    cache.mkdir()
    human_source = bt.Source.get(
        entity="bionty.Protein", organism="human", currently_used=True
    )
    filename, _ = _public_ontology.encode_filenames(
        organism=human_source.organism,
        name=human_source.name,
        version=human_source.version,
        entity=human_source.entity,
    )
    stale = cache / filename
    upstream = tmp_path / "upstream.parquet"
    pd.DataFrame(
        {"uniprotkb_id": ["A0A024QYT4"], "name": ["Old cache entry"]}
    ).to_parquet(stale)
    pd.DataFrame({"uniprotkb_id": ["P01111"], "name": ["Refreshed entry"]}).to_parquet(
        upstream
    )
    os.utime(stale, (1, 1))
    original_cache = bt.base.settings.dynamicdir
    monkeypatch.setattr(bt.base.settings, "dynamicdir", cache)
    refreshes = []

    def sync_assets(filename, localpath, assets_base_url):
        if localpath == stale:
            if localpath.stat().st_mtime < upstream.stat().st_mtime:
                shutil.copy2(upstream, localpath)
                refreshes.append(localpath)
        elif filename.endswith("__Protein.parquet"):
            pd.DataFrame({"uniprotkb_id": [], "name": []}).to_parquet(localpath)
        else:
            shutil.copy2(original_cache / filename, localpath)
        return localpath

    monkeypatch.setattr(_public_ontology, "s3_bionty_assets", sync_assets)
    return stale, refreshes


@pytest.mark.usefixtures("empty_protein_lookup_db")
def test_protein_from_source_stale_negative(stale_protein_cache):
    cached_parquet, refreshes = stale_protein_cache
    assert pd.read_parquet(cached_parquet)["uniprotkb_id"].tolist() == ["A0A024QYT4"]

    protein = bt.Protein.from_source(uniprotkb_id="P01111")

    assert refreshes == [cached_parquet]
    assert protein.uniprotkb_id == "P01111"
    assert protein.name == "Refreshed entry"
    assert protein.organism.name == "human"
    assert bt.Organism.filter().count() == 1
    assert bt.Protein.filter().count() == 0


@pytest.mark.usefixtures("empty_protein_lookup_db")
def test_protein_from_source_stale_positive(stale_protein_cache):
    cached_parquet, refreshes = stale_protein_cache
    assert pd.read_parquet(cached_parquet)["uniprotkb_id"].tolist() == ["A0A024QYT4"]

    with pytest.raises(DoesNotExist):
        bt.Protein.from_source(uniprotkb_id="A0A024QYT4")

    assert refreshes == [cached_parquet]
    assert pd.read_parquet(cached_parquet)["uniprotkb_id"].tolist() == ["P01111"]
    assert bt.Protein.filter().count() == 0
    assert bt.Organism.filter().count() == 0


@pytest.mark.usefixtures("empty_protein_lookup_db")
def test_protein_from_source_conflicting_organism_does_not_write():
    mouse_source = bt.Source.get(
        entity="bionty.Protein", organism="mouse", currently_used=True
    )
    assert bt.Organism.filter().count() == 0

    with pytest.raises(InvalidArgument, match="does not match source organism"):
        bt.Protein.from_source(
            uniprotkb_id="P01112", organism="human", source=mouse_source
        )

    assert bt.Protein.filter().count() == 0
    assert bt.Organism.filter().count() == 0


@pytest.mark.usefixtures("empty_protein_lookup_db")
def test_protein_from_source_conflicting_organism_record_does_not_write():
    mouse_source = bt.Source.get(
        entity="bionty.Protein", organism="mouse", currently_used=True
    )
    human = bt.Organism.from_source(name="human", mute=True)

    with pytest.raises(InvalidArgument, match="does not match source organism"):
        bt.Protein.from_source(
            uniprotkb_id="P01112", organism=human, source=mouse_source
        )

    assert bt.Organism.filter().count() == 0
    assert bt.Protein.filter().count() == 0


@pytest.mark.usefixtures("empty_protein_lookup_db")
def test_protein_from_source_missing_after_source_match(
    stale_protein_cache, monkeypatch
):
    from lamindb.models import _from_values

    original_create = _from_values.create_records_from_source
    construction_attempts = []

    def miss_during_construction(values, *, field, **kwargs):
        if field is bt.Protein.uniprotkb_id:
            assert bt.Organism.filter().count() == 0
            construction_attempts.append(values.tolist())
            return [], values
        return original_create(values, field=field, **kwargs)

    monkeypatch.setattr(
        _from_values, "create_records_from_source", miss_during_construction
    )
    with pytest.raises(DoesNotExist):
        bt.Protein.from_source(uniprotkb_id="P01111")

    assert construction_attempts == [["P01111"]]
    assert bt.Organism.filter().count() == 0
    assert bt.Protein.filter().count() == 0


@pytest.mark.usefixtures("empty_protein_lookup_db")
def test_protein_from_source_organism_save_failure_rolls_back(
    stale_protein_cache, monkeypatch
):
    original_save = bt.Organism.save

    def fail_after_save(organism, *args, **kwargs):
        original_save(organism, *args, **kwargs)
        raise RuntimeError("organism save failed")

    monkeypatch.setattr(bt.Organism, "save", fail_after_save)
    with pytest.raises(RuntimeError, match="organism save failed"):
        bt.Protein.from_source(uniprotkb_id="P01111")

    assert bt.Organism.filter().count() == 0
    assert bt.Protein.filter().count() == 0


@pytest.mark.usefixtures("empty_protein_lookup_db")
@pytest.mark.parametrize("organism", [None, "human"])
def test_protein_from_source_missing_with_explicit_source(organism):
    source = bt.Source.get(
        entity="bionty.Protein", organism="human", currently_used=True
    )

    with pytest.raises(DoesNotExist):
        bt.Protein.from_source(
            uniprotkb_id="INVALID_999999", organism=organism, source=source
        )

    assert bt.Organism.filter().count() == 0
    assert bt.Protein.filter().count() == 0


@pytest.mark.usefixtures("empty_protein_lookup_db")
@pytest.mark.parametrize(
    ("organism", "source_organism", "accession", "scientific_name"),
    [
        ("human", "human", "P01112", "Homo sapiens"),
        ("Homo sapiens", "human", "P01112", "Homo sapiens"),
        ("rattus norvegicus", "rattus norvegicus", "B4F769", "Rattus norvegicus"),
        ("brown rat", "rattus norvegicus", "B4F769", "Rattus norvegicus"),
    ],
)
def test_protein_from_source_matching_organism_aliases(
    organism, source_organism, accession, scientific_name
):
    source = bt.Source.get(
        entity="bionty.Protein", organism=source_organism, currently_used=True
    )

    protein = bt.Protein.from_source(
        uniprotkb_id=accession, organism=organism, source=source
    )

    assert protein.uniprotkb_id == accession
    assert protein.organism.scientific_name == scientific_name
    assert protein.source == source
    assert bt.Organism.get(scientific_name=scientific_name) == protein.organism

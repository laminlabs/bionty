import os
import tempfile
from pathlib import Path

import pytest
from bionty.base._settings import settings
from bionty.base.dev._handle_sources import (
    add_records_to_existing_dict,
    parse_currently_used_sources,
    parse_sources_yaml,
    records_diff_btw_yamls,
    reset_sources,
    update_local_sources_yaml,
)
from bionty.base.dev._io import load_yaml, write_yaml


@pytest.fixture(scope="function")
def versions_yaml_replica():
    input_file_content = """
    version: "0.2.0"
    Organism:
      ensembl:
        all:
          release-108:
            url: https://ftp.ensembl.org/pub/release-108/species_EnsemblVertebrates.txt
        name: Ensembl
        website: https://www.ensembl.org/index.html
    Gene:
      ensembl:
        human:
          release-108:
            url: https://ftp.ensembl.org/pub/release-108/mysql/homo_sapiens_core_108_38/
          release-107:
            url: https://ftp.ensembl.org/pub/release-107/mysql/homo_sapiens_core_107_38/
        mouse:
          release-108:
            url: https://ftp.ensembl.org/pub/release-108/mysql/mus_musculus_core_108_39/
        name: Ensembl
        website: https://www.ensembl.org/index.html
    CellType:
      cl:
        name: Cell Ontology
        website: https://obophenotype.github.io/cell-ontology/
        all:
          2023-02-15:
            url: http://purl.obolibrary.org/obo/cl/releases/2023-02-15/cl-base.owl
            md5: 9331a6a029cb1863bd0584ab41508df7
          2022-08-16:
            url: http://purl.obolibrary.org/obo/cl/releases/2022-08-16/cl.owl
            md5: d0655766574e63f3fe5ed56d3c030880
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write(input_file_content)
        f.flush()
        yield f.name

    Path(f.name).unlink()


@pytest.fixture(scope="function")
def new_versions_yaml_replica():
    input_file_content = """
    version: "0.2.0"
    Organism:
      ensembl:
        all:
          release-108:
            url: https://ftp.ensembl.org/pub/release-108/species_EnsemblVertebrates.txt
        name: Ensembl
        website: https://www.ensembl.org/index.html
        new-organism:
          release-x:
            url: new-organism-source-link
    Gene:
      ensembl:
        human:
          release-108:
            url: https://ftp.ensembl.org/pub/release-108/mysql/homo_sapiens_core_108_38/
          release-107:
            url: https://ftp.ensembl.org/pub/release-107/mysql/homo_sapiens_core_107_38/
        mouse:
          release-108:
            url: https://ftp.ensembl.org/pub/release-108/mysql/mus_musculus_core_108_39/
        name: Ensembl
        website: https://www.ensembl.org/index.html
      new-source:
        human:
          release-x:
            url: new-gene-source-link
    CellType:
      cl:
        name: Cell Ontology
        website: https://obophenotype.github.io/cell-ontology/
        all:
          new-version:
            url: new-cell-type-source
            md5: new-md5
          2023-02-15:
            url: http://purl.obolibrary.org/obo/cl/releases/2023-02-15/cl-base.owl
            md5: 9331a6a029cb1863bd0584ab41508df7
          2022-08-16:
            url: http://purl.obolibrary.org/obo/cl/releases/2022-08-16/cl.owl
            md5: d0655766574e63f3fe5ed56d3c030880
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write(input_file_content)
        f.flush()
        yield f.name

    Path(f.name).unlink()


@pytest.fixture(scope="function")
def current_yaml_replica():
    input_file_content = """
    Organism:
      all:
        ensembl: release-108
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write(input_file_content)
        f.flush()
        yield f.name

    Path(f.name).unlink()


def test_parse_versions_yaml(versions_yaml_replica):
    parsed_df = parse_sources_yaml(versions_yaml_replica)
    assert parsed_df.shape == (6, 8)
    assert all(
        parsed_df["entity"].values
        == ["Organism", "Gene", "Gene", "Gene", "CellType", "CellType"]
    )
    assert all(
        parsed_df["organism"].values == ["all", "human", "human", "mouse", "all", "all"]
    )
    assert all(
        parsed_df["source"].values
        == ["ensembl", "ensembl", "ensembl", "ensembl", "cl", "cl"]
    )


def test_parse_current_versions(versions_yaml_replica):
    expected = {
        "Organism": {"all": {"ensembl": "release-108"}},
        "Gene": {
            "human": {"ensembl": "release-108"},
            "mouse": {"ensembl": "release-108"},
        },
        "CellType": {"all": {"cl": "2023-02-15"}},
    }

    assert parse_currently_used_sources(versions_yaml_replica) == expected


def test_add_records_to_existing_dict(new_versions_yaml_replica, versions_yaml_replica):
    expected = [
        {
            "entity": "Organism",
            "source": "ensembl",
            "organism": "new-organism",
            "version": "release-x",
            "url": "new-organism-source-link",
            "md5": "",
            "source_name": "Ensembl",
            "source_website": "https://www.ensembl.org/index.html",
        },
        {
            "entity": "Gene",
            "source": "new-source",
            "organism": "human",
            "version": "release-x",
            "url": "new-gene-source-link",
            "md5": "",
            "source_name": "",
            "source_website": "",
        },
        {
            "entity": "CellType",
            "source": "cl",
            "organism": "all",
            "version": "new-version",
            "url": "new-cell-type-source",
            "md5": "new-md5",
            "source_name": "Cell Ontology",
            "source_website": "https://obophenotype.github.io/cell-ontology/",
        },
    ]

    records = records_diff_btw_yamls(new_versions_yaml_replica, versions_yaml_replica)

    assert records == expected

    updated_dict = add_records_to_existing_dict(
        records, load_yaml(versions_yaml_replica)
    )
    assert updated_dict.get("Organism").get("ensembl").get("new-organism").get(
        "release-x"
    ) == {"url": "new-organism-source-link", "md5": ""}
    assert updated_dict.get("Gene").get("new-source").get("human").get("release-x") == {
        "url": "new-gene-source-link",
        "md5": "",
    }
    assert updated_dict.get("CellType").get("cl").get("all").get("new-version") == {
        "url": "new-cell-type-source",
        "md5": "new-md5",
    }


def test_update_local_sources_yaml():
    local_dict = load_yaml(settings.local_sources)
    local_dict.pop("Organism")
    write_yaml(local_dict, settings.local_sources)
    update_local_sources_yaml()


def test_reset_sources(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    import shutil

    shutil.copyfile(
        settings.current_sources.as_posix(), settings.lamindb_sources.as_posix()
    )
    reset_sources()

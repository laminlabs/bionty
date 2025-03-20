import tempfile
from pathlib import Path

import pytest
from bionty.base.dev._handle_sources import (
    parse_currently_used_sources,
    parse_sources_yaml,
)


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
          2022-08-16:
            url: http://purl.obolibrary.org/obo/cl/releases/2022-08-16/cl.owl
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write(input_file_content)
        f.flush()
        yield f.name

    Path(f.name).unlink()


def test_parse_versions_yaml(versions_yaml_replica):
    parsed_df = parse_sources_yaml(versions_yaml_replica)
    assert parsed_df.shape == (6, 7)
    assert all(
        parsed_df["entity"].values
        == ["Organism", "Gene", "Gene", "Gene", "CellType", "CellType"]
    )
    assert all(
        parsed_df["organism"].values == ["all", "human", "human", "mouse", "all", "all"]
    )
    assert all(
        parsed_df["name"].values
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

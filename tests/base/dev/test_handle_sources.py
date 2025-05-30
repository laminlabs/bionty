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
    version: "0.3.0"
    Organism:
      ensembl:
        vertebrates:
          latest-version: release-112
          url: https://ftp.ensembl.org/pub/{version}/species_EnsemblVertebrates.txt
        name: Ensembl
        website: https://www.ensembl.org/index.html
    Gene:
      ensembl:
        human:
          latest-version: release-112
          url: s3://bionty-assets/df_human__ensembl__{version}__Gene.parquet
        mouse:
          latest-version: release-112
          url: s3://bionty-assets/df_mouse__ensembl__{version}__Gene.parquet
        name: Ensembl
        website: https://www.ensembl.org/index.html
    CellType:
      cl:
        all:
          latest-version: 2024-08-16
          url: http://purl.obolibrary.org/obo/cl/releases/{version}/cl.owl
        name: Cell Ontology
        website: https://obophenotype.github.io/cell-ontology
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write(input_file_content)
        f.flush()
        yield f.name

    Path(f.name).unlink()


def test_parse_versions_yaml(versions_yaml_replica):
    parsed_df = parse_sources_yaml(versions_yaml_replica)
    assert parsed_df.shape == (4, 7)
    assert all(parsed_df["entity"].values == ["Organism", "Gene", "Gene", "CellType"])
    assert all(parsed_df["organism"].values == ["vertebrates", "human", "mouse", "all"])
    assert all(parsed_df["name"].values == ["ensembl", "ensembl", "ensembl", "cl"])


def test_parse_current_versions(versions_yaml_replica):
    expected = {
        "Organism": {"vertebrates": {"ensembl": "release-112"}},
        "Gene": {
            "human": {"ensembl": "release-112"},
            "mouse": {"ensembl": "release-112"},
        },
        "CellType": {"all": {"cl": "2024-08-16"}},
    }

    assert parse_currently_used_sources(versions_yaml_replica) == expected

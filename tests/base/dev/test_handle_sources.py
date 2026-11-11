import tempfile
from pathlib import Path

import pytest
from bionty.base.dev._handle_sources import (
    parse_currently_used_sources,
    parse_sources_yaml,
    records_from_sources_yaml,
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


def test_source_records_do_not_import_pandas(tmp_path, monkeypatch):
    content = """
    version: "0.3.0"
    CellLine:
      cellosaurus:
        all:
          latest-version: "56.0"
          url: https://example.com/{version}/cellosaurus
        name: Cellosaurus
        website: https://www.cellosaurus.org/
      clo:
        all:
          latest-version: "2022-03-21"
          url: https://example.com/{version}/clo
        name: Cell Line Ontology
        website: https://example.com
    """
    path = tmp_path / "sources.yaml"
    path.write_text(content)

    # Same rows the DataFrame API returns, including the version filled into the URL.
    assert records_from_sources_yaml(path) == parse_sources_yaml(path).to_dict(
        orient="records"
    )

    import builtins

    real_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "pandas" or name.startswith("pandas."):
            raise ModuleNotFoundError("No module named 'pandas'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    records = records_from_sources_yaml(path)
    current = parse_currently_used_sources(records)
    assert current == {"CellLine": {"all": {"cellosaurus": "56.0"}}}
    # Same choice write_bionty_sources makes: the first source for an organism.
    assert [
        current[record["entity"]][record["organism"]].get(record["name"])
        == record["version"]
        for record in records
    ] == [True, False]

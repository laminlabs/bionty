from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from bionty.base._settings import settings

if TYPE_CHECKING:
    from pandas import DataFrame
from bionty.base.dev._io import load_yaml


def LAMINDB_INSTANCE_LOADED():
    is_loaded = False
    lnenv_filepath = Path.home() / ".lamin/current_instance.env"
    if lnenv_filepath.exists():
        with open(lnenv_filepath.as_posix()) as f:
            is_loaded = "bionty" in f.read().split("schema_str=")[-1]
    return is_loaded


def records_from_sources_yaml(
    filepath: str | Path = settings.public_sources,
    url_pattern: bool = False,
) -> list[dict]:
    """Parse values from sources yaml file into a list of records."""
    all_rows = []
    for entity, sources in load_yaml(filepath).items():
        if entity == "version":
            continue
        for source, organism_source in sources.items():
            name = organism_source.get("name", "")
            website = organism_source.get("website", "")
            for organism, versions in organism_source.items():
                if organism in ["name", "website"]:
                    continue
                latest_version = str(versions.get("latest-version"))
                url = versions.get("url")
                if not url_pattern:
                    url = url.replace("{version}", latest_version)
                all_rows.append(
                    {
                        "entity": entity,
                        "name": source,
                        "organism": organism,
                        "version": latest_version,
                        "url": url,
                        "description": name,
                        "source_website": website,
                    }
                )
    return all_rows


def parse_sources_yaml(
    filepath: str | Path = settings.public_sources,
    url_pattern: bool = False,
) -> DataFrame:
    """Parse values from sources yaml file into a DataFrame.

    Args:
        filepath: Path to the versions yaml file.

    Returns:
        - entity
        - name
        - organism
        - version
        - url
        - description
        - source_website
    """
    import pandas as pd

    return pd.DataFrame(
        records_from_sources_yaml(filepath, url_pattern=url_pattern),
        columns=[
            "entity",
            "name",
            "organism",
            "version",
            "url",
            "description",
            "source_website",
        ],
    )


def parse_currently_used_sources(yaml: str | Path | list[dict]) -> dict:
    """Parse out the most recent versions from yaml."""
    if isinstance(yaml, str | Path):
        records = records_from_sources_yaml(yaml)
    else:
        records = yaml

    current_dict: dict = {}
    for kwargs in records:
        entity, organism, source, version = (
            kwargs["entity"],
            kwargs["organism"],
            kwargs["name"],
            kwargs["version"],
        )
        if entity not in current_dict:
            current_dict[entity] = {}
        if organism not in current_dict[entity]:
            current_dict[entity][organism] = {source: version}
    return current_dict

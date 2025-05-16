from __future__ import annotations

from pathlib import Path

import pandas as pd

from bionty.base._settings import settings
from bionty.base.dev._io import load_yaml


def LAMINDB_INSTANCE_LOADED():
    is_loaded = False
    lnenv_filepath = Path.home() / ".lamin/current_instance.env"
    if lnenv_filepath.exists():
        with open(lnenv_filepath.as_posix()) as f:
            is_loaded = "bionty" in f.read().split("schema_str=")[-1]
    return is_loaded


def parse_sources_yaml(
    filepath: str | Path = settings.public_sources,
    url_pattern: bool = False,
) -> pd.DataFrame:
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
                row = (entity, source, organism, latest_version, url, name, website)
                all_rows.append(row)

    return pd.DataFrame(
        all_rows,
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
        df = parse_sources_yaml(yaml)
        df_current = (
            df[["entity", "name", "organism", "version"]]  # type: ignore
            .drop_duplicates(["entity", "organism", "name"], keep="first")
            .groupby(["entity", "organism", "name"], sort=False)
            .max()
        )
        records = df_current.reset_index().to_dict(orient="records")
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

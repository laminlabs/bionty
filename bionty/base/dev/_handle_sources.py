from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd
from lamin_utils import logger

from bionty.base._settings import settings
from bionty.base.dev._io import load_yaml, write_yaml


def LAMINDB_INSTANCE_LOADED():
    is_loaded = False
    lnenv_filepath = Path.home() / ".lamin/current_instance.env"
    if lnenv_filepath.exists():
        with open(lnenv_filepath.as_posix()) as f:
            is_loaded = "bionty" in f.read().split("schema_str=")[-1]
    return is_loaded


def reset_sources(confirm: bool = False) -> None:
    """Reset local bionty sources file."""
    from importlib import reload

    import bionty

    def _confirm() -> bool:
        """Ask user to enter Y or N (case-insensitive).

        Returns:
            True if the answer is Y/y.
        """
        if confirm:
            answer = "y"
        else:
            answer = ""
            while answer not in ["y", "n"]:
                answer = input(
                    "Are you sure that you want to reset your local bionty sources?"
                    " (y/n) "
                ).lower()
        return answer == "y"

    if _confirm():
        try:
            settings.local_sources.unlink()
            logger.success(f"removed file: {settings.local_sources}.")
        except FileNotFoundError:
            pass
        try:
            settings.current_sources.unlink()
            logger.success(f"removed file: {settings.current_sources}.")
        except FileNotFoundError:
            pass
        try:
            settings.lamindb_sources.unlink()
            logger.success(f"removed file: {settings.lamindb_sources}.")
        except FileNotFoundError:
            pass

        reload(bionty)
        logger.info("reloaded bionty!")


def create_or_update_sources_local_yaml(overwrite: bool = True) -> None:
    """If settings.local_sources doesn't exist, copy from settings.public_sources and create it.

    Args:
        overwrite: Whether to overwrite the current settings.local_sources.
    """
    if not settings.local_sources.exists() or overwrite:
        public_df_records = parse_sources_yaml(settings.public_sources).to_dict(  # type: ignore
            orient="records"
        )
        versions = add_records_to_existing_dict(public_df_records, {})
        versions_header = {"version": load_yaml(settings.public_sources).get("version")}
        versions_header.update(versions)
        write_yaml(versions_header, settings.local_sources)
    else:
        update_local_sources_yaml()


def parse_sources_yaml(
    filepath: str | Path = settings.public_sources,
) -> pd.DataFrame:
    """Parse values from sources yaml file into a DataFrame.

    Args:
        filepath: Path to the versions yaml file.

    Returns:
        - entity
        - source
        - organism
        - version
        - url
        - md5
        - source_name
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
                for version_key, version_meta in versions.items():
                    row = (
                        entity,
                        source,
                        organism,
                        str(version_key),
                        version_meta.get("url"),
                        version_meta.get("md5", ""),
                        name,
                        website,
                    )
                    all_rows.append(row)

    return pd.DataFrame(
        all_rows,
        columns=[
            "entity",
            "source",
            "organism",
            "version",
            "url",
            "md5",
            "source_name",
            "source_website",
        ],
    )


def create_currently_used_sources_yaml(
    overwrite: bool = True, source: Literal["versions", "local"] = "local"
) -> None:
    """Write the most recent version to the settings.current_sources .

    Takes the 1st source defined in the source.

    Args:
        overwrite: Whether to overwrite the settings.current_sources even if it exists already.
        source: The yaml source to use to create the settings.current_sources.
                Defaults to 'local'.
    """
    if not settings.current_sources.exists() or overwrite:
        source_path = (
            settings.public_sources if source == "versions" else settings.local_sources
        )

        write_yaml(parse_currently_used_sources(source_path), settings.current_sources)


def records_diff_btw_yamls(yamlpath1: str | Path, yamlpath2: str | Path) -> list:
    """Records in yaml1 but not yaml2."""
    public_df_records = parse_sources_yaml(yamlpath1).to_dict(orient="records")
    local_df_records = parse_sources_yaml(yamlpath2).to_dict(orient="records")
    additional_records = [
        record for record in public_df_records if record not in local_df_records
    ]

    return additional_records


def update_local_sources_yaml() -> None:
    """Update settings.local_sources to add additional entries from settings.public_sources."""
    additional_records = records_diff_btw_yamls(
        settings.public_sources, settings.local_sources
    )
    if len(additional_records) > 0:
        updated_local_versions = add_records_to_existing_dict(
            additional_records, load_yaml(settings.local_sources)
        )
        write_yaml(updated_local_versions, settings.local_sources)
        logger.success(
            f"wrote new records from public sources.yaml to {settings.local_sources}!\n\n"
            "if you see this message repeatedly, run: import bionty; bionty.base.reset_sources()"
        )


def parse_currently_used_sources(yaml: str | Path | list[dict]) -> dict:
    """Parse out the most recent versions from yaml."""

    def _parse(key: str):
        if isinstance(yaml, (str, Path)):
            df = parse_sources_yaml(yaml)
            df_current = (
                df[["entity", "source", key, "version"]]  # type: ignore
                .drop_duplicates(["entity", key, "source"], keep="first")
                .groupby(["entity", key, "source"], sort=False)
                .max()
            )
            records = df_current.reset_index().to_dict(orient="records")
        else:
            records = yaml

        current_dict: dict = {}
        for kwargs in records:
            entity, organism, source, version = (
                kwargs["entity"],
                kwargs[key],
                kwargs["source"],
                kwargs["version"],
            )
            if entity not in current_dict:
                current_dict[entity] = {}
            if organism not in current_dict[entity]:
                current_dict[entity][organism] = {source: version}
        return current_dict

    try:
        return _parse("organism")
    except KeyError:
        return _parse("species")


def add_records_to_existing_dict(records: list[dict], target_dict: dict) -> dict:
    """Add records to a versions yaml file."""
    for kwargs in records:
        entity, source, organism, version = (
            kwargs["entity"],
            kwargs["source"],
            kwargs["organism"],
            kwargs["version"],
        )
        if entity not in target_dict:
            target_dict[entity] = {}
        if source not in target_dict[entity]:
            target_dict[entity][source] = {
                organism: {version: {"url": kwargs["url"], "md5": kwargs["md5"]}}
            }
            target_dict[entity][source].update(
                {"name": kwargs["source_name"], "website": kwargs["source_website"]}
            )
        if organism not in target_dict[entity][source]:
            target_dict[entity][source][organism] = {
                version: {"url": kwargs["url"], "md5": kwargs["md5"]}
            }
        if version not in target_dict[entity][source][organism]:
            target_dict[entity][source][organism][version] = {
                "url": kwargs["url"],
                "md5": kwargs["md5"],
            }
    return target_dict

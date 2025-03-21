from __future__ import annotations

from typing import TYPE_CHECKING

from lamin_utils import logger

import bionty.base as bt_base

if TYPE_CHECKING:
    from pathlib import Path

    from lamindb.models import Artifact, Record


def sync_public_sources(update_currently_used: bool = False) -> None:
    """Sync up the Source registry with the new public sources.

    This function registers new public sources in the Source registry.

    Args:
        update_currently_used: Whether to update the currently_used sources to the latest versions.

    Example::

        from bionty.core import sync_all_sources_to_latest

        sync_public_sources()
    """
    import bionty as bt
    from bionty._biorecord import list_biorecord_models

    records = bt.Source.filter().all()
    df_sources = bt_base.display_available_sources().reset_index()
    bionty_models = list_biorecord_models(bt)
    for kwargs in df_sources.to_dict(orient="records"):
        if kwargs["entity"] in bionty_models:
            kwargs["entity"] = "bionty." + kwargs["entity"]
        record = records.filter(
            name=kwargs["name"],
            version=kwargs["version"],
            entity=kwargs["entity"],
            organism=kwargs["organism"],
        ).all()
        if len(record) == 0:
            record = bt.Source(**kwargs).save()
            logger.success(f"added new source: {record}")
        else:
            # update metadata fields
            record.update(**kwargs)
            logger.success(f"updated source: {record.one()}")

    if update_currently_used:
        logger.info("setting the latest version as currently_used...")
        df = records.df()
        for (_, _, _), df_group in df.groupby(["entity", "organism", "name"]):
            if df_group.currently_used.sum() == 0:
                continue
            latest_uid = df_group.sort_values("version", ascending=False).uid.iloc[0]
            latest_record = records.get(latest_uid)
            latest_record.currently_used = True
            latest_record.save()

    logger.success("synced up Source registry with the latest public sources")


def register_source_in_bionty_assets(
    filepath: Path,
    source: Record,
    is_dataframe: bool = True,
    update: bool = False,
) -> Artifact:
    """Register a new source in the laminlabs/bionty-assets instance.

    Args:
        filepath: Path to the source file.
        source: Source record.
        is_dataframe: Whether the file is the DataFrame of the source.
        update: Whether to update the source if it already exists.

    Returns:
        Registered artifact record.

    Example::

        from bionty.core import register_source_in_bionty_assets

        source = Source.filter(entity="bionty.Gene", organism="human", name="ensembl", version="release-112").save()

        source_artifact = register_source_in_bionty_assets(
            "path/to/source.parquet",
            source,
            is_dataframe=True,
        )
    """
    import lamindb as ln

    assert ln.setup.settings.instance.slug == "laminlabs/bionty-assets"

    if "." not in source.entity:
        raise ValueError(
            "source entity must be in form of 'module.ClassName', e.g. 'bionty.Gene'"
        )

    filepath = ln.UPath(filepath)
    if is_dataframe:
        assert filepath.suffix == ".parquet"

    artifact = ln.Artifact.filter(
        key=filepath.name, _key_is_virtual=False
    ).one_or_none()
    if artifact is not None:
        if not update:
            raise ValueError(
                f"artifact already exists: {artifact}\n   → pass `update=True` to update it"
            )
        else:
            artifact.replace(filepath)
    else:
        artifact = ln.Artifact(filepath, key=filepath.name)
        # NOTE: we use non-virtual keys for bionty-assets artifacts
        artifact._key_is_virtual = False
    artifact.save()

    if is_dataframe:
        organism, source_name, version, entity = filepath.stem.removeprefix(
            "df_"
        ).split("__")
        assert organism == source.organism
        assert source_name == source.name
        assert version == source.version
        assert entity == source.entity.split(".")[-1]
        source.dataframe_artifact = artifact
        source.save()
        logger.print(
            f"linked Source(uid={source.uid}) to dataframe_artifact {artifact}"
        )
    else:
        source.artifacts.add(artifact)
        logger.print(f"linked Source(uid={source.uid}) to {artifact}")

    return artifact

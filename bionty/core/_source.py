from __future__ import annotations

from typing import TYPE_CHECKING

from lamin_utils import logger

import bionty.base as bt_base

if TYPE_CHECKING:
    from pathlib import Path

    from lamindb.models import Artifact, Record


def sync_public_sources(update_currently_used: bool = False) -> None:
    """Add new public sources to the Source registry.

    This function registers new public sources in the Source registry.

    Public sources are in [sources.yaml](https://github.com/laminlabs/bionty/blob/main/bionty/base/sources.yaml).

    Args:
        update_currently_used: If True, set the latest version as currently_used.

    Example::

        from bionty.core import sync_public_sources

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


def update_records_to_source(registry: type[Record], source: Record) -> None:
    """Update the existing records associated with old source to the new source.

    Args:
        registry: Record class to update.
        source: Source record to apply updates.
    """
    import lamindb as ln

    from bionty._source import filter_public_df_columns

    entity = registry.__get_name_with_module__()

    if entity != source.entity:
        raise ValueError(f"please pass a source record of the same entity: {entity}")

    # find records that need to be upgraded
    filter_kwargs = {
        "source__entity": entity,
        "source__name": source.name,
    }
    if hasattr(registry, "organism_id"):
        filter_kwargs["organism__name"] = source.organism
    records = registry.filter(**filter_kwargs).exclude(source=source).all()
    if len(records) == 0:
        return

    # determine the ontology ID field to use
    ontology_id_field = getattr(registry, "_ontology_id_field", "ontology_id")
    name_field = getattr(registry, "_name_field", "name")

    # get the new data from the source
    public_df = filter_public_df_columns(registry, registry.public(source=source))
    public_df.rename(columns={"parents": "_parents"}, inplace=True)
    if ontology_id_field not in public_df.columns:
        ontology_id_field = "stable_id" if "stable_id" in public_df.columns else None
        if not ontology_id_field:
            raise ValueError(
                f"'{ontology_id_field}' column is not found in the source dataframe."
            )

    # a dictionary of records indexed by ontology ID
    public_dict = {row[ontology_id_field]: row for _, row in public_df.iterrows()}

    # filter records that have matching ontology IDs
    records = records.filter(
        **{ontology_id_field + "__in": set(public_dict.keys())}
    ).all()

    # update records without artifacts
    # simply update the record if no artifacts are associated
    records_without_artifacts = records.filter(artifacts=None).all()
    records_to_update = []
    if records_without_artifacts:
        for record in records_without_artifacts:
            ontology_id = getattr(record, ontology_id_field)
            # update all fields from the new source
            for col in public_df.columns:
                setattr(record, col, public_dict[ontology_id].get(col))
            record.source_id = source.id
            records_to_update.append(record)

    # handle records with artifacts
    records_with_artifacts = records.exclude(artifacts=None).all()
    ontology_ids_for_new_records = []
    for record in records_with_artifacts:
        ontology_id = getattr(record, ontology_id_field)

        # if name changed, create a new record
        if (
            ontology_id in public_dict
            and hasattr(record, name_field)
            and getattr(record, name_field) != public_dict[ontology_id].get(name_field)
        ):
            ontology_ids_for_new_records.append(ontology_id)
        # otherwise, update the existing record
        else:
            for col in public_df.columns:
                setattr(record, col, public_dict[ontology_id].get(col))
            record.source_id = source.id
            records_to_update.append(record)
    # bulk update records with artifacts where name didn't change
    if records_to_update:
        logger.info(f"updating {len(records_to_update)} records...")
        ln.save(records_to_update)
        logger.success(f"{len(records_to_update)} records updated!")

    # create new records for those with name changes
    if ontology_ids_for_new_records:
        logger.info(f"creating {len(ontology_ids_for_new_records)} new records...")
        registry.from_values(
            ontology_ids_for_new_records,
            field=getattr(registry, ontology_id_field),
            source=source,
        ).save()
        logger.success(f"{len(ontology_ids_for_new_records)} new records created!")

    # set the source as currently used
    if not source.currently_used:
        source.currently_used = True
        source.save()


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

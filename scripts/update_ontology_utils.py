from pathlib import Path

import bionty as bt
from bionty.base._ontology_url import get_ontology_url
from lamin_utils import logger


def get_ontology_version(source_name: str, version: str = None) -> str:
    """Get the ontology version to use, fetches latest if not specified."""
    logger.debug(
        f"getting ontology URL for {source_name}, requested version: {version or 'latest'}"
    )
    *_, version_to_use = get_ontology_url(prefix=source_name, version=version)
    return version_to_use


def validate_ontology_data(
    entity: str, source_name: str, organism: str, new_df, version_to_use: str
) -> bool:
    """Validate new ontology data against existing."""
    required_columns = {"name", "ontology_id", "synonyms"}
    config_id = f"{entity}_{source_name}_{organism}"

    try:
        currently_used_source = bt.Source.filter(
            entity=f"bionty.{entity}",
            name=source_name,
            organism=organism,
            currently_used=True,
        ).one_or_none()

        if currently_used_source:
            current_version_df = getattr(bt.base, entity)(
                source=currently_used_source
            ).df()
            n_new = new_df.shape[0]
            n_old = current_version_df.shape[0]

            # should have more or equal rows than the earlier version
            if n_new < n_old:
                logger.warning(
                    f"entity {entity} using source {source_name} of version {version_to_use} and organism {organism} has fewer rows than current version: {n_new} < {n_old}. Skipping..."
                )
                return False

            # Check required columns
            missing_columns = required_columns - set(new_df.columns)
            if missing_columns:
                logger.warning(
                    f"{config_id} missing required columns: {missing_columns}. Skipping..."
                )
                return False

    except ValueError as e:
        if "No source url is available" in str(e):
            pass  # This occurs during testing in local instances
        else:
            raise

    return True


def register_ontology_source(
    entity: str, source_name: str, organism: str, version_to_use: str
) -> bool:
    """Register an ontology in bionty assets."""
    from bionty.core._source import register_source_in_bionty_assets

    config_id = f"{entity}_{source_name}_{organism}"

    try:
        logger.debug(f"adding source record for {entity}")
        source_rec = getattr(bt, entity).add_source(
            source=source_name, version=version_to_use
        )

        logger.info(f"registering assets for {config_id}...")

        register_source_in_bionty_assets(
            Path(
                f"{bt.base.settings.dynamicdir}/df_{organism}__{source_name}__{version_to_use}__{entity}.parquet"
            ),
            source=source_rec,
            is_dataframe=True,
        )
        register_source_in_bionty_assets(
            Path(
                f"{bt.base.settings.dynamicdir}/ontology_{organism}__{source_name}__{version_to_use}__{entity}"
            ),
            source=source_rec,
            is_dataframe=False,
        )
        logger.info(f"registered a new version {version_to_use} of {entity}.")
        return True

    except ValueError as e:
        if "artifact already exists" in str(e):
            logger.warning(
                f"entity {entity} using source {source_name} of version {version_to_use} and organism {organism} is already registered. Skipping..."
            )
        else:
            raise
        return False
    except FileNotFoundError:
        logger.warning(
            f"entity {entity} using source {source_name} of version {version_to_use} and organism {organism} file cannot be found. "
            "This can happen if the ontology was previously registered and the pronto ontology file did not get recreated. Skipping..."
        )
        return False


def process_ontology(config: tuple) -> bool:
    """Process a single ontology configuration."""
    entity, source_name, organism, *version = config
    config_id = f"{entity}_{source_name}_{organism}"

    try:
        # fetch the latest version of ontology if not specified
        version_to_use = get_ontology_version(
            source_name, version[0] if version else None
        )

        logger.info(
            f"processing... {entity:<20} {source_name:<10} {version_to_use:<12} {organism}"
        )

        new_df = getattr(bt.base, entity)(
            source=source_name, version=version_to_use
        ).df()

        if not validate_ontology_data(
            entity, source_name, organism, new_df, version_to_use
        ):
            return False

        return register_ontology_source(entity, source_name, organism, version_to_use)

    except Exception as e:
        logger.error(f"{config_id} failed: {type(e).__name__}: {str(e)}")
        return False

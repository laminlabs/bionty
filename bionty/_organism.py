import re

import pandas as pd
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from lamin_utils import logger
from lamindb.base.types import FieldAttr

from .models import BioRecord, Organism


class OrganismNotSet(SystemExit):
    """The `organism` parameter was not passed or is not globally set."""

    pass


def create_or_get_organism_record(
    organism: str | Organism | None,
    registry: type[BioRecord],
    field: FieldAttr | None = None,
) -> Organism | None:
    """Create or get an organism record.

    From the following options:
    1. the globally setting of organism
    2. the passed organism record
    3. the passed organism name
    """
    # also returns None if a registry doesn't require organism field
    organism_record = None
    if is_organism_required(registry=registry, field=field) or organism is not None:
        from .core._settings import settings
        from .models import Organism

        # using global setting of organism
        if organism is None and settings.organism is not None:
            logger.debug(f"using configured organism = {settings.organism.name}")
            return settings.organism

        # create or get organism record
        if isinstance(organism, Organism):
            organism_record = organism
        elif isinstance(organism, str):
            if is_organism_required:
                organism_record = get_or_create_organism_from_name(name=organism)

    return organism_record


def is_organism_required(
    registry: type[BioRecord], field: FieldAttr | None = None
) -> bool:
    """Check if the registry has an organism field and is required.

    Returns:
        True if the registry has an organism field and is required, False otherwise.
    """
    required = True

    # first we determine the requireness based on the registry.organism FK field
    try:
        organism_field = registry._meta.get_field("organism")
        # organism is not required or not a relation
        if organism_field.null or not organism_field.is_relation:
            required = False
        else:
            required = True
    except FieldDoesNotExist:
        required = False

    # field of the registry is used to determine if organism is required to create record in the registry
    if field is not None:
        is_simple_field_unique = field.field.unique and not field.field.is_relation
        required = required and not is_simple_field_unique

    return required


def get_or_create_organism_from_name(
    name: str, using_key: str | None = None
) -> Organism:
    """Create organism record if not exists."""
    import bionty as bt

    using_key = None if using_key == "default" else using_key

    organism_record = bt.Organism.connect(using_key).filter(name=name).one_or_none()
    if organism_record is None:
        from lamindb.errors import DoesNotExist

        try:
            organism_record = bt.Organism.from_source(
                name=name
            )  # here assumes the default source is ensembl vertebrates
            organism_record.save(using=using_key)
        except DoesNotExist:
            raise OrganismNotSet(
                f"Organism {name} can't be created from the source, check your spelling or create it manually."
            ) from None
    return organism_record


def infer_organism_from_ensembl_id(
    id: str, using_key: str | None = None
) -> Organism | None:
    """Get organism record from ensembl id."""
    import bionty as bt
    from bionty.base.dev._io import s3_bionty_assets

    # below has to consume a file path and NOT a directory because otherwise it fails on reticulate
    localpath = s3_bionty_assets(
        ".lamindb/0QeqXlKq9aqW8aqe0000.parquet",
        bt.base.settings.dynamicdir / "ensembl_prefix.parquet",
    )
    ensembl_prefixes = pd.read_parquet(localpath).set_index("gene_prefix")

    prefix = (
        re.search(r"^[A-Za-z]+", id).group(0) if re.search(r"^[A-Za-z]+", id) else id
    )

    # for ensembl vertebrates, we infer organism from the ensembl prefix
    if prefix in ensembl_prefixes.index:
        organism_name = ensembl_prefixes.loc[prefix, "name"].lower()
        return get_or_create_organism_from_name(name=organism_name, using_key=using_key)
    return None

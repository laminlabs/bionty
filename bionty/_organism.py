import re

import pandas as pd
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from lamin_utils import logger

from .models import BioRecord, Organism


class OrganismNotSet(SystemExit):
    """The `organism` parameter was not passed or is not globally set."""

    pass


def create_or_get_organism_record(
    organism: str | Organism | None, registry: type[BioRecord], field: str | None = None
) -> Organism | None:
    """Create or get an organism record from the given organism name."""
    # return None if a registry doesn't require organism field
    organism_record = None
    if is_organism_required(registry):
        # using global setting of organism
        from .core._settings import settings
        from .models import Organism

        if organism is None and settings.organism is not None:
            logger.warning(f"using default organism = {settings.organism.name}")
            return settings.organism

        if isinstance(organism, Organism):
            organism_record = organism
        elif isinstance(organism, str):
            try:
                # existing organism record
                organism_record = Organism.objects.get(name=organism)
            except ObjectDoesNotExist:
                try:
                    # create a organism record from bionty reference
                    organisms = Organism.from_values([organism])
                    if len(organisms) == 0:
                        raise ValueError(
                            f"Organism {organism} can't be created from the bionty reference, check your spelling or create it manually."
                        )
                    organism_record = organisms[0].save()  # type:ignore
                except KeyError:
                    # no such organism is found in bionty reference
                    organism_record = None

        if organism_record is None:
            if hasattr(registry, "_ontology_id_field") and field in {
                registry._ontology_id_field,
                "uid",
            }:
                return None
            raise OrganismNotSet(
                f"{registry.__name__} requires to specify a organism name via `organism=` or `bionty.settings.organism=`!"
            )

    return organism_record


def is_organism_required(registry: type[BioRecord]) -> bool:
    """Check if the registry has an organism field and is required.

    Returns:
        True if the registry has an organism field and is required, False otherwise.
    """
    try:
        organism_field = registry._meta.get_field("organism")
        # organism is not required or not a relation
        if organism_field.null or not organism_field.is_relation:
            return False
        else:
            return True
    except FieldDoesNotExist:
        return False


def organism_from_ensembl_id(id: str, using_key: str | None) -> Organism | None:
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
    if prefix in ensembl_prefixes.index:
        organism_name = ensembl_prefixes.loc[prefix, "name"].lower()

        using_key = None if using_key == "default" else using_key

        organism_record = (
            bt.Organism.using(using_key).filter(name=organism_name).one_or_none()
        )
        if organism_record is None:
            organisms = bt.Organism.from_values([organism_name])
            if len(organisms) > 0:
                organism_record = organisms[0]
                organism_record.save(using=using_key)
            else:
                raise OrganismNotSet(
                    f"Organism {organism_name} can't be created from the source, check your spelling or create it manually."
                )
        return organism_record
    return None

import re

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
    required = registry.require_organism(field=field)
    if required or organism is not None:
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
            # not error if organism isn't required, for instance passing organism="all" for CellLine
            organism_record = get_or_create_organism_from_name(
                name=organism, error=required
            )

    return organism_record


def get_or_create_organism_from_name(
    name: str, using_key: str | None = None, error: bool = True
) -> Organism:
    """Create organism record if not exists."""
    import bionty as bt

    using_key = None if using_key == "default" else using_key

    organism_record = bt.Organism.connect(using_key).filter(name=name).one_or_none()
    if organism_record is None:
        # try to match organism by scientific name
        organism_record = (
            bt.Organism.connect(using_key).filter(scientific_name=name).one_or_none()
        )
        if organism_record is None:
            from lamindb.errors import DoesNotExist
            from lamindb.models.query_set import SQLRecordList

            # try to create from ncbitaxon source
            try:
                source = bt.Source.filter(name="ncbitaxon").first()
                organism_record = bt.Organism.from_source(name, source=source)
                if isinstance(organism_record, SQLRecordList):
                    organism_record = organism_record[0]
                    logger.warning(
                        f"Multiple organisms found for {name}, saving the first one: {organism_record}"
                    )
                organism_record.save(using=using_key)
            except DoesNotExist:
                try:
                    organism_record = bt.Organism.from_source(
                        scientific_name=name, source=source
                    )
                    organism_record.save(using=using_key)
                except DoesNotExist:
                    if error:
                        raise OrganismNotSet(
                            f"Organism {name} can't be created from the source, check your spelling or create it manually."
                        ) from None
                    else:
                        # for instance, organism="all" for CellLine should pass
                        pass
    return organism_record


def infer_organism_from_ensembl_id(
    id: str, using_key: str | None = None
) -> Organism | None:
    """Get organism record from ensembl id."""
    import pandas as pd

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
        organism_name = ensembl_prefixes.loc[prefix, "name"]
        # ensembl_prefixes can have duplicate entries for a prefix (e.g., ENSRNOG)
        # when Ensembl lists both a canonical organism and strain-specific variants.
        # In this case, loc returns a Series. We prefer names without " - " because
        # Ensembl uses that delimiter to append strain/assembly qualifiers
        # (for instance "Rat - SHR/Utx ..."), while the canonical species name stays
        # unsuffixed (for instance "Rat"). If every entry is qualified, we take the
        # shared base name before " - " when all variants agree; otherwise we fall
        # back to the first value to keep inference resilient.
        if isinstance(organism_name, pd.Series):
            organism_names = organism_name.dropna().astype(str).str.lower()
            canonical_names = organism_names[~organism_names.str.contains(r" - ")]
            if len(canonical_names) > 0:
                organism_name = canonical_names.iloc[0]
            else:
                base_names = organism_names.str.split(" - ", n=1).str[0].str.strip()
                unique_base_names = base_names.drop_duplicates()
                organism_name = (
                    unique_base_names.iloc[0]
                    if len(unique_base_names) == 1
                    else organism_names.iloc[0]
                )
        else:
            organism_name = str(organism_name).lower()
        return get_or_create_organism_from_name(name=organism_name, using_key=using_key)
    return None

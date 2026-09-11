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


def _from_source_organism(**kwargs):
    """Return an Organism from source, or None if the value is missing."""
    from lamindb.errors import DoesNotExist

    import bionty as bt

    try:
        record = bt.Organism.from_source(**kwargs)
    except DoesNotExist:
        return None
    if isinstance(record, list):
        if not record:
            return None
        # Ensembl lists strain assemblies under the same ontology_id; prefer the
        # unsuffixed species row when present.
        unsuffixed = [
            item
            for item in record
            if getattr(item, "name", None) and " - " not in item.name
        ]
        return unsuffixed[0] if unsuffixed else record[0]
    return record


def _save_or_get_organism(organism_record, using_key: str | None = None):
    """Reuse a DB record with the same ontology_id if present."""
    import bionty as bt

    if isinstance(organism_record, list):
        organism_record = organism_record[0]
    if organism_record.ontology_id:
        existing = (
            bt.Organism.connect(using_key)
            .filter(ontology_id=organism_record.ontology_id)
            .one_or_none()
        )
        if existing is not None:
            return existing
    organism_record.save(using=using_key)
    return organism_record


def get_or_create_organism_from_ontology_id(
    ontology_id: str, using_key: str | None = None
) -> Organism | None:
    """Return a saved Organism with this ontology_id, creating it from source if needed."""
    import bionty as bt

    using_key = None if using_key == "default" else using_key
    organism_record = (
        bt.Organism.connect(using_key).filter(ontology_id=ontology_id).one_or_none()
    )
    if organism_record is not None:
        return organism_record

    organism_record = _from_source_organism(ontology_id=ontology_id)
    if organism_record is None:
        source = bt.Source.filter(name="ncbitaxon").first()
        if source is not None:
            organism_record = _from_source_organism(
                ontology_id=ontology_id, source=source
            )
    if organism_record is None:
        return None
    return _save_or_get_organism(organism_record, using_key=using_key)


def get_or_create_organism_from_name(
    name: str, using_key: str | None = None, error: bool = True
) -> Organism:
    """Create organism record if not exists."""
    from lamindb.errors import DoesNotExist

    import bionty as bt

    using_key = None if using_key == "default" else using_key

    organism_record = bt.Organism.connect(using_key).filter(name=name).one_or_none()
    if organism_record is None:
        # try to match organism by scientific name
        organism_record = (
            bt.Organism.connect(using_key).filter(scientific_name=name).one_or_none()
        )
        if organism_record is None:
            try:
                organism_record = bt.Organism.from_source(name=name)
                organism_record = _save_or_get_organism(
                    organism_record, using_key=using_key
                )
            except DoesNotExist:
                try:
                    source = bt.Source.filter(name="ncbitaxon").first()
                    organism_record = bt.Organism.from_source(
                        scientific_name=name, source=source
                    )
                    organism_record = _save_or_get_organism(
                        organism_record, using_key=using_key
                    )
                except DoesNotExist:
                    if error:
                        raise OrganismNotSet(
                            f"Organism {name} can't be created from the source, "
                            "check your spelling or create it manually."
                        ) from None
                    # else: organism="all" for CellLine should pass
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
        ontology_id = _ontology_id_from_ensembl_prefix(ensembl_prefixes, prefix)
        if ontology_id is not None:
            return get_or_create_organism_from_ontology_id(
                ontology_id, using_key=using_key
            )
    return None


def _ontology_id_from_ensembl_prefix(ensembl_prefixes, prefix: str) -> str | None:
    """Map an Ensembl gene prefix to NCBITaxon ontology_id.

    Prefix tables can list several assemblies for the same gene prefix (e.g.
    ENSRNOG) and their common names change between Ensembl releases. Join to the
    Ensembl organism table and return the ontology_id when it is unambiguous.
    """
    import pandas as pd

    import bionty.base as bt_base

    rows = ensembl_prefixes.loc[[prefix]]
    if isinstance(rows, pd.Series):
        rows = rows.to_frame().T

    organism_df = bt_base.Organism(source="ensembl").to_dataframe()
    if organism_df.index.name == "name":
        organism_df = organism_df.reset_index()
    if "ontology_id" not in organism_df.columns:
        return None

    matches = pd.DataFrame()
    if "scientific_name" in rows.columns and "scientific_name" in organism_df.columns:
        sci_names = rows["scientific_name"].dropna().astype(str).str.strip()
        sci_names = sci_names[sci_names != ""].drop_duplicates()
        if len(sci_names) > 0:
            matches = organism_df[organism_df["scientific_name"].isin(sci_names)]
    if matches.empty and "name" in organism_df.columns:
        names = rows["name"].dropna().astype(str).str.lower()
        canonical_names = names[~names.str.contains(r" - ", regex=True)]
        query_names = canonical_names if len(canonical_names) > 0 else names
        matches = organism_df[
            organism_df["name"].astype(str).str.lower().isin(query_names)
        ]
    if matches.empty:
        return None

    ontology_ids = matches["ontology_id"].dropna().astype(str).drop_duplicates()
    if len(ontology_ids) == 1:
        return ontology_ids.iloc[0]
    if "name" in matches.columns:
        canonical = matches[
            ~matches["name"].astype(str).str.contains(r" - ", regex=True)
        ]
        if not canonical.empty:
            ontology_ids = (
                canonical["ontology_id"].dropna().astype(str).drop_duplicates()
            )
            if len(ontology_ids) >= 1:
                return ontology_ids.iloc[0]
    return None

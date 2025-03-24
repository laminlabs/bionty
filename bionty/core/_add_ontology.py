from __future__ import annotations

from typing import TYPE_CHECKING

from lamin_utils import logger

from bionty._organism import create_or_get_organism_record, is_organism_required

if TYPE_CHECKING:
    from collections.abc import Iterable

    import pandas as pd
    from lamindb.models import Record

    from bionty.models import BioRecord, Organism, Source


def get_all_ancestors(df: pd.DataFrame, ontology_ids: Iterable[str]) -> set[str]:
    ancestors = set()
    stack = list(ontology_ids)
    while stack:
        onto_id = stack.pop()
        try:
            parents = df.at[onto_id, "parents"]
            for parent in parents:
                if parent not in ancestors:
                    ancestors.add(parent)
                    stack.append(parent)
        except KeyError:
            logger.warning(f"ontology ID {onto_id} not found in DataFrame")
    return ancestors


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index()
    if "ontology_id" in df.columns:
        return df.set_index("ontology_id")
    return df


def get_new_ontology_ids(
    registry: type[BioRecord], ontology_ids: Iterable[str], df: pd.DataFrame
) -> tuple[set[str], set[str]]:
    all_ontology_ids = set(ontology_ids) | get_all_ancestors(df, ontology_ids)
    existing_ontology_ids = set(
        registry.filter(ontology_id__in=all_ontology_ids).values_list(
            "ontology_id", flat=True
        )
    )
    return (all_ontology_ids - existing_ontology_ids), all_ontology_ids


def create_records(
    registry: type[BioRecord],
    df: pd.DataFrame,
    source_record: Source,
    organism: str | Organism | None = None,
) -> list[Record]:
    """Bulk-create records from a DataFrame skipping validation."""
    df = df.reset_index()
    df = df.rename(columns={"definition": "description"})

    if "parents" in df.columns:
        df = df.drop(columns=["parents"])

    df_records = df.to_dict(orient="records")

    if organism is None and is_organism_required(registry):
        organism = source_record.organism

    organism = create_or_get_organism_record(organism=organism, registry=registry)

    valid_fields = [f.name for f in registry._meta.fields]
    records = [
        registry(
            **{k: v for k, v in record.items() if k in valid_fields},
            **({"organism": organism} if "organism" in valid_fields else {}),
            source_id=source_record.id,
            _skip_validation=True,
        )
        for record in df_records
    ]

    return records


def create_link_records(
    registry: type[BioRecord], df: pd.DataFrame, records: list[Record]
) -> list[Record]:
    """Create link records.

    Args:
        registry: The model class of the records.
        df: The DataFrame with all ontology IDs and their parents.
        records: All records of the ontology.
    """
    source = records[0].source
    linkorm = registry.parents.through
    link_records = []
    registry_name_lower = registry.__name__.lower()

    # Create a dictionary for quick lookups
    record_dict = {r.ontology_id: r for r in records if r.source_id == source.id}

    for child_id, parents_ids in df["parents"].items():
        if len(parents_ids) == 0:
            continue
        child_record = record_dict.get(child_id)
        if not child_record:
            continue
        for parent_id in parents_ids:
            parent_record = record_dict.get(parent_id)
            if parent_record:
                link_records.append(
                    linkorm(
                        **{
                            f"from_{registry_name_lower}": child_record,
                            f"to_{registry_name_lower}": parent_record,
                        }
                    )
                )
    return link_records


def check_source_in_db(
    registry: type[BioRecord],
    source: Source,
    n_all: int = None,
    n_in_db: int = None,
) -> None:
    if not hasattr(registry, "source_id"):
        logger.warning(f"no `source` field in the registry {registry.__name__}!")
    else:
        n_all = n_all or registry.public(source=source).df().shape[0]
        # all records of the source in the database
        n_in_db = n_in_db or registry.filter(source=source).count()
        if n_in_db >= n_all:
            # make sure in_db is set to True if all records are in the database
            source.in_db = True
            source.save()
        else:
            source.in_db = False
            source.save()


def add_ontology_from_df(
    registry: type[BioRecord],
    ontology_ids: list[str] | None = None,
    organism: str | Organism | None = None,
    source: Source | None = None,
    ignore_conflicts: bool = True,
) -> None:
    """Add ontology records from source to the database based on ontology ids."""
    import lamindb as ln

    from bionty._source import get_source_record

    source_record = get_source_record(registry, organism=organism, source=source)
    public = registry.public(source=source_record)
    df = prepare_dataframe(public.df())

    if ontology_ids is None:
        logger.info(
            f"importing {registry.__name__} records from {public.source}, {public.version}"
        )
        df_new = df_all = df
    else:
        new_ontology_ids, all_ontology_ids = get_new_ontology_ids(
            registry, ontology_ids, df
        )
        df_new = df[df.index.isin(new_ontology_ids)]
        df_all = df[df.index.isin(all_ontology_ids)]

    # do not create records from obsolete terms
    if hasattr(registry, "ontology_id"):
        df_all = df_all[~df_all["name"].fillna("").str.startswith("obsolete")]

    n_all = df_all.shape[0]
    if n_all == 0:
        raise ValueError("No valid records to add!")

    # all records of the source in the database
    all_records = registry.filter(source=source_record).all()
    n_in_db = all_records.count()

    check_source_in_db(
        registry=registry,
        source=source_record,
        n_all=n_all,
        n_in_db=n_in_db,
    )

    records = create_records(registry, df_new, source_record, organism)
    new_records = [r for r in records if r._state.adding]
    if ontology_ids is None:
        logger.info(f"adding {len(new_records)} new records")
    registry.objects.bulk_create(new_records, ignore_conflicts=ignore_conflicts)

    all_records = registry.filter(
        source=source_record
    ).all()  # need to update all_records after bulk_create
    if hasattr(registry, "parents"):
        link_records = create_link_records(registry, df_all, all_records)
        new_link_records = [r for r in link_records if r._state.adding]
        if ontology_ids is None:
            logger.info(f"adding {len(new_link_records)} parents/children links")
        ln.save(new_link_records, ignore_conflicts=ignore_conflicts)

    if ontology_ids is None:
        logger.success("import is completed!")
        source_record.in_db = True
        source_record.save()


# used in save() to bulk save parents
def add_ontology(
    records: list[BioRecord],
    organism: str | Organism | None = None,
    source: Source | None = None,
    ignore_conflicts: bool = True,
) -> None:
    """Add ontology records from source to the database based on ontology ids."""
    registry = records[0]._meta.model
    source = source or records[0].source
    if (
        hasattr(registry, "organism_id")
        and not registry._meta.get_field("organism_id").null
    ):
        organism = organism or records[0].organism
    ontology_ids = [r.ontology_id for r in records]
    add_ontology_from_df(
        registry=registry,
        ontology_ids=ontology_ids,
        organism=organism,
        source=source,
        ignore_conflicts=ignore_conflicts,
    )

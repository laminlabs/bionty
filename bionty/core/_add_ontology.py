from typing import Iterable, List, Optional, Set, Tuple, Type, Union

import pandas as pd
from lnschema_core.models import Record

from bionty.models import BioRecord, Source


def get_all_ancestors(df: pd.DataFrame, ontology_ids: Iterable[str]) -> Set[str]:
    ancestors = set()

    def get_parents(onto_id: str) -> None:
        try:
            parents = df.at[onto_id, "parents"]
            for parent in parents:
                if parent not in ancestors:
                    ancestors.add(parent)
                    get_parents(parent)
        except KeyError:
            print(f"Warning: Ontology ID {onto_id} not found in DataFrame")

    for onto_id in ontology_ids:
        get_parents(onto_id)

    return ancestors


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index()
    if "ontology_id" in df.columns:
        return df.set_index("ontology_id")
    return df


def get_new_ontology_ids(
    registry: Type[BioRecord], ontology_ids: Iterable[str], df_all: pd.DataFrame
) -> Tuple[Set[str], Set[str]]:
    parents_ids = get_all_ancestors(df_all, ontology_ids)
    ontology_ids = set(ontology_ids) | parents_ids
    existing_ontology_ids = set(
        registry.filter(ontology_id__in=ontology_ids).values_list(
            "ontology_id", flat=True
        )
    )
    return (ontology_ids - existing_ontology_ids), ontology_ids


def create_records(
    registry: Type[BioRecord], df: pd.DataFrame, source_record: Source
) -> List[Record]:
    import lamindb as ln

    df_records = (
        df.reset_index()
        .rename(columns={"definition": "description"})
        .drop(columns=["parents"])
        .to_dict(orient="records")
    )
    try:
        ln.settings.creation.search_names = False
        records = [
            registry(**record, source_id=source_record.id) for record in df_records
        ]
    finally:
        ln.settings.creation.search_names = True

    return records


def create_link_records(
    registry: Type[BioRecord], df: pd.DataFrame, records: List[Record]
) -> List[Record]:
    source = records[0].source
    linkorm = registry.parents.through
    link_records = []
    for child_id, parents_ids in df["parents"].items():
        if len(parents_ids) == 0:
            continue
        child_record = next(
            (r for r in records if r.ontology_id == child_id and r.source == source),
            None,
        )
        if not child_record:
            continue
        for parent_id in parents_ids:
            parent_record = next(
                (
                    r
                    for r in records
                    if r.ontology_id == parent_id and r.source == source
                ),
                None,
            )
            if parent_record:
                link_records.append(
                    linkorm(
                        **{
                            f"from_{registry.__name__.lower()}": child_record,
                            f"to_{registry.__name__.lower()}": parent_record,
                        }
                    )
                )
    return link_records


def add_ontology_from_df(
    registry: Type[BioRecord],
    ontology_ids: Optional[List[str]] = None,
    organism: Union[str, Record, None] = None,
    source: Optional[Source] = None,
    ignore_conflicts: bool = True,
):
    import lamindb as ln

    from bionty._bionty import get_source_record

    public = registry.public(organism=organism, source=source)
    df = prepare_dataframe(public.df())

    if ontology_ids is None:
        df_new = df
        df_all = df
    else:
        new_ontology_ids, all_ontology_ids = get_new_ontology_ids(
            registry, ontology_ids, df
        )
        df_new = df[df.index.isin(new_ontology_ids)]
        df_all = df[df.index.isin(all_ontology_ids)]

    # TODO: consider StaticReference
    source_record = get_source_record(public)  # type:ignore
    # do not create records from obsolete terms
    records = [
        r
        for r in create_records(registry, df_new, source_record)
        if not r.name.startswith("obsolete")
    ]
    registry.objects.bulk_create(records, ignore_conflicts=ignore_conflicts)

    # all records of the source in the database
    all_records = registry.filter(source=source_record).all()
    link_records = create_link_records(registry, df_all, all_records)
    ln.save(link_records, ignore_conflicts=ignore_conflicts)

    if ontology_ids is None and len(records) > 0:
        source_record.in_db = True
        source_record.save()


def add_ontology(
    records: List[BioRecord],
    organism: Union[str, Record, None] = None,
    source: Optional[Source] = None,
    ignore_conflicts: bool = True,
):
    registry = records[0]._meta.model
    source = source or records[0].source
    if hasattr(registry, "organism_id"):
        organism = organism or records[0].organism
    ontology_ids = [r.ontology_id for r in records]
    add_ontology_from_df(
        registry=registry,
        ontology_ids=ontology_ids,
        organism=organism,
        source=source,
        ignore_conflicts=ignore_conflicts,
    )

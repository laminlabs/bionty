from __future__ import annotations

from typing import TYPE_CHECKING

from lamindb.base.utils import concrete_model
from lamindb.models import SQLRecord

from ._organism import (
    OrganismNotSet,
    create_or_get_organism_record,
)

if TYPE_CHECKING:
    from typing import Any

    from pandas import DataFrame

    import bionty.base as bt_base


def _none_if_missing(value: Any) -> Any:
    """Map a scalar missing value to None.

    Pandas 3 string dtypes use ``NaN`` as the missing sentinel. ``DataFrame.to_dict``
    and row access then yield ``float("nan")``, which Django text fields persist as
    the literal ``"nan"``. Non-scalars such as ``parents`` lists are unchanged.
    """
    import pandas as pd

    if pd.api.types.is_scalar(value) and pd.isna(value):
        return None
    return value


def get_source_record(
    registry: type[SQLRecord],
    organism: str | SQLRecord | None = None,
    source: SQLRecord | None = None,
) -> SQLRecord:
    """Get a Source record for a given BioRecord model."""
    from .models import Source

    if source is not None:
        return source

    organism_record = create_or_get_organism_record(
        organism=organism, registry=registry
    )
    if organism_record is None and registry.require_organism():
        raise OrganismNotSet(
            f"`organism` is required to get Source record for {registry.__name__}!"
        )

    entity_name = registry.__get_name_with_module__()
    filter_kwargs = {"entity": entity_name}
    if isinstance(organism_record, SQLRecord):
        filter_kwargs["organism"] = organism_record.name
    elif isinstance(organism, str):
        filter_kwargs["organism"] = (
            organism  # e.g. organism can be "all" for bionty.CellType
        )

    sources = Source.filter(**filter_kwargs).all()
    if len(sources) == 0:
        if isinstance(organism_record, SQLRecord):
            # try to match organism by scientific name
            filter_kwargs["organism"] = organism_record.scientific_name.lower()
            sources = Source.filter(**filter_kwargs).all()
            if len(sources) == 0:
                raise ValueError(f"No source record found for filter {filter_kwargs}")
        else:
            raise ValueError(f"No source record found for filter {filter_kwargs}")
    if len(sources) == 1:
        return sources.one()

    current_sources = sources.filter(currently_used=True).all()
    if len(current_sources) == 1:
        return current_sources.first()
    elif len(current_sources) > 1:
        if organism is None:
            # for bionty.Organism, in most cases we load from the vertebrates source because ncbitaxon is too big
            if entity_name == "bionty.Organism":
                current_sources_vertebrates = current_sources.filter(
                    organism="vertebrates"
                ).all()
                if len(current_sources_vertebrates) > 0:
                    return current_sources_vertebrates.first()
            # return source with organism="all"
            current_sources_all = current_sources.filter(organism="all").all()
            if len(current_sources_all) > 0:
                return current_sources_all.first()
        return current_sources.first()
    else:  # len(current_sources) == 0
        sources_all = sources.filter(organism="all").all()
        if len(sources_all) > 0:
            # return source with organism="all"
            return sources_all.first()
        return sources.first()


def source_matches_organism(source: SQLRecord, organism: SQLRecord) -> bool:
    """Return True if a Source record's organism matches an Organism record."""
    source_organism = getattr(source, "organism", None)
    if not source_organism or source_organism == "all":
        return True
    src_org_lower = source_organism.lower()
    org_name = getattr(organism, "name", None)
    if org_name and org_name.lower() == src_org_lower:
        return True
    sci_name = getattr(organism, "scientific_name", None)
    if sci_name and sci_name.lower() == src_org_lower:
        return True
    return False


def _source_contains_field_value(
    registry: type[SQLRecord],
    source_record: SQLRecord,
    field_name: str,
    value: Any,
) -> bool:
    """Return True if `source_record` contains `value` in `field_name`."""
    try:
        public_ontology = registry.public(source=source_record)
    except Exception:
        return False
    df = public_ontology.to_dataframe()
    if df.empty:
        return False
    if field_name in df.columns:
        return bool((df[field_name] == value).any())
    if df.index.name == field_name:
        return value in df.index
    return False


def find_source_for_field_value(
    registry: type[SQLRecord],
    field_name: str,
    value: Any,
) -> SQLRecord | None:
    """Search active Source records for `registry` to locate a unique field value.

    Checks `currently_used=True` sources first (ordered by `id`, prioritizing
    `bionty.settings.organism` if configured as a lookup hint), then falls back
    to the first non-`currently_used` source for any organism that has no
    `currently_used=True` source. Does not create `Organism` records while
    scanning.
    """
    from .core._settings import settings
    from .models import Source

    if not value:
        return None

    entity_name = concrete_model(registry).__get_name_with_module__()
    current_sources = list(
        Source.filter(entity=entity_name, currently_used=True).order_by("id")
    )
    covered_organisms = {s.organism for s in current_sources}
    fallback_sources = []
    seen_fallback: set[str] = set()
    for src in Source.filter(entity=entity_name, currently_used=False).order_by("id"):
        if src.organism not in covered_organisms and src.organism not in seen_fallback:
            fallback_sources.append(src)
            seen_fallback.add(src.organism)

    candidate_sources = current_sources + fallback_sources
    if not candidate_sources:
        return None

    # Use settings.organism as a fast-path ordering hint without restricting the search.
    configured_organism = settings.organism
    if configured_organism is not None:
        preferred = [
            s
            for s in candidate_sources
            if source_matches_organism(s, configured_organism)
        ]
        others = [s for s in candidate_sources if s not in preferred]
        candidate_sources = preferred + others

    for source_record in candidate_sources:
        if _source_contains_field_value(registry, source_record, field_name, value):
            return source_record
    return None


def filter_public_df_columns(
    registry: type[SQLRecord], public_ontology: bt_base.PublicOntology
) -> DataFrame:
    """Filter columns of public ontology to match the registry fields."""
    import pandas as pd

    def _prepare_public_df(
        registry: type[SQLRecord], bionty_df: DataFrame
    ) -> DataFrame:
        """Prepare the bionty DataFrame to match the registry fields."""
        if bionty_df.empty:
            return bionty_df
        if registry.__get_name_with_module__() == "bionty.Gene":
            # groupby ensembl_gene_id and concat ncbi_gene_ids
            groupby_id_col = (
                "stable_id"
                if "stable_id" in bionty_df and bionty_df["stable_id"].notna().all()
                else "ensembl_gene_id"
            )
            if groupby_id_col not in bionty_df:
                raise ValueError(
                    "public df must contain column 'ensembl_gene_id' or 'stable_id'"
                )
            bionty_df.drop(
                columns=["hgnc_id", "mgi_id", "index"], errors="ignore", inplace=True
            )
            agg_kwags = {}
            if "ncbi_gene_id" in bionty_df:
                bionty_df.drop_duplicates(
                    [groupby_id_col, "ncbi_gene_id"], inplace=True
                )
                bionty_df["ncbi_gene_id"] = bionty_df["ncbi_gene_id"].fillna("")
                bionty_df.rename(
                    columns={"ncbi_gene_id": "ncbi_gene_ids"}, inplace=True
                )
                agg_kwags["ncbi_gene_ids"] = "|".join
            for col in ["symbol", "biotype", "description", "synonyms"]:
                if col in bionty_df:
                    agg_kwags[col] = "first"  # type: ignore
            bionty_df = bionty_df.groupby(groupby_id_col).agg(agg_kwags).reset_index()

        # rename definition to description for the bionty registry in db
        if "definition" in bionty_df:
            bionty_df.rename(columns={"definition": "description"}, inplace=True)
        return bionty_df

    bionty_df: DataFrame = pd.DataFrame()
    if public_ontology is not None:
        registry_field_names = {i.name for i in registry._meta.fields}
        # parents needs to be added here as relationships aren't in fields
        registry_field_names.add("parents")
        bionty_df = _prepare_public_df(
            registry, public_ontology.to_dataframe().reset_index()
        )
        bionty_df = bionty_df.loc[:, bionty_df.columns.isin(registry_field_names)]
    return bionty_df

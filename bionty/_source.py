import pandas as pd
from lamindb.models import Record

import bionty.base as bt_base

from ._organism import create_or_get_organism_record


def get_source_record(
    registry: type[Record],
    organism: str | Record | None = None,
    source: Record | None = None,
) -> Record:
    """Get a Source record for a given BioRecord model."""
    from .models import Source

    if source is not None:
        return source

    organism_record = create_or_get_organism_record(organism, registry)

    entity_name = registry.__get_name_with_module__()
    filter_kwargs = {"entity": entity_name}
    if isinstance(organism_record, Record):
        filter_kwargs["organism"] = organism_record.name

    sources = Source.filter(**filter_kwargs).all()
    if len(sources) == 0:
        raise ValueError(f"No source record found for {entity_name}")
    if len(sources) == 1:
        return sources.one()

    current_sources = sources.filter(currently_used=True).all()
    if len(current_sources) == 1:
        return current_sources.first()
    elif len(current_sources) > 1:
        if organism is None:
            # for Organism, in most cases we load from the vertebrates source because ncbitaxon is too big
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


def filter_public_df_columns(
    model: type[Record], public_ontology: bt_base.PublicOntology
) -> pd.DataFrame:
    """Filter columns of public ontology to match the model fields."""

    def _prepare_public_df(model: type[Record], bionty_df: pd.DataFrame):
        """Prepare the bionty DataFrame to match the model fields."""
        if model.__get_name_with_module__() == "bionty.Gene":
            # groupby ensembl_gene_id and concat ncbi_gene_ids
            groupby_id_col = (
                "ensembl_gene_id" if "ensembl_gene_id" in bionty_df else "stable_id"
            )
            bionty_df.drop(
                columns=["hgnc_id", "mgi_id", "index"], errors="ignore", inplace=True
            )
            bionty_df.drop_duplicates([groupby_id_col, "ncbi_gene_id"], inplace=True)
            bionty_df["ncbi_gene_id"] = bionty_df["ncbi_gene_id"].fillna("")
            bionty_df = (
                bionty_df.groupby(groupby_id_col)
                .agg(
                    {
                        "symbol": "first",
                        "ncbi_gene_id": "|".join,
                        "biotype": "first",
                        "description": "first",
                        "synonyms": "first",
                    }
                )
                .reset_index()
            )
            bionty_df.rename(columns={"ncbi_gene_id": "ncbi_gene_ids"}, inplace=True)

        # rename definition to description for the bionty registry in db
        bionty_df.rename(columns={"definition": "description"}, inplace=True)
        return bionty_df

    bionty_df = pd.DataFrame()
    if public_ontology is not None:
        model_field_names = {i.name for i in model._meta.fields}
        # parents needs to be added here as relationships aren't in fields
        model_field_names.add("parents")
        bionty_df = _prepare_public_df(model, public_ontology.df().reset_index())
        bionty_df = bionty_df.loc[:, bionty_df.columns.isin(model_field_names)]
    return bionty_df

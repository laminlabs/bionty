from typing import Type

import pandas as pd
from lamin_utils import logger
from lamindb_setup.core._setup_bionty_sources import RENAME
from lnschema_core.models import Record

import bionty.base as bionty_base


def sync_all_sources_to_latest():
    """Sync up the Source registry with the latest available sources.

    Examples:
        >>> from bionty.core import sync_all_sources_to_latest
        >>> sync_all_sources_to_latest()
    """
    import lamindb as ln

    from bionty.models import Source

    try:
        ln.settings.creation.search_names = False
        records = Source.filter().all()
        df_sources = bionty_base.display_available_sources().reset_index()
        for _, row in df_sources.iterrows():
            kwargs = row.to_dict()
            for db_name, base_name in RENAME.items():
                if base_name in kwargs:
                    kwargs[db_name] = kwargs.pop(base_name)
            if not kwargs["entity"].startswith("bionty."):
                kwargs["entity"] = "bionty." + kwargs["entity"]
            record = records.filter(
                name=kwargs["name"],
                version=kwargs["version"],
                entity=kwargs["entity"],
                organism=kwargs["organism"],
            ).all()
            if len(record) == 0:
                record = Source(**kwargs)
                record.save()
                logger.success(f"added {record}")
            else:
                # update metadata fields
                record.update(**kwargs)
                logger.success(f"updated {record.one()}")
        logger.info("setting the latest version as currently_used...")
        set_latest_sources_as_currently_used()
        logger.success("synced up Source registry with the latest available sources")
        logger.warning("please reload your instance to reflect the updates!")
    finally:
        ln.settings.creation.search_names = True


def set_latest_sources_as_currently_used():
    """Set the currently_used column to True for the latest version of each source.

    Examples:
        >>> from bionty.core import set_latest_sources_as_currently_used
        >>> set_latest_sources_as_currently_used()
    """
    from bionty.models import Source

    records = Source.filter().all()
    df = records.df()
    for (entity, organism), df_group in df.groupby(["entity", "organism"]):
        latest_uid = df_group.sort_values("version", ascending=False).uid.iloc[0]
        records.filter(uid=latest_uid).update(currently_used=True)
        records.filter(entity=entity, organism=organism).exclude(uid=latest_uid).update(
            currently_used=False
        )


def filter_bionty_df_columns(
    model: Type[Record], public_ontology: bionty_base.PublicOntology
) -> pd.DataFrame:
    """Filter columns of public ontology to match the model fields."""
    bionty_df = pd.DataFrame()
    if public_ontology is not None:
        model_field_names = {i.name for i in model._meta.fields}
        # parents needs to be added here as relationships aren't in fields
        model_field_names.add("parents")
        bionty_df = _prepare_bionty_df(model, public_ontology.df().reset_index())
        bionty_df = bionty_df.loc[:, bionty_df.columns.isin(model_field_names)]
    return bionty_df


def _prepare_bionty_df(model: type[Record], bionty_df: pd.DataFrame):
    """Prepare the bionty DataFrame to match the model fields."""
    if model.__get_name_with_schema__() == "bionty.Gene":
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

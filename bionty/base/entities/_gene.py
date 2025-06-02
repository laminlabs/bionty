from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NamedTuple

import pandas as pd
from lamin_utils import logger

from bionty.base._public_ontology import PublicOntology
from bionty.base._settings import settings
from bionty.base.dev._doc_util import _doc_params
from bionty.base.dev._handle_sources import LAMINDB_INSTANCE_LOADED
from bionty.base.dev._io import s3_bionty_assets

from ._organism import Organism
from ._shared_docstrings import doc_entites

if TYPE_CHECKING:
    from collections.abc import Iterable


class MappingResult(NamedTuple):
    """Result of mapping legacy Ensembl gene IDs to current IDs.

    Attributes:
        mapped: Dictionary of successfully mapped old ensembl IDs to new ensembl IDs
        ambiguous: Dictionary of ambiguously mapped old ensembl IDs to new ensembl IDs - when
            a legacy ID maps to multiple current IDs
        unmapped: List of old ensembl IDs that couldn't be found in the current version
    """

    mapped: dict[str, str]
    ambiguous: dict[str, list[str]]
    unmapped: list[str]


@_doc_params(doc_entities=doc_entites)
class Gene(PublicOntology):
    """Gene.

    1. Ensembl
    https://www.ensembl.org/

    Args:
        {doc_entities}

    Notes:
        Biotypes: https://www.ensembl.org/info/genome/genebuild/biotypes.html
        Gene Naming: https://www.ensembl.org/info/genome/genebuild/gene_names.html
    """

    def __init__(
        self,
        organism: Literal["human", "mouse", "saccharomyces cerevisiae"] | None = None,
        source: Literal["ensembl"] | None = None,
        version: Literal["release-109", "release-110", "release-111", "release-112"]
        | None = None,
        **kwargs,
    ):
        self.taxa = kwargs.pop("taxa", "vertebrates")
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            ols_supported=False,
            **kwargs,
        )

    def _load_df(self):
        if self.source == "ensembl":
            df = super()._load_df()
            if df.empty:
                # Load the Ensembl gene table
                df = EnsemblGene(
                    organism=self._organism, version=self._version, taxa=self.taxa
                ).download_df()
                df.to_parquet(self._local_parquet_path)
            return df
        return super()._load_df()

    # TODO: generalize this to all sources
    def register_source_in_lamindb(self):
        """Register the source in lamindb."""
        if not self._df.empty and LAMINDB_INSTANCE_LOADED:
            import bionty as bt

            # Register the source in lamindb
            source_kwargs = {
                "entity": "bionty.Gene",
                "organism": self._organism,
                "name": self.source,
                "version": self._version,
            }
            source = bt.Source.filter(**source_kwargs).one_or_none()
            if source is None:
                source = bt.Source(**source_kwargs, description="Ensembl").save()
                bt.Gene.add_source(source, df=self._df)
            else:
                logger.warning("source already exists!")

    def map_legacy_ids(self, values: Iterable) -> MappingResult:
        """Convert legacy ids to current IDs.

        This only works if the legacy ensembl ID has a reference to the current ensembl ID.
        It is possible that the HGNC IDs are identical, and the genomic locations are very close,
        but a mapping may still be absent.

        Args:
            values: Legacy ensemble gene IDs of any version

        Example::

            import bionty as bt

            gene = bt.base.Gene()
            gene.map_legacy_genes(["ENSG00000260150", "ENSG00000260587"])
        """
        if self.source != "ensembl":
            raise NotImplementedError
        if isinstance(values, str):
            values = [values]
        ensembl = EnsemblGene(organism=self.organism, version=self.version)
        legacy_df_filename = f"df-legacy_{self.organism}__{self.source}__{self.version}__{self.__class__.__name__}.parquet"
        legacy_df_localpath = settings.dynamicdir / legacy_df_filename
        s3_bionty_assets(
            filename=legacy_df_filename,
            assets_base_url="s3://bionty-assets",
            localpath=legacy_df_localpath,
        )
        try:
            results = pd.read_parquet(legacy_df_localpath)
        except FileNotFoundError:
            raise NotImplementedError from None
        results = results[results.old_stable_id.isin(values)].copy()
        return ensembl._process_convert_result(results, values=values)


class EnsemblGene:
    def __init__(
        self,
        organism: str,
        version: str,
        taxa: Literal[
            "vertebrates", "bacteria", "fungi", "metazoa", "plants", "all"
        ] = "vertebrates",
    ) -> None:
        """Ensembl Gene using direct PyMySQL connection.

        Args:
            organism: Name of the organism
            version: Name of the ensembl DB version, e.g. "release-110"
            taxa: The taxa of the organism to fetch genes for.
        """
        self._import()

        self._organism = (
            Organism(source="ensembl", version=version, taxa=taxa)  # type:ignore
            .lookup()
            .dict()
            .get(organism)
        )

        # Determine port based on taxa
        self._port = 4157 if taxa == "plants" else 3306
        self._host = "ensembldb.ensembl.org"
        self._db = self._organism.core_db
        self._conn = None

    def _import(self):
        try:
            # Check for required dependencies
            import pymysql  # type: ignore
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "To query from the Ensembl database, please run:\npip install pymysql"
            ) from None

    def _get_connection(self):
        """Get a PyMySQL connection to the Ensembl database."""
        import pymysql

        if self._conn is None or not self._conn.open:
            self._conn = pymysql.connect(
                host=self._host,
                port=self._port,
                user="anonymous",
                password="",
                database=self._db,
            )
        return self._conn

    def _execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query using PyMySQL and return results as DataFrame."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                return pd.DataFrame(cursor.fetchall(), columns=columns)
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            conn.close()
            self._conn = None
            raise e

    def external_dbs(self) -> pd.DataFrame:
        """Get all external database information."""
        return self._execute_query("SELECT * FROM external_db")

    def download_df(
        self, external_db_names: dict[str, str] | None = None
    ) -> pd.DataFrame:
        """Fetch gene table from Ensembl database.

        Args:
            external_db_names: {external database name : df column name}, see `.external_dbs()`
                Default is {"EntrezGene": "ncbi_gene_id"}.
        """
        query_core = """
        SELECT gene.stable_id, xref.display_label, gene.biotype, gene.description, external_synonym.synonym
        FROM gene
        LEFT JOIN xref ON gene.display_xref_id = xref.xref_id
        LEFT JOIN external_synonym ON gene.display_xref_id = external_synonym.xref_id
        """
        # Make sure to always include EntrezGene
        external_db_names = {
            **{"EntrezGene": "ncbi_gene_id"},
            **(external_db_names or {}),
        }
        external_db_names_str = ", ".join(
            [f"'{name}'" for name in external_db_names.keys()]
        )

        query_external = f"""
        SELECT gene.stable_id, object_xref.xref_id, xref.dbprimary_acc, external_db.db_name
        FROM gene
        LEFT JOIN object_xref ON gene.gene_id = object_xref.ensembl_id
        LEFT JOIN xref ON object_xref.xref_id = xref.xref_id
        LEFT JOIN external_db ON xref.external_db_id = external_db.external_db_id
        WHERE object_xref.ensembl_object_type = 'Gene' AND external_db.db_name IN ({external_db_names_str})
        """

        # Query for the basic gene annotations
        results_core = self._execute_query(query_core)
        logger.info("fetching records from the core DB...")

        # Aggregate metadata based on ensembl stable_id
        results_core_group = results_core.groupby("stable_id").agg(
            {
                "display_label": "first",
                "biotype": "first",
                "description": "first",
                "synonym": lambda x: "|".join([i for i in set(x) if i is not None]),
            }
        )

        # Query for external ids
        results_external = self._execute_query(query_external)
        logger.info("fetching records from the external DBs...")

        def add_external_db_column(
            df: pd.DataFrame, ext_db: str, df_col: str
        ) -> pd.DataFrame:
            # Filter by the external database name
            ext = (
                results_external[results_external["db_name"] == ext_db]
                .drop_duplicates(["stable_id", "dbprimary_acc"])
                .drop(columns=["xref_id", "db_name"])
            )
            ext.rename(columns={"dbprimary_acc": df_col}, inplace=True)
            ext = ext.set_index("stable_id")

            # Check for duplicates
            dup = ext[ext.index.duplicated(keep=False)]
            if dup.shape[0] > 0:
                logger.warning(
                    f"duplicated #rows ensembl_gene_id with {df_col}: {dup.shape[0]}"
                )

            # Merge with existing dataframe
            df_merge = df.merge(ext, left_index=True, right_index=True, how="outer")
            return df_merge

        # Add all external database columns (including EntrezGene)
        df = results_core_group.copy()
        for ext_db, df_col in external_db_names.items():
            df = add_external_db_column(df=df, ext_db=ext_db, df_col=df_col)

        # Finalize the dataframe
        df = df.reset_index().rename(
            columns={
                "stable_id": "ensembl_gene_id",
                "display_label": "symbol",
                "synonym": "synonyms",
            }
        )

        # Define the columns we want to prioritize (they'll appear first in the dataframe)
        priority_columns = [
            "ensembl_gene_id",
            "symbol",
            "ncbi_gene_id",
            "biotype",
            "description",
            "synonyms",
        ]
        # Create a new ordered list with priority columns first, then any remaining columns
        all_columns = priority_columns + [
            col for col in df.columns if col not in priority_columns
        ]
        df_res = df[all_columns].copy()

        # Remove rows with null ensembl_gene_id
        df_res = df_res[df_res["ensembl_gene_id"].notna()]

        # Separate IDs: ensembl_gene_id for ENS-prefixed, stable_id for others
        logger.debug("Separating IDs based on ENS prefix")

        # Create a mask for ENS-prefixed IDs
        is_ens = df_res["ensembl_gene_id"].str.startswith("ENS")
        # If there are any non-ENS IDs, add a stable_id column
        if not all(is_ens):
            logger.warning(
                f"Found {(~is_ens).sum()} IDs without ENS prefix, moving these to stable_id column."
            )
            # Add stable_id column if it doesn't exist
            if "stable_id" not in df_res.columns:
                df_res.insert(0, "stable_id", None)
            # Move non-ENS IDs to stable_id column
            df_res.loc[~is_ens, "stable_id"] = df_res.loc[~is_ens, "ensembl_gene_id"]
            # Clear the ensembl_gene_id for these rows
            df_res.loc[~is_ens, "ensembl_gene_id"] = None

        # Sort by stable_id first (if it exists and has values), then by ensembl_gene_id
        if "stable_id" in df_res.columns and df_res["stable_id"].notna().any():
            df_res = df_res.sort_values(
                ["stable_id", "ensembl_gene_id"], na_position="last"
            ).reset_index(drop=True)
        else:
            df_res = df_res.sort_values("ensembl_gene_id").reset_index(drop=True)

        if "description" in df_res.columns:
            df_res["description"] = df_res["description"].str.replace(
                r"\[.*?\]", "", regex=True
            )
        logger.important(f"downloaded Gene table containing {df_res.shape[0]} entries.")
        return df_res

    def download_legacy_ids_df(
        self, df: pd.DataFrame, col: str | None = None
    ) -> pd.DataFrame:
        """Download legacy Ensembl gene IDs for the current IDs.

        Args:
            df: DataFrame containing Ensembl gene IDs
            col: Column name in df that contains the Ensembl gene IDs

        Returns:
            DataFrame containing mapping between current and legacy IDs
        """
        col = "ensembl_gene_id" if col is None else col

        # Filter out None/NaN values to prevent SQL errors
        valid_ids = df[df[col].notna()][col].tolist()

        # Handle empty list case
        if not valid_ids:
            logger.warning(
                "No valid IDs found in the specified column. Returning empty DataFrame."
            )
            return pd.DataFrame()

        # Format for SQL IN clause - need to add quotes around each ID
        formatted_ids = "(" + ", ".join(f"'{id}'" for id in valid_ids) + ")"

        # Construct and execute query
        query = f"""
            SELECT * FROM stable_id_event
            JOIN mapping_session USING (mapping_session_id)
            WHERE type = 'gene'
            AND new_stable_id IN {formatted_ids}
            AND score > 0
            AND old_stable_id != new_stable_id
        """
        # Execute the query and fetch results
        try:
            results = self._execute_query(query)
            logger.info(f"Downloaded {len(results)} legacy ID mappings")
            return results
        except Exception as e:
            logger.error(f"Error querying legacy IDs: {e}")
            # Return an empty DataFrame rather than failing
            return pd.DataFrame()

    def map_legacy_ids(self, values: Iterable, df: pd.DataFrame) -> MappingResult:
        """Maps legacy gene IDs to current Ensembl gene IDs.

        Takes legacy gene IDs and maps them to current Ensembl IDs by querying the Ensembl database.
        Returns mapping results categorized as unique mappings,
        ambiguous mappings (one legacy ID maps to multiple current IDs), and unmapped IDs.

        Args:
            values: Single gene ID string or iterable of gene ID strings to map
            df: DataFrame containing current Ensembl gene IDs in 'ensembl_gene_id' column

        Example::

            map_legacy_ids(['ENSG00000139618'], df)
            #> MappingResult(
            #>     mapped={'ENSG00000139618': 'ENSG00000012048'},
            #>     ambiguous={},
            #>     unmapped=[],
            )
        """
        # Handle single string input
        if isinstance(values, str):
            values = [values]

        # Convert values to list if it's another iterable type
        values_list = list(values)

        # Format legacy gene IDs for SQL
        legacy_genes = "(" + ", ".join(f"'{gene}'" for gene in values_list) + ")"

        # Filter out None/NaN values from current IDs
        valid_current_ids = df[df["ensembl_gene_id"].notna()][
            "ensembl_gene_id"
        ].tolist()

        # Handle empty list case
        if not valid_current_ids:
            logger.warning(
                "No valid current IDs found. Returning empty mapping result."
            )
            return MappingResult(mapped={}, ambiguous={}, unmapped=values_list)

        # Format current IDs for SQL
        current_ids_sql = "(" + ", ".join(f"'{id}'" for id in valid_current_ids) + ")"

        try:
            # Query the ensembl database
            query = f"""
                SELECT * FROM stable_id_event
                JOIN mapping_session USING (mapping_session_id)
                WHERE type = 'gene'
                AND old_stable_id IN {legacy_genes}
                AND new_stable_id IN {current_ids_sql}
                AND old_stable_id != new_stable_id
            """

            results = self._execute_query(query)
            return self._process_convert_result(results, values_list)
        except Exception as e:
            logger.error(f"Error mapping legacy IDs: {e}")
            return MappingResult(mapped={}, ambiguous={}, unmapped=values_list)

    def _process_convert_result(
        self,
        results: pd.DataFrame,
        values: Iterable,
    ) -> MappingResult:
        """Process the results of a legacy ID mapping query.

        Args:
            results: DataFrame with mapping results
            values: Original input values to map

        Returns:
            A MappingResult object with mapped, ambiguous, and unmapped entries
        """
        # Unique mappings
        mapper = (
            results.drop_duplicates(["old_stable_id"], keep=False)
            .set_index("old_stable_id")["new_stable_id"]
            .to_dict()
        )

        # Ambiguous mappings (one legacy ID maps to multiple current IDs)
        ambiguous = (
            results[~results["old_stable_id"].isin(mapper)][
                ["old_stable_id", "new_stable_id"]
            ]
            .groupby("old_stable_id", group_keys=False)["new_stable_id"]
            .apply(list)
            .to_dict()
        )

        # Unmappable IDs (input IDs not found in results)
        unmapped = set(values).difference(results["old_stable_id"])

        return MappingResult(
            mapped=mapper, ambiguous=ambiguous, unmapped=list(unmapped)
        )

    def __del__(self):
        """Clean up database connection when the object is destroyed."""
        if hasattr(self, "_conn") and self._conn is not None and self._conn.open:
            self._conn.close()

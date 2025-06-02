from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING, Literal

import numpy as np
import pandas as pd
from lamin_utils import logger
from lamin_utils._lookup import Lookup

from ._settings import check_datasetdir_exists, check_dynamicdir_exists, settings
from .dev._handle_sources import LAMINDB_INSTANCE_LOADED
from .dev._io import s3_bionty_assets, url_download

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from bionty.base._ontology import Ontology

    from .dev import InspectResult


def encode_filenames(
    organism: str, name: str, version: str, entity: str
) -> tuple[str, str]:
    """Encode names of the cached files."""
    parquet_filename = f"df_{organism}__{name}__{version}__{entity}.parquet"
    ontology_filename = f"ontology_{organism}__{name}__{version}__{entity}".replace(
        " ", "_"
    )

    return parquet_filename, ontology_filename


class PublicOntology:
    """PublicOntology object."""

    def __init__(
        self,
        source: str | None = None,
        version: str | None = None,
        organism: str | None = None,
        *,
        include_id_prefixes: dict[str, list[str]] | None = None,
        include_rel: str | None = None,
        entity: str | None = None,
        ols_supported: bool = True,
    ):
        self._entity = entity or self.__class__.__name__
        self._ols_supported = ols_supported

        # search in all available sources to get url
        try:
            self._fetch_sources()
            self._source_dict = self._match_sources(
                self._all_sources,
                name=source,
                version=version,
                organism=organism,
            )

        except (ValueError, KeyError) as e:
            if LAMINDB_INSTANCE_LOADED:
                # to support StaticSource in lamindb
                self._source_dict = {}
                pass
            else:
                raise e

        self._organism = self._source_dict.get("organism") or organism
        self._source = self._source_dict.get("name") or source
        self._version = self._source_dict.get("version") or version

        self._get_url()
        self._set_file_paths()
        self.include_id_prefixes = include_id_prefixes
        self.include_rel = include_rel

        # df is only read into memory at the init to improve performance
        df = self._load_df()
        # self._df has no index
        if not df.empty and df.index.name is not None:
            df = df.reset_index()
        self._df: pd.DataFrame = df

        # set column names/fields as attributes
        for col_name in self._df.columns:
            try:
                setattr(self, col_name, PublicOntologyField(self, col_name))
            # Some fields of an ontology (e.g. Gene) are not PublicOntology class attributes and must be skipped.
            except AttributeError:
                pass

    def __repr__(self) -> str:
        # fmt: off
        representation = (
            f"PublicOntology\n"
            f"Entity: {self._entity}\n"
            f"Organism: {self.organism}\n"
            f"Source: {self.source}, {self.version}\n"
            f"#terms: {self._df.shape[0] if hasattr(self, '_df') else ''}\n\n"
        )
        # fmt: on
        return representation

    @property
    def organism(self):
        """The `name` of `Organism`."""
        return self._organism

    @property
    def source(self):
        """Name of the source."""
        return self._source

    @property
    def version(self):
        """Version of the source."""
        return self._version

    @property
    def fields(self) -> set:
        """All PublicOntology entity fields."""
        blacklist = {"include_id_prefixes", "include_rel"}
        fields = {
            field
            for field in vars(self)
            if not callable(getattr(self, field)) and not field.startswith("_")
        }
        return fields - blacklist

    def _download_ontology_file(self, localpath: Path, url: str) -> None:
        """Download ontology source file to _local_ontology_path."""
        if not localpath.exists():
            logger.info(f"downloading {self._entity} ontology source file...")
            if not url:
                raise ValueError(
                    f"No source url is available for {self._entity} ontology."
                )
            self._url_download(url, localpath)

    def _fetch_sources(self) -> None:
        from .dev._handle_sources import parse_sources_yaml

        self._all_sources = parse_sources_yaml(url_pattern=True)

    def _match_sources(
        self,
        ref_sources: pd.DataFrame,
        name: str | None = None,
        version: str | None = None,
        organism: str | None = None,
    ) -> dict[str, str]:
        """Match a source record based on passed organism, name and version."""
        # Build filter conditions from non-None parameters
        conditions = {}
        if organism is not None:
            conditions["organism"] = organism
        if name is not None:
            conditions["name"] = name

        # If no parameters provided, use the first source
        if not conditions:
            rows = ref_sources
        else:
            # Filter dataframe using all conditions
            query = True
            for col, value in conditions.items():
                query = query & (ref_sources[col] == value)
            rows = ref_sources[query]

        # For ensembl, need to filter by entity
        if not rows.empty and rows.head(1)["name"].values[0] == "ensembl":
            rows = rows[rows["entity"] == self._entity.split(".")[-1]]

        row = rows.head(1)

        # If no records matched
        if row.empty:
            url = None
            ontology_version = None
            if self._ols_supported:
                # try to get the ontology url
                if name and name not in ref_sources["name"].values:
                    from ._ontology_url import get_ontology_url

                    try:
                        url, ontology_version = get_ontology_url(
                            prefix=name, version=version
                        )
                        meta_dict = {
                            "name": name,
                            "version": ontology_version,
                            "organism": organism or "all",
                            "url": url,
                            "description": f"{name} Ontology",
                            "source_website": f"https://www.ebi.ac.uk/ols/ontologies/{name}",
                        }

                        return meta_dict
                    except Exception:
                        pass
            if url is None:
                raise ValueError(
                    f"No source is available with {conditions}\n"
                    "Check `.display_sources()`"
                )

        # Build result and replace version placeholder in URL
        meta_dict = row.iloc[0].to_dict()
        ver = version or meta_dict.get("version")
        meta_dict["version"] = ver
        meta_dict["url"] = meta_dict["url"].replace("{version}", ver)
        meta_dict.pop("entity", None)  # remove entity from the dict
        return meta_dict

    @check_dynamicdir_exists
    def _url_download(self, url: str, localpath: Path) -> None:
        """Download file from url to dynamicdir _local_ontology_path."""
        # Try to download from s3://bionty-assets
        s3_bionty_assets(
            filename=self._ontology_filename,  # type: ignore
            assets_base_url="s3://bionty-assets",
            localpath=localpath,
        )

        # If the file is not available, download from the url
        if not localpath.exists():
            logger.info(f"downloading {self._entity} source file from: {url}")
            _ = url_download(url, localpath)

    def _get_url(self):
        """Get the url of the source."""
        self._url: str = self._source_dict.get("url", "")

    @check_datasetdir_exists
    def _set_file_paths(self) -> None:
        """Sets local file paths."""
        # parquet file name, ontology source file name
        self._parquet_filename, self._ontology_filename = encode_filenames(
            organism=self.organism,
            name=self.source,
            version=self.version,
            entity=self._entity,
        )
        self._local_parquet_path: Path = settings.dynamicdir / self._parquet_filename

        # user provide reference table as the url in parquet format
        if self._url.endswith(".parquet"):
            # no local ontology source file
            self._local_ontology_path = None  # type:ignore
            if not self._url.startswith("s3://bionty-assets/"):
                # will not try to download the parquet file from s3://bionty-assets
                self._parquet_filename = None  # type:ignore
        else:
            self._local_ontology_path = settings.dynamicdir / self._ontology_filename

        # ontology source not present in the sources.yaml file
        # these entities don't have ontology files
        if not self._url and not self._ols_supported:
            self._local_ontology_path = None

    def _get_default_field(self, field: PublicOntologyField | str | None = None) -> str:
        """Default to name field."""
        if field is None:
            if "name" in self._df.columns:
                field = "name"
            elif "symbol" in self._df.columns:
                field = "symbol"
            else:
                raise ValueError("Please specify a field!")
        field = str(field)
        if field not in self._df.columns:
            raise AssertionError(f"No {field} column exists!")
        return field

    def _load_df(self) -> pd.DataFrame:
        if self._parquet_filename is None:
            self._url_download(self._url, self._local_parquet_path)
        else:
            s3_bionty_assets(
                filename=self._parquet_filename,
                assets_base_url="s3://bionty-assets",
                localpath=self._local_parquet_path,
            )
        # If download is not possible, write a parquet file of the ontology df
        if not self._url.endswith(".parquet"):
            if not self._local_parquet_path.exists():
                pronto = self.to_pronto(mute=True)
                if pronto is not None:
                    df = pronto.to_df(
                        source=self.source,
                        include_id_prefixes=self.include_id_prefixes,
                        include_rel=self.include_rel,
                    )
                    df.to_parquet(self._local_parquet_path)

        if self._local_parquet_path.exists():
            # Loading the parquet file resets the index
            return pd.read_parquet(self._local_parquet_path)
        return pd.DataFrame()

    def to_pronto(self, mute: bool = False) -> Ontology:  # type:ignore
        """The Pronto Ontology object.

        See: https://pronto.readthedocs.io/en/stable/api/pronto.Ontology.html
        """
        if importlib.util.find_spec("pronto") is None:  # type:ignore
            raise ImportError(
                "pronto package is not installed. Please install it using: pip install pronto."
            )

        from ._ontology import Ontology

        if self._local_ontology_path is None:
            if not mute:
                logger.error(f"{self._entity} has no Pronto Ontology object!")
        else:
            self._download_ontology_file(
                localpath=self._local_ontology_path,
                url=self._url,
            )
            return Ontology(handle=self._local_ontology_path)

    def df(self) -> pd.DataFrame:
        """Pandas DataFrame of the ontology.

        Returns:
            A Pandas DataFrame of the ontology.

        Example::

            import bionty.base as bt_base

            bt_base.Gene().df()
        """
        if "ontology_id" in self._df.columns:
            # Filter ontology_id by source prefix
            filtered_df = self._df[
                self._df["ontology_id"]
                .str.upper()
                .str.startswith(f"{self._source.upper()}:")
            ].set_index("ontology_id")
            if not filtered_df.empty:
                return filtered_df
            return self._df.set_index("ontology_id")
        else:
            return self._df

    def validate(
        self,
        values: Iterable,
        field: PublicOntologyField,
        *,
        mute: bool = False,
        **kwargs,
    ) -> np.ndarray:
        """Validate a list of values against a field of entity reference.

        Args:
            values: Identifiers that will be checked against the field.
            field: The PublicOntologyField of the ontology to compare against.
                Examples are 'ontology_id' to map against the source ID
                or 'name' to map against the ontologies field names.
            mute: Whether to suppress logging. Defaults to False.
            kwargs: Used for backwards compatibility and return types.

        Returns:
            A boolean array indicating compliance validation.

        Example::

            import bionty.base as bt_base

            public = bt_base.Gene()
            gene_symbols = ["A1CF", "A1BG", "FANCD1", "FANCD20"]
            public.validate(gene_symbols, field=public.symbol)
        """
        from lamin_utils._inspect import validate

        if isinstance(values, str):
            values = [values]

        # in bionty-base passed django fields do not resolve properly to a string
        if str(field).startswith("FieldAttr"):
            field_str = str(field).split(".")[-1][:-1]
        else:
            field_str = str(field)
        field_values = self._df[str(field_str)]

        return validate(
            identifiers=values,
            field_values=field_values,
            case_sensitive=True,
            mute=mute,
            **kwargs,
        )

    def inspect(
        self,
        values: Iterable,
        field: PublicOntologyField,
        *,
        mute: bool = False,
        **kwargs,
    ) -> InspectResult:
        """Inspect a list of values against a field of entity reference.

        Args:
            values: Identifiers that will be checked against the field.
            field: The PublicOntologyField of the ontology to compare against.
                Examples are 'ontology_id' to map against the source ID
                or 'name' to map against the ontologies field names.
            return_df: Whether to return a Pandas DataFrame.
            mute: Whether to suppress logging. Defaults to False.
            kwargs: Used for backwards compatibility and return types.

        Returns:
            - A Dictionary of "validated" and "not_validated" identifiers
            - If `return_df`: A DataFrame indexed by identifiers with a boolean
                `__validated__` column indicating compliance validation.

        Example::

            import bionty.base as bt_base

            public = bt_base.Gene()
            gene_symbols = ["A1CF", "A1BG", "FANCD1", "FANCD20"]
            public.inspect(gene_symbols, field=public.symbol)
        """
        from lamin_utils._inspect import inspect

        if isinstance(values, str):
            values = [values]

        return inspect(
            df=self._df,
            identifiers=values,
            field=str(field),
            mute=mute,
            **kwargs,
        )

    # unfortunately, the doc string here is duplicated with ORM.standardize
    def standardize(
        self,
        values: Iterable,
        field: PublicOntologyField | str | None = None,
        *,
        return_field: str = None,
        return_mapper: bool = False,
        case_sensitive: bool = False,
        mute: bool = False,
        keep: Literal["first", "last", False] = "first",
        synonyms_field: PublicOntologyField | str = "synonyms",
    ) -> dict[str, str] | list[str]:
        """Convert into standardized names.

        Args:
            values: `Iterable` Synonyms that will be standardized.
            field: `Optional[str]` The field representing the standardized names.
            return_field: `Optional[str]` The field to return. Defaults to field.
            return_mapper: `bool = False` If `True`, returns `{input_synonym1:
                standardized_name1}`.
            case_sensitive: `bool = False` Whether the mapping is case sensitive.
            keep: {'first', 'last', False}, default 'first'.
                When a synonym maps to multiple standardized values, determines
                which duplicates to mark as `pandas.DataFrame.duplicated`.

                - "first": returns the first mapped standardized value
                - "last": returns the last mapped standardized value
                - False: returns all mapped standardized value
            mute: Whether to mute logging. Defaults to False.
            synonyms_field: `str = "synonyms"` A field containing the concatenated synonyms.

        Returns:
            If `return_mapper` is `False`: a list of standardized names. Otherwise,
            a dictionary of mapped values with mappable synonyms as keys and
            standardized names as values.

        Example::

            import bionty.base as bt_base

            public = bt_base.Gene()
            gene_symbols = ["A1CF", "A1BG", "FANCD1", "FANCD20"]
            standardized_symbols = public.standardize(gene_symbols, public.symbol)
        """
        from lamin_utils._standardize import standardize as map_synonyms

        if isinstance(values, str):
            values = [values]

        return map_synonyms(
            df=self._df,
            identifiers=values,
            field=self._get_default_field(field),
            return_field=self._get_default_field(return_field),
            return_mapper=return_mapper,
            case_sensitive=case_sensitive,
            mute=mute,
            keep=keep,
            synonyms_field=str(synonyms_field),
        )

    def lookup(self, field: PublicOntologyField | str | None = None) -> tuple:
        """An auto-complete object for a PublicOntology field.

        Args:
            field: The field to lookup the values for.
                Defaults to 'name'.

        Returns:
            A NamedTuple of lookup information of the field values.

        Example::

            import bionty.base as bt_base

            lookup = bt_base.CellType().lookup()
            lookup.cd103_positive_dendritic_cell
            lookup_dict = lookup.dict()
            lookup['CD103-positive dendritic cell']
        """
        return Lookup(
            df=self._df,
            field=self._get_default_field(field),
            tuple_name=self._entity,
            prefix="bt",
        ).lookup()

    def search(
        self,
        string: str,
        *,
        field: PublicOntologyField | str | list[PublicOntologyField | str] = None,
        limit: int | None = None,
        case_sensitive: bool = False,
    ):
        """Search a given string against a PublicOntology field or fields.

        Args:
            string: The input string to match against the field values.
            field: The PublicOntologyField or several fileds of the ontology
                the input string is matching against. Search all fields containing strings by default.
            limit: Maximum amount of top results to return. If None, return all results.
            case_sensitive: Whether the match is case sensitive.

        Returns:
            Ranked search results.

        Example::

            import bionty.base as bt_base

            public = bt_base.CellType()
            public.search("gamma delta T cell")
        """
        from lamin_utils._search import search

        if isinstance(field, PublicOntologyField):
            field = field.name
        elif field is not None and not isinstance(field, str):
            field = [f.name if isinstance(f, PublicOntologyField) else f for f in field]

        result = search(
            df=self._df,
            string=string,
            field=field,
            limit=limit,
            case_sensitive=case_sensitive,
        )
        if "ontology_id" in result.columns:
            result = result.set_index("ontology_id")
        return result

    def diff(
        self, compare_to: PublicOntology, **kwargs
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Determines a diff between two PublicOntology objects' ontologies.

        Args:
            compare_to: PublicOntology object that must be of the same class as the calling object.
            kwargs: Are passed to pd.DataFrame.compare()

        Returns:
            A tuple of two DataFrames:
            1. New entries.
            2. A pd.DataFrame.compare result which denotes all changes in `self` and `other`.

        Example::

            import bionty.base as bt_base

            public_1 = bt_base.Disease(source="mondo", version="2023-04-04")
            public_2 = bt_base.Disease(source="mondo", version="2023-04-04")
            new_entries, modified_entries = public_1.diff(public_2)
            print(new_entries.head())
            print(modified_entries.head())
        """
        if type(self) is not type(compare_to):
            raise ValueError("Both PublicOntology objects must be of the same class.")

        if not self.source == compare_to.source:
            raise ValueError("Both PublicOntology objects must use the same source.")

        if self.version == compare_to.version:
            raise ValueError("The versions of the PublicOntology objects must differ.")

        # The 'parents' column (among potentially others) contain Numpy array values.
        # We transform them to tuples to determine the diff.
        def _convert_arrays_to_tuples(arr):  # pragma: no cover
            if isinstance(arr, np.ndarray):
                return tuple(arr)
            else:
                return arr

        for bt_obj in [self, compare_to]:
            for column in bt_obj.df().columns:
                if any(isinstance(val, np.ndarray) for val in bt_obj.df()[column]):
                    bt_obj._df[column] = bt_obj.df()[column].apply(
                        _convert_arrays_to_tuples
                    )

        # New entries
        new_entries = pd.concat([self.df(), compare_to.df()]).drop_duplicates(
            keep=False
        )

        # Changes in existing entries
        common_index = self.df().index.intersection(compare_to.df().index)
        self_df_common = self.df().loc[common_index]
        compare_to_df_common = compare_to.df().loc[common_index]
        modified_entries = self_df_common.compare(compare_to_df_common, **kwargs)

        logging.info(f"{len(new_entries)} new entries were added.")
        logging.info(f"{len(modified_entries)} entries were modified.")

        return new_entries, modified_entries


class InvalidParamError(Exception):
    """Custom exception for PublicOntology parameter validation errors."""

    pass


class PublicOntologyField:
    """Field of a PublicOntology model."""

    def __init__(self, parent: PublicOntology, name: str):
        self.parent = parent
        self.name = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

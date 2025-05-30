from __future__ import annotations

from typing import Literal

import pandas as pd

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params
from bionty.base.dev._io import s3_bionty_assets
from bionty.base.entities._shared_docstrings import organism_removed


@_doc_params(doc_entities=organism_removed)
class Organism(PublicOntology):
    """Organism.

    1. Organism ontology
    https://www.ensembl.org/index.html

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        taxa: (
            Literal["vertebrates", "bacteria", "fungi", "metazoa", "plants", "all"]
            | None
        ) = None,
        source: Literal["ensembl", "ncbitaxon"] | None = None,
        version: (
            Literal[
                "2023-06-20",
                "release-57",
                "release-112",
            ]
            | None
        ) = None,
        **kwargs,
    ):
        # To support the organism kwarg being passed in getattr access in other parts of the code
        # https://github.com/laminlabs/bionty/issues/163
        if "organism" in kwargs and taxa is None:
            taxa = kwargs.pop("organism")
        super().__init__(organism=taxa, source=source, version=version, **kwargs)

    def _load_df(self) -> pd.DataFrame:
        if self.source == "ensembl":
            if not self._local_parquet_path.exists():
                # try to download from s3
                s3_bionty_assets(
                    filename=self._parquet_filename,
                    assets_base_url="s3://bionty-assets",
                    localpath=self._local_parquet_path,
                )

            # try to download from original url
            if not self._local_parquet_path.exists():
                self._url_download(self._url, self._local_ontology_path)  # type:ignore
                df = pd.read_csv(
                    self._local_ontology_path,
                    sep="\t",
                    index_col=False,  # type:ignore
                )
                df.rename(
                    columns={
                        "#name": "name",
                        "species": "scientific_name",
                        "taxonomy_id": "ontology_id",
                    },
                    inplace=True,
                )
                df["name"] = df["name"].str.lower()
                df["ontology_id"] = "NCBITaxon:" + df["ontology_id"].astype(str)
                df["scientific_name"] = df["scientific_name"].apply(
                    lambda x: " ".join(
                        [x.split("_")[0].capitalize()] + x.split("_")[1:]
                    )
                )
                df.to_parquet(self._local_parquet_path)
                return df
            else:
                df = pd.read_parquet(self._local_parquet_path)
                return _standardize_scientific_name(df)
        else:
            return super()._load_df()

    def df(self) -> pd.DataFrame:
        """Pandas DataFrame of the ontology.

        Returns:
            A Pandas DataFrame of the ontology.

        Example::

            import bionty.base as bionty_base

            bt.Organism().df()
        """
        return self._df.set_index("name")


def _standardize_scientific_name(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize scientific name following NCBITaxon convention.

    homo_sapiens -> Homo sapiens
    """
    df["scientific_name"] = df["scientific_name"].apply(
        lambda x: " ".join([x.split("_")[0].capitalize()] + x.split("_")[1:])
    )
    return df

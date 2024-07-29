import json
from pathlib import Path
from typing import Literal, Optional

import pandas as pd

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._io import s3_bionty_assets

from ._shared_docstrings import _doc_params, doc_entites


@_doc_params(doc_entities=doc_entites)
class BFXPipeline(PublicOntology):
    """Bioinformatics pipelines.

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Optional[Literal["all"]] = None,
        source: Optional[Literal["lamin"]] = None,
        version: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(source=source, version=version, organism=organism, **kwargs)

    def _load_df(self) -> pd.DataFrame:
        localpath = self._local_parquet_path.as_posix().replace(  # type:ignore
            ".parquet", ".json"
        )
        s3_bionty_assets("bfxpipelines.json", Path(localpath))
        with open(localpath) as f:
            data = json.load(f)

        df = pd.DataFrame(data).transpose()
        df.drop("versions", inplace=True, axis=1)
        df.rename(columns={"id": "ontology_id"}, inplace=True)
        df.set_index("ontology_id", inplace=True, drop=True)

        return df

    def df(self) -> pd.DataFrame:
        """Pandas DataFrame of the ontology.

        Returns:
            A Pandas DataFrame of the ontology.

        Examples:
            >>> import bionty.base as bionty_base
            >>> bt.BFXPipeline().df()
        """
        return self._df.set_index("ontology_id")

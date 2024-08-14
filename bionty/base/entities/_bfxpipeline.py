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

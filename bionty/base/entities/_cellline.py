from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


@_doc_params(doc_entities=doc_entites)
class CellLine(PublicOntology):
    """Cell line.

    1. Cell Line Ontology
    https://github.com/CLO-ontology/CLO

    2. DepMap
    https://depmap.org

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["clo", "depmap"] | None = None,
        version: Literal["2022-03-21", "2024-Q2"] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"clo": ["CLO"]},
            **kwargs,
        )

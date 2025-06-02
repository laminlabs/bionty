from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


@_doc_params(doc_entities=doc_entites)
class CellMarker(PublicOntology):
    """Cell markers.

    1. Cell Marker Ontology
    http://bio-bigdata.hrbmu.edu.cn/CellMarker/

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["human", "mouse"] | None = None,
        source: Literal["cellmarker"] | None = None,
        version: Literal["2.0"] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            ols_supported=False,
            **kwargs,
        )

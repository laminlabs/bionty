from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


@_doc_params(doc_entities=doc_entites)
class Ethnicity(PublicOntology):
    """Ethnicity.

    1. Human Ancestry Ontology
    https://github.com/EBISPOT/hancestro

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["human"] | None = None,
        source: Literal["hancestro"] | None = None,
        version: Literal["3.0"] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"hancestro": ["HANCESTRO"]},
            **kwargs,
        )

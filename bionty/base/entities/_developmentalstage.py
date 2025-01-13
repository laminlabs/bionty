from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


@_doc_params(doc_entities=doc_entites)
class DevelopmentalStage(PublicOntology):
    """Developmental Stage.

    1. Developmental Stage Ontology
    https://github.com/obophenotype/developmental-stage-ontologies

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["human", "mouse"] | None = None,
        source: Literal["hsapdv", "mmusdv"] | None = None,
        version: Literal["2020-03-10", "2024-05-28"] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"hsapdv": ["HsapDv"], "mmusdv": ["MmusDv"]},
            include_rel="part_of",
            **kwargs,
        )

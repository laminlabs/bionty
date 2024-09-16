from typing import Literal, Optional

from bionty.base._public_ontology import PublicOntology

from ._shared_docstrings import _doc_params, doc_entites


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
        organism: Optional[Literal["human", "mouse"]] = None,
        source: Optional[Literal["hsapdv", "mmusdv"]] = None,
        version: Optional[Literal["2020-03-10", "2024-05-28"]] = None,
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

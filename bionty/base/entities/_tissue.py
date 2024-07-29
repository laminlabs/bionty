from typing import Literal, Optional

from bionty.base._public_ontology import PublicOntology

from ._shared_docstrings import _doc_params, doc_entites


@_doc_params(doc_entities=doc_entites)
class Tissue(PublicOntology):
    """Tissue.

    1. Uberon
    Edits of terms are coordinated and reviewed on:
    https://github.com/obophenotype/uberon

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Optional[Literal["all"]] = None,
        source: Optional[Literal["uberon"]] = None,
        version: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"uberon": ["UBERON"]},
            **kwargs,
        )

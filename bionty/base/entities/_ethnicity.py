from typing import Literal, Optional

from bionty.base._public_ontology import PublicOntology

from ._shared_docstrings import _doc_params, doc_entites


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
        organism: Optional[Literal["human"]] = None,
        source: Optional[Literal["hancestro"]] = None,
        version: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"hancestro": ["HANCESTRO"]},
            **kwargs,
        )

from typing import Literal, Optional

from bionty.base._public_ontology import PublicOntology

from ._shared_docstrings import _doc_params, doc_entites


@_doc_params(doc_entities=doc_entites)
class Pathway(PublicOntology):
    """Pathway.

    1. Gene Ontology
    https://bioportal.bioontology.org/ontologies/GO/?p=summary

    2. Pathway Ontology
    https://bioportal.bioontology.org/ontologies/PW/?p=summary

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Optional[Literal["all"]] = None,
        source: Optional[Literal["go", "pw"]] = None,
        version: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(source=source, version=version, organism=organism, **kwargs)

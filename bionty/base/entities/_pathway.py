from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


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
        organism: Literal["all"] | None = None,
        source: Literal["go", "pw"] | None = None,
        version: Literal["2023-05-10", "2024-06-17"] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(source=source, version=version, organism=organism, **kwargs)

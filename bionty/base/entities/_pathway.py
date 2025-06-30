from __future__ import annotations

from typing import Literal, overload

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites

GOVersions = Literal[
    "2024-11-03",
    "2024-06-17",
    "2023-05-10",
]

PWVersions = Literal["7.84"]


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

    @overload
    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["go"] = None,
        version: GOVersions | None = None,
        **kwargs,
    ) -> None: ...

    @overload
    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["pw"] = None,
        version: PWVersions | None = None,
        **kwargs,
    ) -> None: ...

    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["go", "pw"] | None = None,
        version: GOVersions | PWVersions | None = None,
        **kwargs,
    ) -> None:
        super().__init__(source=source, version=version, organism=organism, **kwargs)

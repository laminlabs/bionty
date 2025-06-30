from __future__ import annotations

from typing import Literal, overload

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites

DRONVersions = Literal[
    "2025-04-18",
    "2024-08-05",
    "2023-03-10",
]

CHEBIVersions = Literal[
    "2024-07-27",
    "2024-03-02",
]


@_doc_params(doc_entities=doc_entites)
class Drug(PublicOntology):
    """Drug ontologies.

    1. DRON
    Edits of terms are coordinated and reviewed on:
    https://bioportal.bioontology.org/ontologies/DRON/

    2. CHEBI
    https://www.ebi.ac.uk/chebi/

    Args:
        {doc_entities}
    """

    @overload
    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["dron"] = None,
        version: DRONVersions | None = None,
        **kwargs,
    ) -> None: ...

    @overload
    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["chebi"] = None,
        version: CHEBIVersions | None = None,
        **kwargs,
    ) -> None: ...

    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["dron", "chebi"] | None = None,
        version: DRONVersions | CHEBIVersions | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"dron:": ["DRON"]},
            **kwargs,
        )

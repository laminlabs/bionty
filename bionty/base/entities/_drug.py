from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


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

    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["dron", "chebi"] | None = None,
        version: Literal["2024-07-27", "2023-03-10", "2024-03-02", "2024-08-05"]
        | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"dron": ["DRON"]},
            **kwargs,
        )

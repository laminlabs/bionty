from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


@_doc_params(doc_entities=doc_entites)
class Protein(PublicOntology):
    """Protein.

    1. Uniprot
    https://www.uniprot.org/

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["human", "mouse", "mouse-ear cress", "bovine", "dog", "chinese hamster", "e. coli", "long-tailed macaque", "saccharomyces cerevisiae s288c", "pig"] | None = None,
        source: Literal["uniprot"] | None = None,
        version: Literal["2026-01", "2024-03", "2023-03", "2023-02", "2025-04-10"] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            ols_supported=False,
            **kwargs,
        )

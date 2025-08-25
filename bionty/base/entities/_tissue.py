from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


@_doc_params(doc_entities=doc_entites)
class Tissue(PublicOntology):
    """Tissue.

    1. Uberon
    https://github.com/obophenotype/uberon

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["uberon"] | None = None,
        version: Literal[
            "2025-05-28",
            "2024-08-07",
            "2024-05-13",
            "2024-03-22",
            "2024-02-20",
            "2024-01-18",
            "2023-09-05",
            "2023-04-19",
            "2023-02-14",
            "2022-08-19",
        ]
        | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"uberon": ["UBERON:"]},
            include_rel="part_of",
            **kwargs,
        )

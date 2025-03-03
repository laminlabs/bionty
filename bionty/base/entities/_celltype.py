from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


@_doc_params(doc_entities=doc_entites)
class CellType(PublicOntology):
    """Cell type ontologies.

    1. Cell ontology
    https://github.com/obophenotype/cell-ontology

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["cl"] | None = None,
        version: Literal[
            "2022-08-16",
            "2023-02-15",
            "2023-04-20",
            "2023-08-24",
            "2024-01-04",
            "2024-02-13",
            "2024-04-05",
            "2024-05-15",
            "2024-08-16",
        ]
        | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"cl": ["CL"]},
            **kwargs,
        )

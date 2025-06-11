from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


@_doc_params(doc_entities=doc_entites)
class Phenotype(PublicOntology):
    """Phenotype.

    1. Human Phenotype Ontology
    https://hpo.jax.org/app/

    4.Phecodes ICD10 map
    https://phewascatalog.org/phecodes_icd10

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["human", "all"] | None = None,
        source: Literal["hp", "phe", "pato"] | None = None,
        version: Literal[
            "1.2",
            "2023-05-18",
            "2024-03-28",
            "2022-12-17",
            "2024-01-22",
            "2024-04-18",
            "2023-05-31",
            "2024-02-07",
            "2024-06-18",
            "2023-01-27",
            "2023-04-05",
            "2023-06-17",
            "2024-03-06",
            "2024-04-26",
            "2025-05-14",
            "2025-05-06",
        ]
        | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={
                "hp": ["HP"],
                "mp": ["MP"],  # mp might require an exclusion prefix for mpath
                "zp": ["ZP"],
                "pato": ["PATO"],
            },
            **kwargs,
        )

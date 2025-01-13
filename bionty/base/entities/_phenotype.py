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

    2. Mammalian Phenotype Ontology
    https://github.com/mgijax/mammalian-phenotype-ontology

    3. Zebrafish Phenotype Ontology
    https://github.com/obophenotype/zebrafish-phenotype-ontology

    4.Phecodes ICD10 map
    https://phewascatalog.org/phecodes_icd10

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["human", "mammalian", "zebrafish", "all"] | None = None,
        source: Literal["hp", "phe", "mp", "zp", "pato"] | None = None,
        version: Literal[
            "2023-05-18",
            "2024-03-28",
            "1.2",
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

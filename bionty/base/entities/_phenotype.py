from __future__ import annotations

from typing import Literal, overload

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites

HPVersions = Literal[
    "2025-05-06",
    "2024-04-26",
    "2024-03-06",
    "2023-06-17",
    "2023-04-05",
    "2023-01-27",
]

PHEVersions = Literal["1.2"]

PATOVersions = Literal[
    "2025-05-14",
    "2024-03-28",
    "2023-05-18",
]


@_doc_params(doc_entities=doc_entites)
class Phenotype(PublicOntology):
    """Phenotype.

    1. Human Phenotype Ontology
    https://hpo.jax.org/app/

    2. Phecodes ICD10 map
    https://phewascatalog.org/phecodes_icd10

    3. PATO - Phenotype And Trait Ontology
    https://obofoundry.org/ontology/pato.html

    Args:
        {doc_entities}
    """

    @overload
    def __init__(
        self,
        organism: Literal["human"] | None = None,
        source: Literal["hp"] = None,
        version: HPVersions | None = None,
        **kwargs,
    ) -> None: ...

    @overload
    def __init__(
        self,
        organism: Literal["human"] | None = None,
        source: Literal["phe"] = None,
        version: PHEVersions | None = None,
        **kwargs,
    ) -> None: ...

    @overload
    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["pato"] = None,
        version: PATOVersions | None = None,
        **kwargs,
    ) -> None: ...

    def __init__(
        self,
        organism: Literal["human", "all"] | None = None,
        source: Literal["hp", "phe", "pato"] | None = None,
        version: HPVersions | PHEVersions | PATOVersions | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={
                "hp:": ["HP"],
                "mp:": ["MP"],  # mp might require an exclusion prefix for mpath
                "zp:": ["ZP"],
                "pato:": ["PATO"],
            },
            **kwargs,
        )

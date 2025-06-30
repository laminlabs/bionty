from __future__ import annotations

from typing import Literal, overload

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites

ICDVersions = Literal["icd-9-2011", "icd-10-2020", "icd-10-2024", "icd-11-2023"]

MondoVersions = Literal[
    "2025-06-03",
    "2024-08-06",
    "2024-06-04",
    "2024-05-08",
    "2024-02-06",
    "2024-01-03",
    "2023-08-02",
    "2023-04-04",
    "2023-02-06",
    "2022-10-11",
    "2023-04-04",
]

DOIDVersions = Literal[
    "2025-05-30", "2024-05-29", "2024-01-31", "2023-03-31", "2023-01-30"
]


@_doc_params(doc_entities=doc_entites)
class Disease(PublicOntology):
    """Disease ontologies.

    1. Mondo
    Edits of terms are coordinated and reviewed on:
    https://github.com/monarch-initiative/mondo

    2. Human Disease Ontology
    Edits of terms are coordinated and reviewed on:
    https://github.com/DiseaseOntology/HumanDiseaseOntology

    3. International Classification of Diseases (ICD)
    Edits of terms are coordinated and reviewed on:
    https://www.who.int/standards/classifications/classification-of-diseases

    Args:
        {doc_entities}
    """

    @overload
    def __init__(
        self,
        organism: Literal["all", "human"] | None = None,
        source: Literal["icd"] = None,
        version: ICDVersions | None = None,
        **kwargs,
    ) -> None: ...

    @overload
    def __init__(
        self,
        organism: Literal["all", "human"] | None = None,
        source: Literal["mondo"] = None,
        version: MondoVersions | None = None,
        **kwargs,
    ) -> None: ...

    @overload
    def __init__(
        self,
        organism: Literal["all", "human"] | None = None,
        source: Literal["doid"] = None,
        version: DOIDVersions | None = None,
        **kwargs,
    ) -> None: ...

    def __init__(
        self,
        organism: Literal["all", "human"] | None = None,
        source: Literal["mondo", "doid", "icd"] | None = None,
        version: MondoVersions | DOIDVersions | ICDVersions | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"mondo:": ["MONDO"]},
            **kwargs,
        )

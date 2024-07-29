from typing import Literal, Optional

from bionty.base._public_ontology import PublicOntology

from ._shared_docstrings import _doc_params, doc_entites


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

    def __init__(
        self,
        organism: Optional[Literal["all", "human"]] = None,
        source: Optional[Literal["mondo", "doid", "icd"]] = None,
        version: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"mondo": ["MONDO"]},
            **kwargs,
        )

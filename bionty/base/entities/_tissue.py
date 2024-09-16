from typing import Literal, Optional

from bionty.base._public_ontology import PublicOntology

from ._shared_docstrings import _doc_params, doc_entites


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
        organism: Optional[Literal["all"]] = None,
        source: Optional[Literal["uberon"]] = None,
        version: Optional[
            Literal[
                "2022-08-19",
                "2023-02-14",
                "2023-04-19",
                "2023-09-05",
                "2024-01-18",
                "2024-02-20",
                "2024-05-13",
                "2024-08-07",
            ]
        ] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"uberon": ["UBERON"]},
            include_rel="part_of",
            **kwargs,
        )

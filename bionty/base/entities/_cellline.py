from typing import Literal, Optional

from bionty.base._public_ontology import PublicOntology

from ._shared_docstrings import _doc_params, doc_entites


@_doc_params(doc_entities=doc_entites)
class CellLine(PublicOntology):
    """Cell line.

    1. Cell Line Ontology
    https://github.com/CLO-ontology/CLO

    2. DepMap
    https://depmap.org

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Optional[Literal["all"]] = None,
        source: Optional[Literal["clo", "depmap"]] = None,
        version: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            include_id_prefixes={"clo": ["CLO"]},
            **kwargs,
        )

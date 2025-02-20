from __future__ import annotations

from typing import Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params

from ._shared_docstrings import doc_entites


@_doc_params(doc_entities=doc_entites)
class BioSample(PublicOntology):
    """BioSample attributes.

    1. NCBI BioSample Attributes
    https://www.ncbi.nlm.nih.gov/biosample/docs/attributes

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["ncbi"] | None = None,
        version: Literal["2023-09"] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(source=source, version=version, organism=organism, **kwargs)

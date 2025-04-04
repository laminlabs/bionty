from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from bionty.base._public_ontology import PublicOntology
from bionty.base.dev._doc_util import _doc_params
from bionty.base.entities._shared_docstrings import organism_removed

if TYPE_CHECKING:
    from bionty.base._ontology import Ontology


@_doc_params(doc_entities=organism_removed)
class ExperimentalFactor(PublicOntology):
    """Experimental Factor.

    1. Experimental Factor Ontology
    https://www.ebi.ac.uk/ols/ontologies/efo

    Args:
        {doc_entities}
    """

    def __init__(
        self,
        organism: Literal["all"] | None = None,
        source: Literal["efo"] | None = None,
        version: Literal[
            "3.48.0",
            "3.57.0",
            "3.62.0",
            "3.63.0",
            "3.65.0",
            "3.66.0",
            "3.69.0",
            "3.70.0",
        ]
        | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            organism=organism,
            source=source,
            version=version,
            include_id_prefixes={"efo": ["EFO", "http://www.ebi.ac.uk/efo/"]},
            **kwargs,
        )

    def to_pronto(self, mute: bool = False) -> Ontology:
        """The Pronto Ontology object.

        See: https://pronto.readthedocs.io/en/stable/api/pronto.Ontology.html
        """
        from bionty.base._ontology import Ontology

        self._download_ontology_file(
            localpath=self._local_ontology_path,
            url=self._url,
        )
        return Ontology(
            handle=self._local_ontology_path,
            prefix="http://www.ebi.ac.uk/efo/",
        )

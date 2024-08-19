from typing import Literal, Optional

from bionty.base._public_ontology import PublicOntology

from ._shared_docstrings import _doc_params, doc_entites


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
        organism: Optional[Literal["human", "mammalian", "zebrafish", "all"]] = None,
        source: Optional[Literal["hp", "phe", "mp", "zp", "pato"]] = None,
        version: Optional[str] = None,
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

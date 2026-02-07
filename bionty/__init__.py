"""Basic biological entities, coupled to public ontologies [`source <https://github.com/laminlabs/bionty/blob/main/bionty/models.py>`__].

- Create records from public ontologies using `.from_source()`.
- Access public ontologies via `.public()` to search & bulk-create records.
- Use hierarchical relationships among records (`.parents`).
- Use `.synonyms` and `.abbr` to manage synonyms.
- Manage ontology versions.

Mount `bionty` in a new instance::

   lamin init --storage <path_to_storage_location> --modules bionty

Import the package::

    import bionty as bt

Access public ontologies::

    genes = bt.Gene.public()
    genes.validate(["BRCA1", "TCF7"], field="symbol")

Create records from public ontologies::

   cell_type = bt.CellType.from_source(ontology_id="CL:0000037")
   cell_type.save()

View ontological hierarchy::

   cell_type.view_parents()

Create your own records::

   cell_type_new = bt.CellType(name="my new cell type")
   cell_type_new.save()
   cell_type_new.parents.add(cell_type)
   cell_type_new.view_parents()

Manage synonyms::

   cell_type_new.add_synonyms(["my cell type", "my cell"])
   cell_type_new.set_abbr("MCT")

Detailed guides:

- :doc:`docs:public-ontologies`
- :doc:`docs:manage-ontologies`

Registries:

.. autosummary::
   :toctree: .

   Organism
   Gene
   Protein
   CellMarker
   CellType
   CellLine
   Tissue
   Disease
   Pathway
   Phenotype
   ExperimentalFactor
   DevelopmentalStage
   Ethnicity

Settings:

.. autosummary::
   :toctree: .

   settings

Ontology versions:

.. autosummary::
   :toctree: .

   Source

Submodules:

.. autosummary::
   :toctree: .

   core
   base
   models
   uids

"""

import importlib

__version__ = "2.1.0"

from lamindb_setup._check_setup import _check_instance_setup

from . import _biorecord, uids

_check_instance_setup(from_module="bionty")

__all__ = [
    "CellLine",
    "CellMarker",
    "CellType",
    "DevelopmentalStage",
    "Disease",
    "Ethnicity",
    "ExperimentalFactor",
    "Gene",
    "Organism",
    "Pathway",
    "Phenotype",
    "Protein",
    "Source",
    "Tissue",
    # modules
    "settings",
    "base",
    "core",
    "uids",
]

ids = uids  # backward compat

_MODEL_NAMES = (
    "CellLine",
    "CellMarker",
    "CellType",
    "DevelopmentalStage",
    "Disease",
    "Ethnicity",
    "ExperimentalFactor",
    "Gene",
    "Organism",
    "Pathway",
    "Phenotype",
    "Protein",
    "Source",
    "Tissue",
)


def __getattr__(name: str):
    """Lazy-import to avoid loading pandas/pyarrow at package import."""
    if name == "base":
        return importlib.import_module(".base", "bionty")
    if name == "settings":
        from .core._settings import settings

        return settings
    if name in _MODEL_NAMES:
        from . import models

        return getattr(models, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

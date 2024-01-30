"""Registries for basic biological entities, coupled to public ontologies.

Features
========

- Create records from entries in public ontologies using `.from_public()`.
- Access full underlying public ontologies via `.public()` to search & bulk-create records.
- Create in-house ontologies by using hierarchical relationships among records (`.parents`).
- Use `.synonyms` and `.abbr` to manage synonyms.

All registries inherit from :class:`~lamindb.dev.CanValidate` &
:class:`~lamindb.dev.HasParents` to curate, validate & annotate data, and from
:class:`~lamindb.dev.Registry` for query & search.

.. dropdown:: How to ensure reproducibility across different versions of public ontologies?

   It's important to track versions of external data dependencies.

   `bionty` manages it under the hood:

   - Versions of public databases are auto-tracked in :class:`PublicSource`.
   - Records are indexed by universal ids, created by hashing `name` & `ontology_id` for portability across databases.

.. note::

   Read the guides:

   - :doc:`/bio-registries`
   - :doc:`/validate`

   For more background on how public ontologies are accessed, see the utility
   library `Bionty-base <https://lamin.ai/docs/bionty-base>`__.

API
===

Import the package::

   import bionty as bt

Basic biological registries:

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

Public ontology versions:

.. autosummary::
   :toctree: .

   PublicSource

Developer API:

.. autosummary::
   :toctree: .

   dev
   ids
"""

__version__ = "0.40.0"

from lamindb_setup import _check_instance_setup
from lamindb_setup._check_instance_setup import _INSTANCE_NOT_SETUP_WARNING
from lnschema_bionty import ids

_INSTANCE_SETUP = _check_instance_setup(from_lamindb=True)


class InstanceNotSetupError(Exception):
    pass


def __getattr__(name):
    raise InstanceNotSetupError(
        f"{_INSTANCE_NOT_SETUP_WARNING}If you used the CLI to init or load an instance,"
        " please RESTART the python session (in a notebook, restart kernel)"
    )


# only import all other functionality if setup was successful
if _INSTANCE_SETUP:
    del InstanceNotSetupError
    del __getattr__  # delete so that imports work out
    from lnschema_bionty import (
        CellLine,
        CellMarker,
        CellType,
        DevelopmentalStage,
        Disease,
        Ethnicity,
        ExperimentalFactor,
        Gene,
        Organism,
        Pathway,
        Phenotype,
        Protein,
        PublicSource,
        Tissue,
        dev,
    )
    from lnschema_bionty.dev._settings import settings

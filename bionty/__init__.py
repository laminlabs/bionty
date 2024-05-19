"""Registries for basic biological entities, coupled to public ontologies.

Overview
========

- Create records from entries in public ontologies using `.from_public()`.
- Access full underlying public ontologies via `.public()` to search & bulk-create records.
- Create in-house ontologies by using hierarchical relationships among records (`.parents`).
- Use `.synonyms` and `.abbr` to manage synonyms.

All registries inherit from :class:`~lamindb.core.CanValidate` &
:class:`~lamindb.core.HasParents` to standardize, validate & annotate data, and from
:class:`~lamindb.core.Registry` for query & search.

.. dropdown:: How to ensure reproducibility across different versions of public ontologies?

   It's important to track versions of external data dependencies.

   `bionty` manages it under the hood:

   - Versions of public databases are auto-tracked in :class:`PublicSource`.
   - Records are indexed by universal ids, created by hashing `name` & `ontology_id` for portability across databases.

Installation
============

>>> pip install 'lamindb[bionty]'

Setup
=====

>>> lamin init --storage <storage_name> --schema bionty

Quickstart
==========

Import bionty:

>>> import bionty as bt

Access public ontologies:

>>> genes = bt.Gene.public()
>>> genes.validate(["BRCA1", "TCF7"], field="symbol")

Create records from public ontologies:

>>> cell_type = bt.CellType.from_public(ontology_id="CL:0000037")
>>> cell_type.save()

View ontological hierarchy:

>>> cell_type.view_parents()

Create in-house ontologies:

>>> cell_type_new = bt.CellType(name="my new cell type")
>>> cell_type_new.save()
>>> cell_type_new.parents.add(cell_type)
>>> cell_type_new.view_parents()

Manage synonyms:

>>> cell_type_new.add_synonyms(["my cell type", "my cell"])
>>> cell_type_new.set_abbr("MCT")

.. note::

   Read the guides:

   - `Access public ontologies <https://lamin.ai/docs/public-ontologies>`__
   - :doc:`/bio-registries`

   For more background on how public ontologies are accessed, see the utility
   library `bionty-base <https://lamin.ai/docs/bionty-base>`__.

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

   core
"""

__version__ = "0.43.0"

from lamindb_setup._check_setup import InstanceNotSetupError, _check_instance_setup
from lnschema_bionty import ids


def __getattr__(name):
    raise InstanceNotSetupError()


if _check_instance_setup(from_lamindb=True):
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
        settings,
    )

    from . import core

"""Registries for basic biological entities, coupled to public ontologies.

Overview
========

- Create records from entries in public ontologies using `.from_source()`.
- Access full underlying public ontologies via `.public()` to search & bulk-create records.
- Create in-house ontologies by using hierarchical relationships among records (`.parents`).
- Use `.synonyms` and `.abbr` to manage synonyms.

All registries inherit from :class:`~lamindb.core.CanValidate` &
:class:`~lamindb.core.HasParents` to standardize, validate & annotate data, and from
:class:`~lamindb.core.Record` for query & search.

.. dropdown:: How to ensure reproducibility across different versions of public ontologies?

   It's important to track versions of external data dependencies.

   `bionty` manages it under the hood:

   - Versions of ontology sources are auto-tracked in :class:`Source`.
   - Records are indexed by universal ids, created by hashing `ontology_id` for portability across databases.

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

>>> cell_type = bt.CellType.from_source(ontology_id="CL:0000037")
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
   - :doc:`docs:bio-registries`

   For more background on how public ontologies are accessed, see `bionty.base`.

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

Ontology versions:

.. autosummary::
   :toctree: .

   Source

Developer API:

.. autosummary::
   :toctree: .

   core

Bionty base:

.. autosummary::
   :toctree: .

   base
"""

__version__ = "0.47.1"

from . import base, ids

base.sync_sources()

# from lamindb_setup._check_setup import InstanceNotSetupError as _InstanceNotSetupError
from lamindb_setup._check_setup import _check_instance_setup

# def __getattr__(name):
#     raise _InstanceNotSetupError()


# trigger instance loading if users
# want to access attributes
def __getattr__(name):
    if name not in {"models"}:
        _check_instance_setup(from_lamindb=True)
    return globals()[name]


if _check_instance_setup():
    import lamindb  # this is needed as even the Record base class is defined in lamindb

    del __getattr__  # delete so that imports work out
    from .core._settings import settings
    from .models import (
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
        Source,
        Tissue,
    )

    # backward compat
    PublicSource = Source

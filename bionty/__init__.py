"""Basic biological entities, coupled to public ontologies [`source <https://github.com/laminlabs/bionty/blob/main/bionty/models.py>`__].

- Create records from public ontologies using `.from_source()`.
- Access public ontologies via `.public()` to search & bulk-create records.
- Use hierarchical relationships among records (`.parents`).
- Use `.synonyms` and `.abbr` to manage synonyms.
- Manage ontology versions.

Install and mount `bionty` in a new instance:

>>> pip install 'bionty'
>>> lamin init --storage <storage_name> --schema bionty

Import the package:

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

Detailed guides:

- :doc:`docs:public-ontologies`
- :doc:`docs:bio-registries`

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

"""

__version__ = "0.52.1"

from lamindb_setup.core._setup_bionty_sources import (
    load_bionty_sources as _load_bionty_sources,
)

from . import base, ids

base.sync_sources()

from lamindb_setup._check_setup import _check_instance_setup


def __getattr__(name):
    if name != "models":
        _check_instance_setup(from_module="bionty")
    return globals()[name]


if _check_instance_setup():
    import lamindb as _lamindb  # this is needed as even the Record base class is defined in lamindb
    from lamindb_setup import settings as _setup_settings

    _load_bionty_sources(_setup_settings.instance)

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

"""Access to public ontologies.

`bionty.base` is the read-only interface for public ontology that underlies bionty and doesn't require a lamindb instance.

Import the package::

   import bionty.base as bt_base

Access public ontologies::

   genes = bt_base.Gene()

Get a DataFrame of all available values::

   genes.to_dataframe()

Sources & settings
------------------

.. autofunction:: display_sources
.. autofunction:: display_currently_used_sources
.. autodata:: settings

Base class
----------

`Pronto Ontology objects <https://pronto.readthedocs.io/en/stable/api/pronto.Ontology.html>`__ can be accessed via `{entity}.to_pronto()`.

.. autoclass:: PublicOntology
.. autoclass:: PublicOntologyField

Entities
--------

.. autoclass:: Organism
.. autoclass:: Gene
.. autoclass:: Protein
.. autoclass:: CellMarker
.. autoclass:: CellType
.. autoclass:: CellLine
.. autoclass:: Tissue
.. autoclass:: Disease
.. autoclass:: Phenotype
.. autoclass:: Pathway
.. autoclass:: ExperimentalFactor
.. autoclass:: DevelopmentalStage
.. autoclass:: Drug
.. autoclass:: Ethnicity
.. autoclass:: BFXPipeline
.. autoclass:: BioSample

"""

# dynamic classes
from . import dev
from ._display_sources import display_currently_used_sources, display_sources

# tools
from ._public_ontology import PublicOntology, PublicOntologyField
from ._settings import settings

# sources
# from .dev._handle_sources import reset_sources
from .entities._bfxpipeline import BFXPipeline
from .entities._biosample import BioSample
from .entities._cellline import CellLine
from .entities._cellmarker import CellMarker
from .entities._celltype import CellType
from .entities._developmentalstage import DevelopmentalStage
from .entities._disease import Disease
from .entities._drug import Drug
from .entities._ethnicity import Ethnicity
from .entities._experimentalfactor import ExperimentalFactor
from .entities._gene import Gene
from .entities._organism import Organism
from .entities._pathway import Pathway
from .entities._phenotype import Phenotype
from .entities._protein import Protein
from .entities._tissue import Tissue

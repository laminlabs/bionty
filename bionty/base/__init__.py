"""Access to public ontologies.

`bionty.base` is the read-only interface for public ontology that underlies bionty and doesn't require a lamindb instance.

Import the package:

>>> import bionty.base as bt_base

Access public ontologies:

>>> genes = bt_base.Gene()

Get a DataFrame of all available values:

>>> genes.df()

Entities
========

Bionty base provides access to several entities, most of which are also supported by Bionty.

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
   Phenotype
   Pathway
   ExperimentalFactor
   DevelopmentalStage
   Drug
   Ethnicity
   BFXPipeline
   BioSample

Base class
----------

`Pronto Ontology objects <https://pronto.readthedocs.io/en/stable/api/pronto.Ontology.html>`__ can be accessed via `{entity}.to_pronto()`.

.. autosummary::
   :toctree: .

   PublicOntology
   PublicOntologyField

Ontology sources
----------------

.. autosummary::
   :toctree: .

   display_available_sources
   display_currently_used_sources
   settings

"""

# dynamic classes
from . import dev
from ._display_sources import display_available_sources, display_currently_used_sources

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

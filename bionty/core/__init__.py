"""Developer API.

.. autosummary::
   :toctree: .

   BioRecord
   StaticReference
   Settings
   sync_public_sources
"""

from lamindb_setup._check_setup import _check_instance_setup

_check_instance_setup(from_module="bionty")

from bionty.models import BioRecord, StaticReference

from ._add_ontology import add_ontology
from ._settings import Settings
from ._source import sync_public_sources

# backward-compat
sync_all_sources_to_latest = sync_public_sources

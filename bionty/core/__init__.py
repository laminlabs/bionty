"""Developer API.

.. autosummary::
   :toctree: .

   BioRecord
   StaticReference
   Settings
   sync_all_sources_to_latest
   set_latest_sources_as_currently_used
"""

from lamindb_setup._check_setup import _check_instance_setup

_check_instance_setup(from_module="bionty")

from bionty.models import BioRecord, StaticReference

from ._add_ontology import add_ontology
from ._bionty import (
    set_latest_sources_as_currently_used,
    sync_all_sources_to_latest,
)
from ._settings import Settings

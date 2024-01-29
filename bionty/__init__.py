"""Basic biological entities.

Import the package::

   import bionty

This is the complete API reference:

.. autosummary::
   :toctree: .

   example_function
   ExampleClass
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
    )
    from lnschema_bionty.dev._settings import settings

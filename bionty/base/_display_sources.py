import pandas as pd
from lamin_utils import logger

from bionty.base.dev._handle_sources import LAMINDB_INSTANCE_LOADED

from ._settings import settings
from .dev._handle_sources import parse_currently_used_sources


def display_available_sources() -> pd.DataFrame:
    """Displays all available sources.

    Example::

        import bionty.base as bt_base

        bt.display_available_sources()
    """
    from .dev._handle_sources import parse_sources_yaml

    return parse_sources_yaml(settings.public_sources).set_index("entity")  # type: ignore


# This function naming is consistent with the `currently_used` field in Source SQL table
# Do not rename!
def display_currently_used_sources(mute: bool = False) -> pd.DataFrame:
    """Displays all currently used sources.

    Active version is unique for entity + organism.

    Example::

        import bionty.base as bt_base

        bt.display_currently_used_sources()
    """
    if LAMINDB_INSTANCE_LOADED():
        if not mute:
            logger.error(
                "You have a LaminDB instance loaded, please run the following to check default sources:\n"
                "    → bt.Source.filter(currently_used=True).df()"
            )

    versions = parse_currently_used_sources(settings.public_sources)

    df_rows = []
    for bionty_class, bionty_class_data in versions.items():
        for organism, organism_data in bionty_class_data.items():
            for source, version in organism_data.items():
                df_rows.append(
                    {
                        "entity": bionty_class,
                        "organism": organism,
                        "name": source,
                        "version": version,
                    }
                )

    return pd.DataFrame(df_rows).set_index("entity")

import pandas as pd

from bionty.base.dev._handle_sources import LAMINDB_INSTANCE_LOADED
from bionty.base.dev._io import load_yaml

from ._settings import settings


def display_available_sources() -> pd.DataFrame:
    """Displays all available sources.

    Examples:
        >>> import bionty.base as bionty_base
        >>> bt.display_available_sources()
    """
    from .dev._handle_sources import parse_sources_yaml

    return parse_sources_yaml(settings.local_sources).set_index("entity")  # type: ignore


# This function naming is consistent with the `currently_used` field in Source SQL table
# Do not rename!
def display_currently_used_sources() -> pd.DataFrame:
    """Displays all currently used sources.

    Active version is unique for entity + organism.

    Examples:
        >>> import bionty.base as bionty_base
        >>> bt.display_currently_used_sources()
    """
    VERSIONS_FILE_PATH = (
        settings.lamindb_sources
        if LAMINDB_INSTANCE_LOADED()
        else settings.current_sources
    )

    versions = load_yaml(VERSIONS_FILE_PATH.resolve())

    df_rows = []
    for bionty_class, bionty_class_data in versions.items():
        for organism, organism_data in bionty_class_data.items():
            for source, version in organism_data.items():
                df_rows.append(
                    {
                        "entity": bionty_class,
                        "organism": organism,
                        "source": source,
                        "version": version,
                    }
                )

    return pd.DataFrame(df_rows).set_index("entity")

from filelock import FileLock  # type: ignore

from ._settings import settings
from .dev._handle_sources import (
    create_currently_used_sources_yaml,
    create_or_update_sources_local_yaml,
)


def sync_sources():
    # Make this code safe when running bionty from multiple processes
    with FileLock(settings.versionsdir / "bionty_base.lock"):
        create_or_update_sources_local_yaml(overwrite=False)
        # always generate a new CURRENT_SOURCES file
        create_currently_used_sources_yaml(overwrite=True)

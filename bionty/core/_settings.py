from __future__ import annotations

from lamin_utils import logger

from bionty.models import Organism


class Settings:
    """Settings.

    Directly use `.settings` rather than instantiating this class yourself.
    """

    def __init__(self):
        self._organism = None

    @property
    def organism(self) -> Organism | None:
        """Default organism argument (default `None`).

        Default record to use when `organism` argument is required in `lamindb` functionality.

        Only takes effect if explicitly set!

        Examples:
            >>> bionty.settings.organism = "mouse"
            ✅ set organism: Organism(id=vado, name=mouse, taxon_id=10090, scientific_name=mus_musculus, updated_at=2023-07-21 11:37:08, source_id=CXWj, created_by_id=DzTjkKse) # noqa
        """
        return self._organism

    @organism.setter
    def organism(self, name: str | Organism):
        if isinstance(name, Organism):
            self._organism = name
        else:
            import lamindb as ln

            # do not show the validated message for organism
            verbosity = ln.settings.verbosity
            ln.settings.verbosity = 1
            organism = Organism.from_source(name=name)
            ln.settings.verbosity = verbosity
            if organism is None:
                raise ValueError(
                    f"No organism with name='{name}' is found, please create a organism record!"
                )
            if organism._state.adding:  # type:ignore
                organism.save()  # type:ignore
            logger.debug(f"set organism: {organism}")
            self._organism = organism


settings = Settings()
settings.__doc__ = """Global :class:`~bionty.core.Settings`."""

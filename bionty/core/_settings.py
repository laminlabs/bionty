from __future__ import annotations

from lamin_utils import logger

from bionty.models import Organism


class Settings:
    """Settings.

    Directly use `bt.settings` rather than instantiating this class yourself.
    """

    def __init__(self):
        self._organism = "human"

    @property
    def organism(self) -> Organism | None:
        """Default organism argument (default `"human"`).

        Default organism to use in cases of ambiguity. For instance, gene symbols are duplicated across organisms and need to be disambiguated.

        Examples:

            ::

                bionty.settings.organism = "mouse"
        """
        if isinstance(self._organism, str):
            self.organism = self._organism  # type: ignore
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
            organisms = Organism.from_values([name])
            ln.settings.verbosity = verbosity
            if len(organisms) == 0:
                raise ValueError(
                    f"No organism with name='{name}' is found, please create a organism record!"
                )
            else:
                organism = organisms[0]
            if organism._state.adding:  # type:ignore
                organism.save()  # type:ignore
            self._organism = organism


settings = Settings()
settings.__doc__ = """Global :class:`~bionty.core.Settings`."""

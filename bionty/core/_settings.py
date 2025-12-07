from __future__ import annotations

from lamin_utils import logger

from bionty.models import Organism


class Settings:
    """Settings.

    Directly use `bt.settings` rather than instantiating this class yourself.
    """

    def __init__(self):
        self._organism = None

    @property
    def organism(self) -> Organism | None:
        """Default organism argument (default `None`).

        Default organism to use in cases of ambiguity. For instance, gene symbols are duplicated across organisms and need to be disambiguated.

        Examples:

            ::

                bionty.settings.organism = "mouse"
        """
        if isinstance(self._organism, str):
            self.organism = self._organism  # type: ignore
        return self._organism

    @organism.setter
    def organism(self, name: str | Organism | None):
        if name is None:
            self._organism = None
            return
        if isinstance(name, Organism):
            self._organism = name
        else:
            organism = Organism.from_source(name=name, mute=True)
            if isinstance(organism, list):
                organism = organism[0]
            if organism._state.adding:
                organism.save()
            self._organism = organism


settings = Settings()
settings.__doc__ = """Global :class:`~bionty.core.Settings`."""

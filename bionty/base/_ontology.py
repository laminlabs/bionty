import warnings
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Union

import pandas as pd
import pronto


class Ontology(pronto.Ontology):
    """Interface with ontologies via pronto.

    Also see: https://pronto.readthedocs.io/en/stable/api/pronto.Ontology.html

    Args:
        handle: Path to an ontology source file.
        import_depth: The maximum depth of imports to resolve in the ontology tree.
        timeout: The timeout in seconds to use when performing network I/O.
        threads: The number of threads to use when parsing.
        url: The url of the ontology.
        prefix: Dev only -> prefix for get_term.
    """

    def __init__(
        self,
        handle: Union[str, Path, BinaryIO, None] = None,
        import_depth: int = -1,
        timeout: int = 100,
        threads: Optional[int] = None,
        prefix: str = "",
    ) -> None:
        self._prefix = prefix
        warnings.filterwarnings("ignore", category=pronto.warnings.ProntoWarning)
        super().__init__(
            handle=handle, import_depth=import_depth, timeout=timeout, threads=threads
        )

    def get_term(self, term):
        """Search an ontology by its id."""
        try:
            return super().get_term(term)
        except KeyError:
            return super().get_term(f"{self._prefix}{term.replace(':', '_')}")

    def to_df(
        self,
        source: Optional[str] = None,
        include_id_prefixes: Optional[Dict[str, List[str]]] = None,
    ):
        """Convert pronto.Ontology to a DataFrame with columns id, name, parents."""

        def filter_include_id_prefixes(terms: pronto.ontology._OntologyTerms):
            if include_id_prefixes and source in list(include_id_prefixes.keys()):
                return list(
                    filter(
                        lambda val: any(
                            val.id.startswith(prefix)
                            for prefix in include_id_prefixes[source]  # type: ignore
                        ),
                        terms,
                    )
                )
            else:
                return terms

        if source is not None:
            prefix_list = (
                include_id_prefixes.get(source)
                if include_id_prefixes is not None
                else None
            )
        else:
            prefix_list = None

        filtered_terms = filter_include_id_prefixes(self.terms())

        df_values = []
        for term in filtered_terms:
            # skip terms without id or name
            if (not term.id) or (not term.name):
                continue

            # term definition text
            definition = None if term.definition is None else term.definition.title()

            # concatenate synonyms into a string
            synonyms = "|".join(
                [i.description for i in term.synonyms if i.scope == "EXACT"]
            )
            if len(synonyms) == 0:
                synonyms = None  # type:ignore

            # get 1st degree parents as a list
            if prefix_list is not None:
                superclasses = [
                    s.id
                    for s in term.superclasses(distance=1, with_self=False).to_set()
                    if s.id.startswith(tuple(prefix_list))
                ]
            else:
                superclasses = [
                    s.id
                    for s in term.superclasses(distance=1, with_self=False).to_set()
                ]

            df_values.append((term.id, term.name, definition, synonyms, superclasses))

        df = pd.DataFrame(
            df_values,
            columns=["ontology_id", "name", "definition", "synonyms", "parents"],
        ).set_index("ontology_id")

        # needed to avoid erroring in .lookup()
        df["name"] = df["name"].fillna("")

        return df

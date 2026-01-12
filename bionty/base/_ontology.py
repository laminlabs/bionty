from __future__ import annotations

import sys
from typing import TYPE_CHECKING, BinaryIO

import pandas as pd
from lamin_utils import logger

if TYPE_CHECKING:
    from pathlib import Path


def import_pronto():
    """Import pronto if not already imported."""
    try:
        import warnings

        import pronto  # type: ignore

        if logger._verbosity <= 3:
            # Only apply if not building docs - leads to 'category is not a class' warnings otherwise
            if "sphinx" not in sys.modules:
                warnings.filterwarnings(
                    "ignore", category=pronto.warnings.ProntoWarning
                )

        return pronto
    except ImportError as exc:
        raise ImportError(
            "pronto is not installed. Please install it with `pip install pronto`."
        ) from exc


# Try to create the real class, fall back to a stub
try:
    pronto = import_pronto()

    class Ontology(pronto.Ontology):  # type:ignore
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
            handle: str | Path | BinaryIO | None = None,
            import_depth: int = -1,
            timeout: int = 100,
            threads: int | None = None,
            prefix: str = "",
        ) -> None:
            self._prefix = prefix
            try:
                logger.debug(f"Attempting to parse ontology file: {handle}")
                super().__init__(
                    handle=handle,
                    import_depth=import_depth,
                    timeout=timeout,
                    threads=threads,
                )
                logger.debug("Ontology parsing successful")
            except Exception as e:
                if "ParseError" in str(type(e).__name__) or "unclosed token" in str(e):
                    logger.warning(f"Skipping corrupted ontology file: {handle}")
                    raise ValueError(f"Corrupted ontology file: {str(e)}") from e
                else:
                    raise

        def get_term(self, term):
            """Search an ontology by its id."""
            try:
                return super().get_term(term)
            except KeyError:
                return super().get_term(f"{self._prefix}{term.replace(':', '_')}")

        def to_df(
            self,
            source: str | None = None,
            include_rel: str | None = None,
            include_id_prefixes: dict[str, list[str]] | None = None,
        ):
            """Convert `pronto.Ontology` to a DataFrame with columns id, name, parents, definition, and synonyms.

            Args:
                source: The source of the ontology terms to include. If None, all terms are included.
                include_rel: The relationship ID to include when gathering parent relationships.
                    If provided, it extends the superclasses with the specified relationship.
                include_id_prefixes: A dictionary mapping sources to lists of ID prefixes.
                    Only terms with IDs starting with these prefixes will be included for the specified source.

            Returns:
                A DataFrame containing the filtered ontology terms with columns:
                - ontology_id (index): The unique identifier for each term.
                - name: The name of the term.
                - definition: The definition of the term (None if not available).
                - synonyms: A pipe-separated string of exact synonyms (None if no synonyms).
                - parents: A list of parent term IDs, including superclasses and optionally the specified relationship.
            """
            logger.info(f"starting ontology `to_df()` conversion for source: {source}")

            def filter_include_id_prefixes(terms: pronto.ontology._OntologyTerms):  # type:ignore
                if include_id_prefixes and source in list(include_id_prefixes.keys()):
                    logger.info(
                        f"filtering terms by ID prefixes for source {source}: {include_id_prefixes[source]}"
                    )
                    return list(
                        filter(
                            lambda val: any(
                                val.id.startswith(f"{prefix}")
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

            logger.info("filtering terms by ID prefixes...")
            filtered_terms = filter_include_id_prefixes(self.terms())

            logger.info("processing individual terms...")
            df_values = []

            processed_count = 0
            log_interval = max(1, len(filtered_terms) // 20)  # log every 5% of terms

            for i, term in enumerate(filtered_terms):
                if i % log_interval == 0 and i > 0:
                    print("  ", end="")
                    logger.info(
                        f"Processed {i}/{len(filtered_terms)} terms ({i / len(filtered_terms) * 100:.1f}%)"
                    )

                # skip terms without id or name
                if (not term.id) or (not term.name):
                    continue

                # term definition text
                definition = (
                    None if term.definition is None else term.definition.title()
                )

                # concatenate synonyms into a string
                synonyms = "|".join(
                    [
                        synonym.description
                        for synonym in term.synonyms
                        if synonym.scope == "EXACT"
                    ]
                )
                if len(synonyms) == 0:
                    synonyms = None  # type:ignore

                # get 1st degree parents and additional relatonships (include_rel such as 'part_of')
                superclasses = [
                    superclass.id
                    for superclass in term.superclasses(
                        distance=1, with_self=False
                    ).to_set()
                ]

                if include_rel is not None:
                    if include_rel in [i.id for i in term.relationships]:
                        superclasses.extend(
                            [
                                superclass.id
                                for superclass in term.objects(
                                    self.get_relationship(include_rel)
                                )
                            ]
                        )

                if prefix_list is not None:
                    superclasses = [
                        superclass
                        for superclass in superclasses
                        if superclass.startswith(tuple(prefix_list))
                    ]

                df_values.append(
                    (term.id, term.name, definition, synonyms, superclasses)
                )
                processed_count += 1

            logger.success(f"processed {processed_count} terms")

            df = pd.DataFrame(
                df_values,
                columns=["ontology_id", "name", "definition", "synonyms", "parents"],
            )
            logger.success(f"created DataFrame with {len(df)} rows")

            df["ontology_id"] = [
                i.replace(self._prefix, "").replace("_", ":") for i in df["ontology_id"]
            ]
            df["parents"] = [
                [j.replace(self._prefix, "").replace("_", ":") for j in i]
                for i in df["parents"]
            ]

            # needed to avoid erroring in .lookup()
            df["name"] = df["name"].fillna("")
            logger.success("conversion completed")

            return df.set_index("ontology_id")

except ImportError:
    # Create a stub class that raises an error when instantiated
    class Ontology:  # type:ignore
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "pronto is not installed. Please install it with `pip install pronto`."
            )

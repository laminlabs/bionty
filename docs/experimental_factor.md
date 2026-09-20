---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# ExperimentalFactor

Bionty provides access to the following public {class}`~bionty.ExperimentalFactor` ontologies:

1. [Experimental Factor Ontology](https://www.ebi.ac.uk/ols/ontologies/efo)

Here we show how to access and search ExperimentalFactor ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

experimentalfactors = bt.ExperimentalFactor.public(organism="all")
experimentalfactors
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = experimentalfactors.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = experimentalfactors.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.sequencer
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["sequencer"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = experimentalfactors.lookup(experimentalfactors.ontology_id)
```

```python
lookup.efo_0003739
```

## Search terms

Search behaves in the same way as it does for registries:

```python
experimentalfactors.search("single-cell rna seq").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
experimentalfactors.search("single-cell RNA-seq").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
experimentalfactors.search(
    "protocol that provides the expression profiles of single cells",
    field=experimentalfactors.definition,
).head()
```

## Standardize ExperimentalFactor identifiers

Let us generate a `DataFrame` that stores a number of ExperimentalFactor identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "EFO:0011021",
        "EFO:1002050",
        "EFO:1002047",
        "EFO:1002049",
        "This experimentalfactor does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = experimentalfactors.validate(df_orig.index, experimentalfactors.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.ExperimentalFactor").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.ExperimentalFactor", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="efo", organism="all"
).first()
experimentalfactors= bt.ExperimentalFactor.public(source=source)
experimentalfactors
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

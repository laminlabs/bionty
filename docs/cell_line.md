---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# CellLine

Bionty provides access to the following public {class}`~bionty.CellLine` ontologies:

1. [Cellosaurus](https://www.cellosaurus.org/)
2. [Cell Line Ontology](https://github.com/CLO-ontology/CLO)

Here we show how to access and search CellLine ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

celllines = bt.CellLine.public(organism="all")
celllines
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = celllines.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = celllines.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.hek293
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["HEK293"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = celllines.lookup(celllines.ontology_id)
```

```python
lookup.cvcl_0045
```

## Search terms

Search behaves in the same way as it does for registries:

```python
celllines.search("hek293").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
celllines.search("Human Embryonic Kidney 293").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
celllines.search(
    "suspension cell line",
    field=celllines.description,
).head()
```

## Standardize CellLine identifiers

Let us generate a `DataFrame` that stores a number of CellLine identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "253D cell",
        "HEK293",
        "2C1H7 cell",
        "283TAg cell",
        "This cellline does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = celllines.validate(df_orig.index, celllines.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.CellLine").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.CellLine", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="cellosaurus", organism="all"
).first()
celllines= bt.CellLine.public(source=source)
celllines
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

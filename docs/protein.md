---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# Protein

Bionty provides access to the following public {class}`~bionty.Protein` ontologies:

1. [Uniprot](https://www.uniprot.org/)

Here we show how to access and search Protein ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

proteins = bt.Protein.public(organism="human")
proteins
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = proteins.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = proteins.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.ac3
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["AC3"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = proteins.lookup(proteins.gene_symbol)
```

```python
lookup.rab4a
```

## Search terms

Search behaves in the same way as it does for registries:

```python
proteins.search("RAS").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
proteins.search("member of RAS oncogene family like 2B").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
proteins.search(
    "RABL2B",
    field=proteins.gene_symbol,
).head()
```

## Standardize Protein identifiers

Let us generate a `DataFrame` that stores a number of Protein identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "A0A024QZ08",
        "X6RLV5",
        "X6RM24",
        "A0A024QZQ1",
        "This protein does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = proteins.validate(df_orig.index, proteins.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.Protein").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.Protein", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="uniprot", organism="human"
).first()
proteins= bt.Protein.public(source=source)
proteins
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

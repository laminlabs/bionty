---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# Tissue

Bionty provides access to the following public {class}`~bionty.Tissue` ontologies:

1. [Uberon](http://obophenotype.github.io/uberon)

Here we show how to access and search Tissue ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

tissues = bt.Tissue.public(organism="all")
tissues
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = tissues.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = tissues.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.alveolus_of_lung
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["alveolus of lung"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = tissues.lookup(tissues.ontology_id)
```

```python
lookup.uberon_0000031
```

## Search terms

Search behaves in the same way as it does for registries:

```python
tissues.search("lung alveolus").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
tissues.search("nasal sac").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
tissues.search(
    "spherical outcropping of the respiratory",
    field=tissues.definition,
).head()
```

## Standardize Tissue identifiers

Let us generate a `DataFrame` that stores a number of Tissue identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "UBERON:0000000",
        "UBERON:0000005",
        "UBERON:0000001",
        "UBERON:0000002",
        "This tissue does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = tissues.validate(df_orig.index, tissues.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.Tissue").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.Tissue", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="uberon", organism="all"
).first()
tissues= bt.Tissue.public(source=source)
tissues
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

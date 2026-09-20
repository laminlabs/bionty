---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# Ethnicity

Bionty provides access to the following public {class}`~bionty.Ethnicity` ontologies:

1. [Human Ancestry Ontology](https://github.com/EBISPOT/hancestro)

Here we show how to access and search Ethnicity ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

ethnicitys = bt.Ethnicity.public(organism="human")
ethnicitys
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = ethnicitys.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = ethnicitys.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.american
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["American"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = ethnicitys.lookup(ethnicitys.ontology_id)
```

```python
lookup.hancestro_0463
```

## Search terms

Search behaves in the same way as it does for registries:

```python
ethnicitys.search("American").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
ethnicitys.search("Caucasian").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
ethnicitys.search(
    "General characterisation of the Ancestry of a population",
    field=ethnicitys.definition,
).head()
```

## Standardize Ethnicity identifiers

Let us generate a `DataFrame` that stores a number of Ethnicity identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "Mende",
        "European",
        "South Asian",
        "Arab",
        "This ethnicity does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = ethnicitys.validate(df_orig.index, ethnicitys.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.Ethnicity").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.Ethnicity", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="hancestro", organism="human"
).first()
ethnicitys= bt.Ethnicity.public(source=source)
ethnicitys
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

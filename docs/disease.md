---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# Disease

Bionty provides access to the following public {class}`~bionty.Disease` ontologies:

1. [Mondo](https://mondo.monarchinitiative.org/)
2. [Human Disease](https://disease-ontology.org/)

Here we show how to access and search Disease ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

diseases = bt.Disease.public(organism="all")
diseases
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = diseases.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = diseases.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.alzheimer_disease
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["Alzheimer disease"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = diseases.lookup(diseases.ontology_id)
```

```python
lookup.mondo_0004975
```

## Search terms

Search behaves in the same way as it does for registries:

```python
diseases.search("parkinson disease").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
diseases.search("paralysis agitans").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
diseases.search(
    "progressive degenerative disorder of the central nervous system",
    field=diseases.definition,
).head()
```

## Standardize Disease identifiers

Let us generate a `DataFrame` that stores a number of Disease identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "supraglottis cancer",
        "alexia",
        "trigonitis",
        "paranasal sinus disorder",
        "This disease does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = diseases.validate(df_orig.index, diseases.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.Disease").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.Disease", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="mondo", organism="all"
).first()
diseases= bt.Disease.public(source=source)
diseases
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

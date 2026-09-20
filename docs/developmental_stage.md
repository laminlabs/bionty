---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# DevelopmentalStage

Bionty provides access to the following public {class}`~bionty.DevelopmentalStage` ontologies:

1. [Human Developmental Stages](https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv)
2. [Mouse Developmental Stages](https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv)

Here we show how to access and search DevelopmentalStage ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

developmentalstages = bt.DevelopmentalStage.public(organism="human")
developmentalstages
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = developmentalstages.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = developmentalstages.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.organogenesis_stage
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["organogenesis stage"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = developmentalstages.lookup(developmentalstages.ontology_id)
```

```python
lookup.hsapdv_0000015
```

## Search terms

Search behaves in the same way as it does for registries:

```python
developmentalstages.search("organogenesis").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
developmentalstages.search("developmental stage").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
developmentalstages.search(
    "Prenatal Stage That Starts With Fertilization",
    field=developmentalstages.definition,
).head()
```

## Standardize DevelopmentalStage identifiers

Let us generate a `DataFrame` that stores a number of DevelopmentalStage identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "blastula stage",
        "Carnegie stage 03",
        "neurula stage",
        "organogenesis stage",
        "This developmentalstage does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = developmentalstages.validate(df_orig.index, developmentalstages.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.DevelopmentalStage").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.DevelopmentalStage", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="hsapdv", organism="human"
).first()
developmentalstages= bt.DevelopmentalStage.public(source=source)
developmentalstages
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

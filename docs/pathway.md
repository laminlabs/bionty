---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# Pathway

Bionty provides access to the following public {class}`~bionty.Pathway` ontologies:

1. [Gene Ontology](https://bioportal.bioontology.org/ontologies/GO)
2. [Pathway Ontology](https://bioportal.bioontology.org/ontologies/PW)

Here we show how to access and search Pathway ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

pathways = bt.Pathway.public(organism="all")
pathways
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = pathways.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = pathways.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.acetyl_coa_assimilation_pathway
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["acetyl-CoA assimilation pathway"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = pathways.lookup(pathways.ontology_id)
```

```python
lookup.go_0019681
```

## Search terms

Search behaves in the same way as it does for registries:

```python
pathways.search("acetyl-coa assimilation").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
pathways.search("acetyl-CoA catabolism").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
pathways.search(
    "chemical reactions and pathways resulting in the breakdown of acetyl-CoA",
    field=pathways.definition,
).head()
```

## Standardize Pathway identifiers

Let us generate a `DataFrame` that stores a number of Pathway identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "GO:1905210",
        "GO:1905211",
        "GO:1905212",
        "GO:1905208",
        "This pathway does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = pathways.validate(df_orig.index, pathways.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.Pathway").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.Pathway", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="go", organism="all"
).first()
pathways= bt.Pathway.public(source=source)
pathways
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

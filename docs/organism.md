---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# Organism

Bionty provides access to the following public {class}`~bionty.Organism` ontologies:

1. [Ensembl Species](https://useast.ensembl.org/info/about/species.html)
2. [NCBI Taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy)

Here we show how to access and search Organism ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

organisms = bt.Organism.public(organism="vertebrates")
organisms
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = organisms.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = organisms.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.giant_panda
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["giant panda"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = organisms.lookup(organisms.scientific_name)
```

```python
lookup.ailuropoda_melanoleuca
```

## Search terms

Search behaves in the same way as it does for registries:

```python
organisms.search("rabbit").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
organisms.search("sapiens").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
organisms.search(
    "oryctolagus_cuniculus",
    field=organisms.scientific_name,
).head()
```

## Standardize Organism identifiers

Let us generate a `DataFrame` that stores a number of Organism identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "spiny chromis",
        "silver-eye",
        "platyfish",
        "california sea lion",
        "This organism does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = organisms.validate(df_orig.index, organisms.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.Organism").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.Organism", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="ensembl", organism="vertebrates"
).first()
organisms= bt.Organism.public(source=source)
organisms
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

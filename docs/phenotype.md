---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# Phenotype

Bionty provides access to the following public {class}`~bionty.Phenotype` ontologies:

1. [Human Phenotype](https://hpo.jax.org/app)
2. [Phecodes](https://phewascatalog.org/phecodes_icd10)
3. [PATO](https://github.com/pato-ontology/pato)
4. [Mammalian Phenotype](http://obofoundry.org/ontology/mp.html)

Here we show how to access and search Phenotype ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

phenotypes = bt.Phenotype.public(organism="human")
phenotypes
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = phenotypes.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = phenotypes.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.eeg_with_persistent_abnormal_rhythmic_activity
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["EEG with persistent abnormal rhythmic activity"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = phenotypes.lookup(phenotypes.ontology_id)
```

```python
lookup.hp_0000003
```

## Search terms

Search behaves in the same way as it does for registries:

```python
phenotypes.search("dysplasia").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
phenotypes.search("Congenital hip dysplasia").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
phenotypes.search(
    "lack of development of speech and language",
    field=phenotypes.definition,
).head()
```

## Standardize Phenotype identifiers

Let us generate a `DataFrame` that stores a number of Phenotype identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "Specific learning disability",
        "Dystonia",
        "Cerebral hemorrhage",
        "Slurred speech",
        "This phenotype does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = phenotypes.validate(df_orig.index, phenotypes.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.Phenotype").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.Phenotype", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="hp", organism="human"
).first()
phenotypes= bt.Phenotype.public(source=source)
phenotypes
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

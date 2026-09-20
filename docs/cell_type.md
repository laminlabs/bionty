---
execute_via: python
---

<!-- auto-generated-docs-via-entity-generation -->

# CellType

Bionty provides access to the following public {class}`~bionty.CellType` ontologies:

1. [Cell Ontology](https://obophenotype.github.io/cell-ontology)

Here we show how to access and search CellType ontologies to standardize new data.

Let us create a public ontology accessor with the `.public()` method, which chooses a default public ontology source from {class}`~docs:bionty.Source`.
It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
import bionty as bt
import pandas as pd

celltypes = bt.CellType.public(organism="all")
celltypes
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = celltypes.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = celltypes.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.cd8_positive_alpha_beta_t_cell
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["CD8-positive, alpha-beta T cell"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = celltypes.lookup(celltypes.ontology_id)
```

```python
lookup.cl_0000625
```

## Search terms

Search behaves in the same way as it does for registries:

```python
celltypes.search("Tc1 cell").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
celltypes.search("Tc1 T lymphocyte").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
celltypes.search(
    "cd8-positive, alpha-beta positive t cell",
    field=celltypes.definition,
).head()
```

## Standardize CellType identifiers

Let us generate a `DataFrame` that stores a number of CellType identifiers, some of which corrupted:

```python
df_orig = pd.DataFrame(
    index=[
        "Boettcher cell",
        "bone marrow cell",
        "interstitial cell of ovary",
        "pancreatic ductal cell",
        "This celltype does not exist",
    ]
)
df_orig
```

We can check whether any of our values are validated against the ontology reference:

```python
validated = celltypes.validate(df_orig.index, celltypes.name)
df_orig.index[~validated]
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python tags=["hide-output"]
bt.Source.filter(entity="bionty.CellType").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.CellType", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.filter(
    name="cl", organism="all"
).first()
celltypes= bt.CellType.public(source=source)
celltypes
```
The currently used ontologies can be displayed using:

```python tags=["hide-output"]
bt.Source.filter(currently_used=True).to_dataframe()
```

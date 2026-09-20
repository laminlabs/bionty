---
execute_via: python
---

# CellMarker

lamindb provides access to the following public cell marker ontologies through [bionty](https://lamin.ai/docs/bionty):

1. [CellMarker](http://xteam.xbio.top/CellMarker)

Here we show how to access and search cell marker ontologies to standardize new data.

```python
import bionty as bt
import pandas as pd
```

## PublicOntology objects

Let us create a public ontology object with the `.public()` class method, which chooses a default public ontology source from {class}`~docs:bionty.Source`. It's a [PublicOntology](https://lamin.ai/docs/bionty.dev.publicontology) object, which you can think about as a public registry:

```python
public = bt.CellMarker.public(organism="human")
public
```

As for registries, you can export the ontology as a `DataFrame`:

```python
df = public.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.ontology`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = public.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.immp1l
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["IMMP1L"]
```

## Search terms

Search behaves in the same way as it does for registries:

```python
public.search("CD4").head(5)
```

Search another field (default is `.name`):

```python
public.search("CD4", field=public.gene_symbol).head(1)
```

## Standardize cell marker identifiers

Let us generate a `DataFrame` that stores a number of cell markers identifiers, some of which corrupted:

```python
markers = pd.DataFrame(
    index=[
        "KI67",
        "CCR7",
        "CD14",
        "CD8",
        "CD45RA",
        "CD4",
        "CD3",
        "CD127a",
        "PD1",
        "Invalid-1",
        "Invalid-2",
        "CD66b",
        "Siglec8",
        "Time",
    ]
)
```

Now let’s check which cell markers can be found in the reference:

```python
public.inspect(markers.index, public.name);
```

Logging suggests to map synonyms:

```python
synonyms_mapper = public.standardize(markers.index, return_mapper=True)
synonyms_mapper
```

Let's replace the synonyms with standardized names in the `DataFrame`:

```python
markers.rename(index=synonyms_mapper, inplace=True)
```

The `Time`, `Invalid-1` and `Invalid-2` are non-marker channels which won’t be curated by cell marker:

```python
public.inspect(markers.index, public.name);
```

We don't find `CD127a`, let's check in the lookup with auto-completion:

```python
lookup = public.lookup()
lookup.cd127
```

It should be cd127, we had a typo there with `cd127a`:

```python
curated_df = markers.rename(index={"CD127a": lookup.cd127.name})
```

Optionally, search:

```python
public.search("CD127a").head()
```

Now we see that all cell marker candidates validate:

```python
public.validate(curated_df.index, public.name);
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python
bt.Source.filter(entity="bionty.CellMarker").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.CellMarker", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.get(name="cellmarker", version="2.0", organism="human")
public = bt.CellMarker.public(source=source)
public
```

The currently used ontologies can be displayed using:

```python
bt.Source.filter(currently_used=True).to_dataframe()
```

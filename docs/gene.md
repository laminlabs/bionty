---
execute_via: python
---

# Gene

LaminDB provides access to the following public gene ontologies through [bionty](https://docs.lamin.ai/bionty).

Here we show how to access and search gene ontologies.

```bash
lamin init --storage ./test-public-ontologies --modules bionty
```

```python
import bionty as bt
import pandas as pd
```

## PublicOntology objects

Let us create a public ontology object with the `.public()` class method, which links a default public ontology source from {class}`~docs:bionty.Source`:

```python
public = bt.Gene.public(organism="human")
public
```

Just like you can with registries, you can export the `PublicOntology` object as a `DataFrame`:

```python
df = public.to_dataframe()
df.head()
```

Unlike registries, you can also export it as a Pronto object via `public.to_pronto()`.

## Look up terms

As for registries, terms can be looked up with auto-complete:

```python
lookup = public.lookup()
```

The `.` accessor provides normalized terms (lower case, only contains alphanumeric characters and underscores):

```python
lookup.tcf7
```

To look up the exact original strings, convert the lookup object to dict and use the `[]` accessor:

```python
lookup_dict = lookup.dict()
lookup_dict["TCF7"]
```

By default, the `name` field is used to generate lookup keys. You can specify another field to look up:

```python
lookup = public.lookup(public.ncbi_gene_id)
```

If multiple entries are matched, they are returned as a list:

```python
lookup.bt_100126572
```

## Search terms

Search behaves in the same way as it does for registries:

```python
public.search("TP53").head(3)
```

By default, search also covers synonyms and all other fields containing strings:

```python
public.search("PDL1").head(3)
```

You can turn search only in symbols by passing `field="symbol"`:

```python
public.search("PDL1", field="symbol").head(3)
```

Search specific field (by default, search is done on all fields containing strings):

```python
public.search("tumor protein p53", field=public.description).head()
```

## Standardize gene identifiers

Let us generate a `DataFrame` that stores a number of gene identifiers, some of which corrupted:

```python
data = {
    "gene symbol": ["A1CF", "A1BG", "FANCD1", "corrupted"],
    "ncbi id": ["29974", "1", "5133", "corrupted"],
    "ensembl_gene_id": [
        "ENSG00000148584",
        "ENSG00000121410",
        "ENSG00000188389",
        "ENSGcorrupted",
    ],
}
df_orig = pd.DataFrame(data).set_index("ensembl_gene_id")
df_orig
```

First we can check whether any of our values are validated against the ontology reference:

```python
validated = public.validate(df_orig.index, public.ensembl_gene_id)
df_orig.index[~validated]
```

Next, we validate which symbols are mappable against the ontology:

```python
# based on NCBI gene ID
public.validate(df_orig["ncbi id"], public.ncbi_gene_id)
```

```python
# based on Gene symbols
validated_symbols = public.validate(df_orig["gene symbol"], public.symbol)
df_orig["gene symbol"][~validated_symbols]
```

Here, 2 of the gene symbols are not validated. Inspect why:

```python
public.inspect(df_orig["gene symbol"], public.symbol);
```

Logging suggests to use `.standardize()`:

```python
mapped_symbol_synonyms = public.standardize(df_orig["gene symbol"])
mapped_symbol_synonyms
```

Optionally, you can return a mapper in the form of `{synonym1: standardized_name1, ...}`:

```python
public.standardize(df_orig["gene symbol"], return_mapper=True)
```

We can use the standardized symbols as the new standardized index:

```python
df_curated = df_orig.reset_index()
df_curated.index = mapped_symbol_synonyms
df_curated
```

You can convert identifiers by passing `return_field` to {meth}`~lamindb.models.CanCurate.standardize`:

```python
public.standardize(
    df_curated.index,
    field=public.symbol,
    return_field=public.ensembl_gene_id,
)
```

And return mappable identifiers as a dict:

```python
public.standardize(
    df_curated.index,
    field=public.symbol,
    return_field=public.ensembl_gene_id,
    return_mapper=True,
)
```

## Ontology source versions

For any given entity, we can choose from a number of versions:

```python
bt.Source.filter(entity="bionty.Gene").to_dataframe()
```

```python
# only lists the sources that are currently used
bt.Source.filter(entity="bionty.Gene", currently_used=True).to_dataframe()
```

When instantiating a Bionty object, we can choose a source or version:

```python
source = bt.Source.get(name="ensembl", version="release-116", organism="human")
public = bt.Gene.public(source=source)
public
```

The currently used ontologies can be displayed using:

```python
bt.Source.filter(currently_used=True).to_dataframe()
```

# Extend Bionty

This guide covers how to:

1. Add new terms & records, such as adding a new cell type to a cell type ontology
2. Add new ontologies, such as a new disease ontology
3. Add new entities that Bionty does not cover

## New terms and records

If you'd like to add new terms to an existing ontology: use [LaminDB](https://lamin.ai/docs).

## New ontologies

The easiest way to add new ontologies to existing entities is to adapt the `sources_local.yaml` file in the `$home/.lamin/bionty/versions` directory.
For example, to add a new disease ontology (termed "inhouse_diseases") with an associated version and URL, one adds the following lines to the `sources.local.yaml`.

```yaml
Disease:
  mondo:
    all:
      2023-02-06:
        source: http://purl.obolibrary.org/obo/mondo/releases/2023-02-06/mondo.owl
      2022-10-11:
        source: http://purl.obolibrary.org/obo/mondo/releases/2022-10-11/mondo.owl
    name: Mondo Disease Ontology
    website: https://mondo.monarchinitiative.org/
  doid:
    human:
      2023-01-30:
        source: http://purl.obolibrary.org/obo/doid/releases/2023-01-30/doid.obo
    name: Human Disease Ontology
    website: https://disease-ontology.org/
  inhouse_diseases:
    human:
      2000-01-01:
        source: http://download-my-diseases.com/releases/2000-01-01/mydiseases.owl
    name: My in-house Disease Ontology
    website: http://my-website.com
```

Use "all" if organism doesn't apply or unknown.

If desired, the new ontology can be set as default. See {doc}`./config` for more details.

## New entities

Adding new entities to Bionty requires subclassing the {class}`bionty.base.PublicOntology` and modifying the `sources_local.yaml` file.

The {class}`bionty.base.PublicOntology` requires several properties to be defined:

```python
organism: str,
source: str,
version: str,
```

These are automatically populated by either the currently used PublicOntology sources (see {doc}`./config`) or explicitly passed as parameters when initializing an Entity.

Hence, a new PublicOntology class `MyEntity` would be defined as:

```python
from bionty import PublicOntology


class MyEntity(PublicOntology):
    """MyEntity."""

    def __init__(
        self,
        organism: Optional[str] = None,
        source: Optional[Literal["mydatabase_1", "mydatabase_2"]] = None,
        version: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            source=source,
            version=version,
            organism=organism,
            **kwargs
        )
```

The `local.yml` would then need to be extended as:

```yaml
MyEntity:
  mysource_1:
    human:
      2042-01-01:
        source: http://my-url/releases/2042-01-01/mysource_1.owl
  mysource_2:
    all:
      2042-01-01:
        source: http://my-url/releases/2042-01-01/mysource_2.owl
```

Great! Now we've added a new PublicOntology class, which can be used with all PublicOntology functions! 🎉

# Configuration

## Public bionty sources

Bionty maintains a [sources.yaml](https://raw.githubusercontent.com/laminlabs/bionty/main/bionty/base/sources.yaml) listing public sources of each entity.
These sources are curated ([bionty-assets](https://github.com/laminlabs/bionty-assets)) and stored in a [bionty-assets instance](https://lamin.ai/laminlabs/bionty-assets/) to provide fast and reliable access.
Cached sources files are stored at your local `bionty/base/_dynamic/` directory.

## Display public sources

The available and currently used ontologies can also be printed with
`bionty.base.display_available_sources` or `bionty.base.display_currently_used_sources`.

## Structure of the sources.yaml

```yaml
entity: # Bionty entity class name, e.g. CellType
  source: # short name of the source, (CURIE prefix for ontologies) e.g. cl
    organism: # organism common name, (if none applied, use 'all') e.g. human
      version: # version of the source
        url: # "link to the source file"
```

## Default ontologies and versions in sources.yaml

For each entity, the **first source** and its **maximum version** defined in [sources.yaml](https://raw.githubusercontent.com/laminlabs/bionty/main/bionty/base/sources.yaml) is used as default.
To set your own default ontology and version, shift the order of entries.
For example, in the following "doid" used when "organism" is specified as "human":

(highlighted sources are considered the default)

```{code-block} yaml
---
emphasize-lines: 2-6,12-16
---
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

<br>

We may change the default to "inhouse_diseases" when "organism" is specified as "human", by the following:

```{code-block} yaml
---
emphasize-lines: 2,3,7-9,12-16
---
Disease:
  mondo:
    all:
      2022-10-11:
        source: http://purl.obolibrary.org/obo/mondo/releases/2022-10-11/mondo.owl
      2023-02-06:
        source: http://purl.obolibrary.org/obo/mondo/releases/2023-02-06/mondo.owl
    name: Mondo Disease Ontology
    website: https://mondo.monarchinitiative.org/
  inhouse_diseases:
    human:
      2000-01-01:
        source: http://download-my-diseases.com/releases/2000-01-01/mydiseases.owl
    name: My in-house Disease Ontology
    website: http://my-website.com
  doid:
    human:
      2023-01-30:
        source: http://purl.obolibrary.org/obo/doid/releases/2023-01-30/doid.obo
    name: Human Disease Ontology
    website: https://disease-ontology.org/
```

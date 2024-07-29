# Configuration

## Public bionty sources

Bionty maintains a [sources.yaml](https://raw.githubusercontent.com/laminlabs/bionty/main/bionty/sources/sources.yaml) listing public sources of each entity.

These sources are curated ([biony-assets](https://lamin.ai/docs/bionty-assets)) and stored at s3://bionty-assets to provide fast and reliable access.

Cached sources files are stored at your local `bionty/bionty/_dynamic/` directory.

## Local bionty sources

File `$home:/.lamin/bionty/sources_local.yaml` stores all locally available ontologies.

The content of this file is identical to the public `sources.yaml` for a freshly-installed Bionty.

**Users may edit this file in order to configure customized sources.**

## Display sources

The available and currently active ontologies can also be printed with
{func}`bionty_base.display_available_sources` or {func}`bionty_base.display_currently_used_sources`.

## Format of the sources yaml file

```yaml
entity: # Bionty entity class name, e.g. CellType
  source: # short name of the source, (CURIE prefix for ontologies) e.g. cl
    organism: # organism common name, (if none applied, use 'all') e.g. human
      version: # version of the source
        url: "link to the source file"
        md5: "md5 of the source file"
```

## Setting default ontologies and versions

For each entity, the **first source** and its **maximum version** in `sources_local.yaml` is used as default.

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
        md5: 2b7d479d4bd02a94eab47d1c9e64c5db
      2022-10-11:
        source: http://purl.obolibrary.org/obo/mondo/releases/2022-10-11/mondo.owl
        md5: 04b808d05c2c2e81430b20a0e87552bb
    name: Mondo Disease Ontology
    website: https://mondo.monarchinitiative.org/
  doid:
    human:
      2023-01-30:
        source: http://purl.obolibrary.org/obo/doid/releases/2023-01-30/doid.obo
        md5: 9f0c92ad2896dda82195e9226a06dc36
    name: Human Disease Ontology
    website: https://disease-ontology.org/
  inhouse_diseases:
    human:
      2000-01-01:
        source: http://download-my-diseases.com/releases/2000-01-01/mydiseases.owl
        md5: md5 if available or leave out this row
    name: My in-house Disease Ontology
    website: http://my-website.com
```

<br>

We may change the default to "inhouse_diseases" when "organism" is specified as "human", by the following:

Note: changing the order of versions won't have an effect, as most recent version is taken as default.

```{code-block} yaml
---
emphasize-lines: 2,3,7-9,12-16
---
Disease:
  mondo:
    all:
      2022-10-11:
        source: http://purl.obolibrary.org/obo/mondo/releases/2022-10-11/mondo.owl
        md5: 04b808d05c2c2e81430b20a0e87552bb
      2023-02-06:
        source: http://purl.obolibrary.org/obo/mondo/releases/2023-02-06/mondo.owl
        md5: 2b7d479d4bd02a94eab47d1c9e64c5db
    name: Mondo Disease Ontology
    website: https://mondo.monarchinitiative.org/
  inhouse_diseases:
    human:
      2000-01-01:
        source: http://download-my-diseases.com/releases/2000-01-01/mydiseases.owl
        md5: md5 if available or leave out this row
    name: My in-house Disease Ontology
    website: http://my-website.com
  doid:
    human:
      2023-01-30:
        source: http://purl.obolibrary.org/obo/doid/releases/2023-01-30/doid.obo
        md5: 9f0c92ad2896dda82195e9226a06dc36
    name: Human Disease Ontology
    website: https://disease-ontology.org/
```

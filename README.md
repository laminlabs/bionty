[![Stars](https://img.shields.io/github/stars/laminlabs/bionty?logo=GitHub&color=yellow)](https://github.com/laminlabs/bionty)
[![pypi](https://img.shields.io/pypi/v/bionty?color=blue&label=pypi%20package)](https://pypi.org/project/bionty)

# bionty: Manage biological ontologies

- Access >20 public ontologies (Gene, Protein, CellType, …) through a single API, served from AWS S3 with high availability and low latency given some of the original ontology services are unreliable.
- Create records from entries in public ontologies using `.from_source()`.
- Access full underlying public ontologies via `.public()` to search & bulk-create records.
- Create in-house ontologies by extending public ontologies using hierarchical relationships among records (`.parents`).
- Use `.synonyms` and `.abbr` to manage synonyms.
- Safeguards against typos & duplications.
- Manage multiple ontology versions via `bionty.Source`.

Read the [docs](https://docs.lamin.ai/bionty).

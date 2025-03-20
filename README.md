[![Stars](https://img.shields.io/github/stars/laminlabs/bionty?logo=GitHub&color=yellow)](https://github.com/laminlabs/bionty)
[![pypi](https://img.shields.io/pypi/v/bionty?color=blue&label=pypi%20package)](https://pypi.org/project/bionty)

# bionty: Basic biological entities

- Access >20 public ontologies such as Gene, Protein, CellMarker, ExperimentalFactor, CellType, CellLine, Tissue, …
- Create records from entries in public ontologies using `.from_source()`.
- Access full underlying public ontologies via `.public()` to search & bulk-create records.
- Create in-house ontologies by extending public ontologies using hierarchical relationships among records (`.parents`).
- Use `.synonyms` and `.abbr` to manage synonyms.
- Safeguards against typos & duplications.
- Ontology versioning via the `bionty.Source` registry.

Read [docs](https://docs.lamin.ai/bionty).

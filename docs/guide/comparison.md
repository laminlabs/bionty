# Relating Bionty to other tools

Biological ontologies are structured frameworks that define and categorize biological entities along with the relationships that connect them.
Knowledge graphs, built upon these ontologies, extend this concept by creating interconnected networks of biological entities,
fostering a holistic understanding of complex biological systems.
Here, we will describe the similarities and differences between Bionty and other tools.

## Ontology mappers: [Bionty](https://lamin.ai/docs/bionty)

- Mapping against biological ontologies streamlines data interpretation and communication by establishing a common vocabulary and framework,
  facilitating accurate cross-disciplinary analysis and knowledge exchange within the realm of biological research.

- [Bionty](https://lamin.ai/docs/bionty) is a Python package that provides unified access to biological ontologies.
  It further provides an API to curate biological metadata in standalone mode and as an SQL plugin as part of the [Lamin platform](https://lamin.ai/) by mapping against ontologies.
  To enable the curation of previously unexplored biological data, Bionty can be extended with custom in-house ontologies.
  [Bionty](https://lamin.ai/docs/bionty) is not designed to build ontologies or knowledge graphs.

## Data models: [BioLink](https://biolink.github.io/biolink-model/)

- Data models are structured frameworks used to represent and organize information systematically for efficient storage, retrieval, and analysis of data.
  In the context of the life sciences, data models provide a common language for describing biological entities and the intricate relationships between them.
  By standardizing how data is structured and interconnected, these models enable researchers, databases, and applications to communicate and collaborate effectively,
  leading to more comprehensive insights and discoveries in the field of biology.

- [BioLink](https://biolink.github.io/biolink-model/) is a standardized data model designed to facilitate the integration and querying of biological data from various sources in knowledge graphs.
  It provides a structured way to represent biological entities, their attributes, and the relationships between them, enhancing interoperability in bioinformatics.
  The [Biolink Model](https://biolink.github.io/biolink-model/) is primarily a schema in YAML syntax that is translated into various formats.
  [BioLink](https://biolink.github.io/biolink-model/) does not provide tooling to access the generated knowledge graphs.

## Knowledge graph builders: [Biocypher](https://biocypher.org/)

- Knowledge graphs in the life sciences are information networks that capture complex relationships and connections between various biological entities.
  By representing data in a graph-like structure, they enable researchers to enhance understanding of the intricate interactions that drive biological systems.

- [Biocypher](https://biocypher.org/) is a Python package that simplifies the creation of knowledge graphs.
  Built upon a modular framework, [Biocypher](https://biocypher.org/) empowers users to manipulate and harmonize ontologies.
  [Biocypher](https://biocypher.org/) does not focus on data curation or SQL entities and is primarily for developers interested in building their own knowledge graphs.

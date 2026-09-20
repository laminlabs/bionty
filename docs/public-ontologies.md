# Public biological ontologies

Bionty makes it easy to access different public ontologies with a single API, served with high availablity and low latency from AWS S3.[^outages]

## Modeling public ontologies

In Bionty, a biological entity type (e.g., `Organism`) is a variable that takes values from a vocabulary of terms with biological meaning:

1. There are different roughly equivalent vocabularies for the same entity type. For example, one can describe organism with the vocabulary of the scientific names, the vocabulary of the common names, or the vocabulary of ontology IDs for the same organism.
2. There are different versions & sources of these vocabularies.
3. Terms in the vocabularies have different granularity, and are often hierarchical.

Often, vocabularies are based on a given version of a public reference ontology, but contain additional “custom” terms corresponding to "new knowledge" absent from reference ontologies. For example, new cell types or states, or new synthetic genes. If you face this situation, read how to extend public ontologies with in-house terms: {doc}`docs:manage-ontologies`.

The central class {class}`~bionty.base.PublicOntology` models 3 of the 4 above-mentioned properties of biological entity types:

1. Every `PublicOntology` object comes with a table of terms in which each column corresponds to an alternative vocabulary for the entity.
2. Every table is versioned & has a tracked reference source (typically, a public ontology).
3. Most tables have a children column that allows mapping hierarchies.
4. Adding user-defined records amounts to managing manage-ontologies through Bionty's SQL models.

## Public ontology guides

The guides cover the following entity types:

- {doc}`docs:gene` - [Ensembl](https://ensembl.org), [NCBI Gene](https://www.ncbi.nlm.nih.gov/gene)
- {doc}`docs:protein` - [Uniprot](https://www.uniprot.org/)
- {doc}`docs:organism` - [Ensembl Species](https://useast.ensembl.org/info/about/species.html). [NCBI Taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy)
- {doc}`docs:cell_line` - [Cell Line Ontology](https://github.com/CLO-ontology/CLO)
- {doc}`docs:cell_type` - [Cell Ontology](https://obophenotype.github.io/cell-ontology)
- {doc}`docs:cell_marker` - [CellMarker](http://xteam.xbio.top/CellMarker)
- {doc}`docs:tissue` - [Uberon](http://obophenotype.github.io/uberon)
- {doc}`docs:disease` - [Mondo](https://mondo.monarchinitiative.org), [Human Disease](https://disease-ontology.org), [ICD](https://www.who.int/standards/classifications/classification-of-diseases)
- {doc}`docs:phenotype` - [Human Phenotype](https://hpo.jax.org/app), [Phecodes](https://phewascatalog.org/phecodes_icd10), [PATO](https://github.com/pato-ontology/pato), [Mammalian Phenotype](http://obofoundry.org/ontology/mp.html), [Zebrafish Phenotype](http://obofoundry.org/ontology/zp.html)
- {doc}`docs:pathway` - [Gene Ontology](https://bioportal.bioontology.org/ontologies/GO), [Pathway Ontology](https://bioportal.bioontology.org/ontologies/PW)
- {doc}`docs:experimental_factor` - [Experimental Factor Ontology](https://www.ebi.ac.uk/ols/ontologies/efo)
- {doc}`docs:developmental_stage` - [Human Developmental Stages](https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv), [Mouse Developmental Stages](https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv)
- {doc}`docs:ethnicity` - [Human Ancestry Ontology](https://github.com/EBISPOT/hancestro)

You can see all supported ontology versions [here](https://github.com/laminlabs/bionty/blob/main/bionty/base/sources.yaml).

```{toctree}
:maxdepth: 1
:hidden:

gene
protein
organism
cell_line
cell_type
cell_marker
tissue
disease
phenotype
pathway
experimental_factor
developmental_stage
ethnicity
```

[^outages]: Some of the original ontology services suffer from outages or high latency of their REST services.

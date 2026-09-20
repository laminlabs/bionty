# Access public ontologies

This docs section shows how to access public biological ontologies.

For managing in-house ontologies, see {doc}`docs:manage-ontologies`.

You'll need a lamindb instance with the `bionty` schema module mounted.

```shell
lamin init --modules bionty
```

The guides cover the following entities.

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
<!--
- `Drug` - [Drug Ontology](https://bioportal.bioontology.org/ontologies/DRON), [ChEBI](https://www.ebi.ac.uk/chebi/)
  -->

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

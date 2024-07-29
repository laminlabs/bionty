# Concepts

## Entity

Let's define a biological entity (e.g., `Organism`) to be a variable that takes values from a vocabulary of terms with biological meaning.

1. There are different roughly equivalent vocabularies for the same entity. For example, one can describe organism with the vocabulary of the scientific names, the vocabulary of the common names, or the vocabulary of ontology IDs for the same organism.
2. There are different versions & sources of these vocabularies.
3. Terms in the vocabularies have different granularity, and are often hierarchical.
4. Typically, vocabularies are based on a given version of a public reference ontology, but contain additional “custom” terms corresponding to "new knowledge" absent from reference ontologies. For example, new cell types or states, new synthetic genes, etc.

## PublicOntology object

The central class {class}`~bionty_base.PublicOntology` models 3 of the 4 above-mentioned properties of biological entities:

1. Every `PublicOntology` object comes with a table of terms in which each column corresponds to an alternative vocabulary for the entity.
2. Every table is versioned & has a tracked reference source (typically, a public ontology).
3. Most tables have a children column that allows mapping hierarchies.
4. Adding user-defined records amounts to managing bioregistries, and we recommend using Bionty's SQL extension ([lnschema_bionty](https://lamin.ai/docs/lnschema-bionty)).

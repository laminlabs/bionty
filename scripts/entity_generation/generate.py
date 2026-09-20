from cookiecutter.main import cookiecutter
import jupytext
import shutil
from pathlib import Path

template = {
    "output": "",
    "entity": "",
    "example_value": "",
    "example_dict_value": "",
    "alternative_field_value": "",
    "alternative_field": "",
    "search_value": "",
    "search_synonyms_value": "",
    "search_field": "",
    "search_query": "",
    "identifiers": "",
    "database": "",
    "version": "",
    "organism": "",
    "sources": "",
}

protein = {
    "output": "protein",
    "entity": "Protein",
    "example_value": "ac3",
    "example_dict_value": "AC3",
    "alternative_field_value": "rab4a",
    "alternative_field": "gene_symbol",
    "search_value": "RAS",
    "search_synonyms_value": "member of RAS oncogene family like 2B",
    "search_field": "gene_symbol",
    "search_query": "RABL2B",
    "identifiers": "A0A024QZ08,X6RLV5,X6RM24,A0A024QZQ1",
    "database": "uniprot",
    "version": "2023-03",
    "organism": "human",
    "sources": "1. [Uniprot](https://www.uniprot.org/)",
}

organism = {
    "output": "organism",
    "entity": "Organism",
    "example_value": "giant_panda",
    "example_dict_value": "giant panda",
    "alternative_field_value": "ailuropoda_melanoleuca",
    "alternative_field": "scientific_name",
    "search_value": "rabbit",
    "search_synonyms_value": "sapiens",
    "search_field": "scientific_name",
    "search_query": "oryctolagus_cuniculus",
    "identifiers": "spiny chromis,silver-eye,platyfish,california sea lion",
    "database": "ensembl",
    "version": "release-116",
    "organism": "vertebrates",
    "sources": "1. [Ensembl Species](https://useast.ensembl.org/info/about/species.html),2. [NCBI Taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy)",
}

cell_line = {
    "output": "cell_line",
    "entity": "CellLine",
    "example_value": "hek293",
    "example_dict_value": "HEK293",
    "alternative_field_value": "cvcl_0045",
    "alternative_field": "ontology_id",
    "search_value": "hek293",
    "search_synonyms_value": "Human Embryonic Kidney 293",
    "search_field": "description",
    "search_query": "suspension cell line",
    "identifiers": "253D cell,HEK293,2C1H7 cell,283TAg cell",
    "database": "cellosaurus",
    "version": "54.0",
    "organism": "all",
    "sources": "1. [Cellosaurus](https://www.cellosaurus.org/),2. [Cell Line Ontology](https://github.com/CLO-ontology/CLO)",
}

cell_type = {
    "output": "cell_type",
    "entity": "CellType",
    "example_value": "cd8_positive_alpha_beta_t_cell",
    "example_dict_value": "CD8-positive, alpha-beta T cell",
    "alternative_field_value": "cl_0000625",
    "alternative_field": "ontology_id",
    "search_value": "Tc1 cell",
    "search_synonyms_value": "Tc1 T lymphocyte",
    "search_field": "definition",
    "search_query": "cd8-positive, alpha-beta positive t cell",
    "identifiers": "Boettcher cell,bone marrow cell,interstitial cell of ovary,pancreatic ductal cell",
    "database": "cl",
    "version": "2025-12-17",
    "organism": "all",
    "sources": "1. [Cell Ontology](https://obophenotype.github.io/cell-ontology)",
}

tissue = {
    "output": "tissue",
    "entity": "Tissue",
    "example_value": "alveolus_of_lung",
    "example_dict_value": "alveolus of lung",
    "alternative_field_value": "uberon_0000031",
    "alternative_field": "ontology_id",
    "search_value": "lung alveolus",
    "search_synonyms_value": "nasal sac",
    "search_field": "definition",
    "search_query": "spherical outcropping of the respiratory",
    "identifiers": "UBERON:0000000,UBERON:0000005,UBERON:0000001,UBERON:0000002",
    "database": "uberon",
    "version": "2025-12-04",
    "organism": "all",
    "sources": "1. [Uberon](http://obophenotype.github.io/uberon)",
}


disease = {
    "output": "disease",
    "entity": "Disease",
    "example_value": "alzheimer_disease",
    "example_dict_value": "Alzheimer disease",
    "alternative_field_value": "mondo_0004975",
    "alternative_field": "ontology_id",
    "search_value": "parkinson disease",
    "search_synonyms_value": "paralysis agitans",
    "search_field": "definition",
    "search_query": "progressive degenerative disorder of the central nervous system",
    "identifiers": "supraglottis cancer,alexia,trigonitis,paranasal sinus disorder",
    "database": "mondo",
    "version": "2026-01-06",
    "organism": "all",
    "sources": "1. [Mondo](https://mondo.monarchinitiative.org/),2. [Human Disease](https://disease-ontology.org/)",
}

phenotype = {
    "output": "phenotype",
    "entity": "Phenotype",
    "example_value": "eeg_with_persistent_abnormal_rhythmic_activity",
    "example_dict_value": "EEG with persistent abnormal rhythmic activity",
    "alternative_field_value": "hp_0000003",
    "alternative_field": "ontology_id",
    "search_value": "dysplasia",
    "search_synonyms_value": "Congenital hip dysplasia",
    "search_field": "definition",
    "search_query": "lack of development of speech and language",
    "identifiers": "Specific learning disability,Dystonia,Cerebral hemorrhage,Slurred speech",
    "database": "hp",
    "version": "2026-01-08",
    "organism": "human",
    "sources": "1. [Human Phenotype](https://hpo.jax.org/app),2. [Phecodes](https://phewascatalog.org/phecodes_icd10),3. [PATO](https://github.com/pato-ontology/pato),4. [Mammalian Phenotype](http://obofoundry.org/ontology/mp.html)",
}

pathway = {
    "output": "pathway",
    "entity": "Pathway",
    "example_value": "acetyl_coa_assimilation_pathway",
    "example_dict_value": "acetyl-CoA assimilation pathway",
    "alternative_field_value": "go_0019681",
    "alternative_field": "ontology_id",
    "search_value": "acetyl-coa assimilation",
    "search_synonyms_value": "acetyl-CoA catabolism",
    "search_field": "definition",
    "search_query": "chemical reactions and pathways resulting in the breakdown of acetyl-CoA",
    "identifiers": "GO:1905210,GO:1905211,GO:1905212,GO:1905208",
    "database": "go",
    "version": "2025-10-10",
    "organism": "all",
    "sources": "1. [Gene Ontology](https://bioportal.bioontology.org/ontologies/GO),2. [Pathway Ontology](https://bioportal.bioontology.org/ontologies/PW)",
}

experimental_factor = {
    "output": "experimental_factor",
    "entity": "ExperimentalFactor",
    "example_value": "sequencer",
    "example_dict_value": "sequencer",
    "alternative_field_value": "efo_0003739",
    "alternative_field": "ontology_id",
    "search_value": "single-cell rna seq",
    "search_synonyms_value": "single-cell RNA-seq",
    "search_field": "definition",
    "search_query": "protocol that provides the expression profiles of single cells",
    "identifiers": "EFO:0011021,EFO:1002050,EFO:1002047,EFO:1002049",
    "database": "efo",
    "version": "3.85.0",
    "organism": "all",
    "sources": "1. [Experimental Factor Ontology](https://www.ebi.ac.uk/ols/ontologies/efo)",
}

developmental_stage = {
    "output": "developmental_stage",
    "entity": "DevelopmentalStage",
    "example_value": "organogenesis_stage",
    "example_dict_value": "organogenesis stage",
    "alternative_field_value": "hsapdv_0000015",
    "alternative_field": "ontology_id",
    "search_value": "organogenesis",
    "search_synonyms_value": "developmental stage",
    "search_field": "definition",
    "search_query": "Prenatal Stage That Starts With Fertilization",
    "identifiers": "blastula stage,Carnegie stage 03,neurula stage,organogenesis stage",
    "database": "hsapdv",
    "version": "2025-01-23",
    "organism": "human",
    "sources": "1. [Human Developmental Stages](https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv),2. [Mouse Developmental Stages](https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv)",
}

ethnicity = {
    "output": "ethnicity",
    "entity": "Ethnicity",
    "example_value": "american",
    "example_dict_value": "American",
    "alternative_field_value": "hancestro_0463",
    "alternative_field": "ontology_id",
    "search_value": "American",
    "search_synonyms_value": "Caucasian",
    "search_field": "definition",
    "search_query": "General characterisation of the Ancestry of a population",
    "identifiers": "Mende,European,South Asian,Arab",
    "database": "hancestro",
    "version": "2025-10-14",
    "organism": "human",
    "sources": "1. [Human Ancestry Ontology](https://github.com/EBISPOT/hancestro)",
}


entities_args = [
    protein,
    organism,
    cell_line,
    cell_type,
    tissue,
    disease,
    phenotype,
    pathway,
    experimental_factor,
    developmental_stage,
    ethnicity,
]

for entity_args in entities_args:
    cookiecutter(
        template=str(Path(__file__).resolve().parent),
        no_input=True,
        overwrite_if_exists=True,
        extra_context=entity_args,
    )

    output_name = (
        entity_args["output"]
        if entity_args["output"] is not None
        else entity_args["entity"].lower()
    )
    entity_folder = Path(output_name)
    script_file = entity_folder / f"{output_name}.py"
    notebook_file = entity_folder / f"{output_name}.ipynb"
    output_folder = Path(__file__).resolve().parent.parent.parent / "docs"

    # Convert script to notebook
    with script_file.open("r") as file:
        script_content = file.read()
    notebook = jupytext.reads(script_content, fmt="py")
    jupytext.write(notebook, notebook_file, fmt="ipynb")

    # Clean up output
    shutil.move(str(notebook_file), output_folder)
    shutil.rmtree(entity_folder)

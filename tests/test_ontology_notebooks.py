from pathlib import Path

import nbproject_test as test

DOCS = Path(__file__).parents[1] / "docs"

ONTOLOGY_NOTEBOOKS = [
    "gene.ipynb",
    "cell_line.ipynb",
    "cell_marker.ipynb",
    "cell_type.ipynb",
    "developmental_stage.ipynb",
    "disease.ipynb",
    "ethnicity.ipynb",
    "experimental_factor.ipynb",
    "organism.ipynb",
    "pathway.ipynb",
    "phenotype.ipynb",
    "protein.ipynb",
    "tissue.ipynb",
]


def test_ontology_notebooks():
    for filename in ONTOLOGY_NOTEBOOKS:
        print(filename)
        test.execute_notebooks(DOCS / filename, write=True, print_outputs=False)

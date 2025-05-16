import pytest
from bionty.base._ontology_url import (
    OntologyNotFoundError,
    OntologyVersionNotFoundError,
    get_ontology_url,
)


def test_get_ontology_url():
    # Test with a known prefix and version
    url, ver = get_ontology_url("OBA", "2022-05-11")
    assert url == "http://purl.obolibrary.org/obo/oba/releases/2022-05-11/oba.owl"
    assert ver == "2022-05-11"

    # Test with a known prefix and no version
    prefix = "OBA"
    url, ver = get_ontology_url(prefix)
    assert url is not None
    assert ver is not None

    # A wrong version
    with pytest.raises(OntologyVersionNotFoundError):
        get_ontology_url("OBA", "wrong_version")

    # Test with an unknown prefix
    with pytest.raises(OntologyNotFoundError):
        get_ontology_url("UNKNOWN_PREFIX")

    prefixes = [
        "ncbitaxon",
        "clo",
        "cl",
        "uberon",
        "mondo",
        "doid",
        "efo",
        "pato",
        "hp",
        "mp",
        "zp",
        "go",
        "pw",
        "dron",
        "hsapdv",
        "mmusdv",
        "hancestro",
    ]

    for prefix in prefixes:
        url, ver = get_ontology_url(prefix)
        assert url is not None
        assert ver is not None

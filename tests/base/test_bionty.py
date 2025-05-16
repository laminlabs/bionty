import bionty.base as bt_base
import pytest


def test_unavailable_sources():
    with pytest.raises(ValueError):
        bt_base.CellType(source="random")


def test_diff_successful():
    disease_bt_1 = bt_base.Disease(source="mondo", version="2023-04-04")
    disease_bt_2 = bt_base.Disease(source="mondo", version="2023-02-06")

    new_entries, modified_entries = disease_bt_1.diff(disease_bt_2)
    assert len(new_entries) == 819
    assert len(modified_entries) == 249


def test_diff_value_errors():
    # Two different PublicOntology object types
    disease_bt = bt_base.Disease()
    phenotype_bt = bt_base.Phenotype()
    with pytest.raises(ValueError):
        disease_bt.diff(phenotype_bt)

    # Different sources
    disease_bt_1 = bt_base.Disease(source="mondo")
    disease_bt_2 = bt_base.Disease(source="doid")
    with pytest.raises(ValueError):
        disease_bt_1.diff(disease_bt_2)

    # Same version
    disease_bt_3 = bt_base.Disease(source="mondo", version="2023-04-04")
    disease_bt_4 = bt_base.Disease(source="mondo", version="2023-04-04")
    with pytest.raises(ValueError):
        disease_bt_3.diff(disease_bt_4)

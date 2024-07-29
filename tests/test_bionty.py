import bionty.base as bt
import pytest
from bionty.base._settings import settings


def test_unavailable_sources():
    with pytest.raises(ValueError):
        bt.CellType(source="random")


def test_reset_sources(monkeypatch):
    import shutil

    monkeypatch.setattr("builtins.input", lambda _: "y")

    shutil.copyfile(
        settings.current_sources.as_posix(), settings.lamindb_sources.as_posix()
    )
    bt.reset_sources()

    settings.current_sources.unlink()
    settings.local_sources.unlink()
    bt.reset_sources()


def test_diff_successful():
    disease_bt_1 = bt.Disease(source="mondo", version="2023-04-04")
    disease_bt_2 = bt.Disease(source="mondo", version="2023-02-06")

    new_entries, modified_entries = disease_bt_1.diff(disease_bt_2)
    assert len(new_entries) == 819
    assert len(modified_entries) == 249


def test_diff_value_errors():
    # Two different PublicOntology object types
    disease_bt = bt.Disease()
    phenotype_bt = bt.Phenotype()
    with pytest.raises(ValueError):
        disease_bt.diff(phenotype_bt)

    # Different sources
    disease_bt_1 = bt.Disease(source="mondo")
    disease_bt_2 = bt.Disease(source="doid")
    with pytest.raises(ValueError):
        disease_bt_1.diff(disease_bt_2)

    # Same version
    disease_bt_3 = bt.Disease(source="mondo", version="2023-04-04")
    disease_bt_4 = bt.Disease(source="mondo", version="2023-04-04")
    with pytest.raises(ValueError):
        disease_bt_3.diff(disease_bt_4)

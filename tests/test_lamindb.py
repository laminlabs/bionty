from pathlib import Path

import bionty.base as bt_base
from bionty.base._settings import settings
from bionty.base.dev._handle_sources import LAMINDB_INSTANCE_LOADED


def test_loaded_lamindb():
    import shutil

    shutil.copyfile(
        settings.current_sources.as_posix(), settings.lamindb_sources.as_posix()
    )

    lnenv = Path.home() / ".lamin/current_instance.env"
    with open(lnenv.as_posix(), "w") as f:
        f.write("schema_str=bionty")

    assert LAMINDB_INSTANCE_LOADED()

    ct = bt_base.CellType(version="2022-08-16")
    assert ct.source == "cl"

    lnenv.unlink()
    assert not LAMINDB_INSTANCE_LOADED()

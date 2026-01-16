import os
from functools import wraps
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()


def check_datasetdir_exists(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        settings.datasetdir.mkdir(exist_ok=True)
        return f(*args, **kwargs)

    return wrapper


def check_dynamicdir_exists(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        settings.dynamicdir.mkdir(exist_ok=True)
        return f(*args, **kwargs)

    return wrapper


class Settings:
    def __init__(
        self,
        datasetdir: str | Path | None = None,
        dynamicdir: str | Path | None = None,
    ):
        # setters convert to Path and resolve:
        self.datasetdir = (
            Path(datasetdir) if datasetdir is not None else (self.root_dir / "data/")
        )
        self.dynamicdir = (
            Path(dynamicdir)
            if dynamicdir is not None
            else (self.root_dir / "_dynamic/")
        )

    @property
    def root_dir(self):
        """Root directory for bionty."""
        root_dir_env = os.getenv("BIONTY_ROOT_DIR")
        if root_dir_env not in {None, ""}:
            return Path(root_dir_env).resolve()
        return ROOT_DIR

    @property
    def datasetdir(self):
        """Directory for datasets."""
        return self._datasetdir

    @datasetdir.setter
    def datasetdir(self, datasetdir: str | Path):
        self._datasetdir = Path(datasetdir).resolve()

    @property
    def dynamicdir(self):
        """Directory for datasets."""
        return self._dynamicdir

    @dynamicdir.setter
    def dynamicdir(self, dynamicdir: str | Path):
        self._dynamicdir = Path(dynamicdir).resolve()

    @property
    def public_sources(self):
        return self.root_dir / "sources.yaml"


settings = Settings()

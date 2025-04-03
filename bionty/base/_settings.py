from functools import wraps
from pathlib import Path
from typing import Union

HOME_DIR = Path(f"{Path.home()}/.lamin/bionty").resolve()
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
        datasetdir: str | Path = ROOT_DIR / "data/",
        dynamicdir: str | Path = ROOT_DIR / "_dynamic/",
    ):
        # setters convert to Path and resolve:
        self.datasetdir = datasetdir
        self.dynamicdir = dynamicdir

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
        return ROOT_DIR / "sources.yaml"


settings = Settings()

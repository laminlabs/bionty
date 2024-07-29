import os
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
        datasetdir: Union[str, Path] = ROOT_DIR / "data/",
        dynamicdir: Union[str, Path] = ROOT_DIR / "_dynamic/",
        versionsdir: Union[str, Path] = HOME_DIR / "versions/",
    ):
        # setters convert to Path and resolve:
        self.datasetdir = datasetdir
        self.dynamicdir = dynamicdir

        # needed when running with AWS Lambda
        if "LAMIN_SETTINGS_DIR" in os.environ:
            self.versionsdir = Path(
                f"{os.environ['LAMIN_SETTINGS_DIR']}/.lamin/bionty/versions"
            )
        else:
            self.versionsdir = versionsdir

        self.versionsdir.mkdir(exist_ok=True, parents=True)  # type: ignore

    @property
    def datasetdir(self):
        """Directory for datasets."""
        return self._datasetdir

    @datasetdir.setter
    def datasetdir(self, datasetdir: Union[str, Path]):
        self._datasetdir = Path(datasetdir).resolve()

    @property
    def dynamicdir(self):
        """Directory for datasets."""
        return self._dynamicdir

    @dynamicdir.setter
    def dynamicdir(self, dynamicdir: Union[str, Path]):
        self._dynamicdir = Path(dynamicdir).resolve()

    @property
    def versionsdir(self):
        """Directory for version yamls."""
        return self._versionsdir

    @versionsdir.setter
    def versionsdir(self, versionsdir: Union[str, Path]):
        self._versionsdir = Path(versionsdir).resolve()
        self._versionsdir.mkdir(exist_ok=True, parents=True)  # type: ignore

    @property
    def local_sources(self):
        return self.versionsdir / "sources_local.yaml"

    @property
    def public_sources(self):
        return ROOT_DIR / "sources.yaml"

    @property
    def current_sources(self):
        return self.versionsdir / ".current_sources.yaml"

    @property
    def lamindb_sources(self):
        return self.versionsdir / ".lamindb_current_sources.yaml"


settings = Settings()

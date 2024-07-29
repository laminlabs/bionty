from pathlib import Path

import pytest
from bionty.base.dev._io import url_download


@pytest.fixture
def local(tmp_path):
    url = "https://bionty-assets.s3.amazonaws.com/bfxpipelines.json"
    localpath = tmp_path / Path(url).name
    yield localpath, url
    if localpath.exists():
        localpath.unlink()


def test_url_download(local):
    localpath = local[0]
    url = local[1]
    assert not localpath.exists()

    downloaded_path = Path(url_download(url=url, localpath=localpath))
    assert downloaded_path.exists()

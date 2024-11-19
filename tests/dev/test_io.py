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


def test_local_file(local):
    # Create a temporary file in a temporary directory
    local_file = Path("/tmp/test.txt")
    with open(local_file, "w") as f:
        f.write("temporary file")
    assert local_file.exists()

    downloaded_path = Path(url_download(url=f"file://{local_file}", localpath=local[0]))

    with open(downloaded_path) as f:
        assert f.read() == "temporary file"
    local_file.unlink()

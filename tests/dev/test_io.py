import tempfile
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


def test_local_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        local_file = Path(temp_dir) / "test.txt"
        target_file = Path(temp_dir) / "downloaded.txt"
        test_content = "temporary file"

        local_file.write_text(test_content)
        assert local_file.exists(), "Test file was not created"

        downloaded_path = Path(
            url_download(url=f"file://{local_file}", localpath=target_file)
        )

        assert downloaded_path.exists(), "Downloaded file not found"
        assert downloaded_path.read_text() == test_content, "Content mismatch"

        if downloaded_path.exists():
            downloaded_path.unlink()

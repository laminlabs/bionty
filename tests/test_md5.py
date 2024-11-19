from pathlib import Path

import pytest
from bionty.base.dev._md5 import calculate_md5, verify_md5

CURRENT_DIR = Path(__file__).parent


@pytest.fixture(scope="module")
def file_fixture() -> tuple[str, str]:  # type: ignore
    file_path = "test_file.txt"
    with open(file_path, "w") as f:
        f.write("Hello, world!")
    expected_md5 = calculate_md5(file_path)
    yield file_path, expected_md5
    Path(file_path).unlink()


def test_verify_md5_with_matching_md5(file_fixture):
    file_path, expected_md5 = file_fixture
    assert verify_md5(file_path, expected_md5)


def test_verify_md5_with_non_matching_md5(file_fixture):
    file_path, _ = file_fixture
    assert not verify_md5(file_path, "0123456789abcdef0123456789abcdef")

import hashlib
from pathlib import Path
from typing import Union


def verify_md5(file_path: Union[Path, str], expected_md5: str) -> bool:
    """Compares the md5 sum of an input file and an expected md5 sum.

    Args:
        file_path: Path to the file to compare.
        expected_md5: The expected md5 sum that the input file should be compared to.

    Returns:
        True if the md5 sums match, False otherwise.
    """
    file_md5 = calculate_md5(file_path)

    if file_md5 == expected_md5:
        return True
    else:
        return False


def calculate_md5(file_path: Union[Path, str]) -> str:
    """Calculates the md5 sum of a file.

    Args:
        file_path: Path to the file to calculate the md5 sum for.

    Returns:
        The md5 sum.
    """
    with open(file_path, "rb") as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            md5.update(data)
        file_md5 = md5.hexdigest()

    return file_md5

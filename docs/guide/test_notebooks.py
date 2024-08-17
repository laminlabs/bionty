from pathlib import Path

import nbproject_test as test


def test_notebooks():
    nbdir = Path(__file__).parent
    test.execute_notebooks(nbdir, write=True)

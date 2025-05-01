"""IDs.

Entity-related generators:

.. autosummary::
   :toctree: .

   organism
   gene
   protein
   cellmarker
   ontology
   source

"""

import hashlib
import secrets
import string
from typing import Optional


# temporarily duplicated until we figure out the new place for
# ids in lamindb
def base62(n_char: int) -> str:
    """Random Base62 string."""
    alphabet = string.digits + string.ascii_letters.swapcase()
    id = "".join(secrets.choice(alphabet) for i in range(n_char))
    return id


def hash_str(s: str) -> str:
    from lamin_utils._base62 import encodebytes

    # as we're truncating at a short length, we choose md5 over sha512
    return encodebytes(hashlib.md5(s.encode()).digest())


def hash_id(input_id: str | None = None, *, n_char: int) -> str:
    if input_id is None:
        return base62(n_char=n_char)
    else:
        return hash_str(input_id)[:n_char]


def gene(input_id: str | None = None) -> str:
    """12 base62."""
    return hash_id(input_id, n_char=12)


def protein(input_id: str | None = None) -> str:
    """12 base62."""
    return hash_id(input_id, n_char=12)


def cellmarker(input_id: str | None = None) -> str:
    """12 base62."""
    return hash_id(input_id, n_char=12)


def ontology(input_id: str | None = None):
    """8 base62."""
    return hash_id(input_id, n_char=8)


def source(input_id: str | None = None):
    """8 base62."""
    return hash_id(input_id, n_char=8)

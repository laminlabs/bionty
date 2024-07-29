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
from typing import Optional

from lnschema_core.ids import base62


def hash_str(s: str) -> str:
    from lamin_utils._base62 import encodebytes

    # as we're truncating at a short length, we choose md5 over sha512
    return encodebytes(hashlib.md5(s.encode()).digest())


def hash_id(input_id: Optional[str] = None, *, n_char: int) -> str:
    if input_id is None:
        return base62(n_char=n_char)
    else:
        return hash_str(input_id)[:n_char]


def gene(input_id: Optional[str] = None) -> str:
    """12 base62."""
    return hash_id(input_id, n_char=12)


def protein(input_id: Optional[str] = None) -> str:
    """12 base62."""
    return hash_id(input_id, n_char=12)


def cellmarker(input_id: Optional[str] = None) -> str:
    """12 base62."""
    return hash_id(input_id, n_char=12)


def ontology(input_id: Optional[str] = None):
    """8 base62."""
    return hash_id(input_id, n_char=8)


def source(input_id: Optional[str] = None):
    """4 base62."""
    return hash_id(input_id, n_char=4)


# backward compat
organism = ontology
species = organism
publicsource = source

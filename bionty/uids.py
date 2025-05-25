"""UIDs.

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


def base62(n_char: int) -> str:
    """Random Base62 string."""
    alphabet = string.digits + string.ascii_letters.swapcase()
    id = "".join(secrets.choice(alphabet) for i in range(n_char))
    return id


def encode_base62(s: str) -> str:
    from lamin_utils._base62 import encodebytes

    return encodebytes(hashlib.md5(s.encode()).digest())


def hash_id(input_id: str | None = None, *, n_char: int) -> str:
    if input_id is None:
        return base62(n_char=n_char)
    else:
        return encode_base62(input_id)[:n_char]


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


def encode_uid(registry: type, kwargs: dict):
    """The type passed needs to be a subclass of BioRecord."""
    from lamindb.models import SQLRecord

    from . import ids

    if kwargs.get("uid") is not None:
        # if uid is passed, no encoding is needed
        return kwargs
    name = registry.__name__.lower()
    if hasattr(registry, "organism_id"):
        organism = kwargs.get("organism")
        if organism is None:
            if kwargs.get("organism_id") is not None:
                from .models import Organism

                organism = Organism.get(kwargs.get("organism_id")).name
        elif isinstance(organism, SQLRecord):
            organism = organism.name
    else:
        organism = ""

    if hasattr(registry, "_ontology_id_field"):
        ontology_id_field = registry._ontology_id_field
    else:
        ontology_id_field = "ontology_id"
    if hasattr(registry, "_name_field"):
        name_field = registry._name_field
    else:
        name_field = "name"

    str_to_encode = None
    if name == "source":
        str_to_encode = f"{kwargs.get('entity', '')}{kwargs.get('name', '')}{kwargs.get('organism', '')}{kwargs.get('version', '')}"
    elif name == "gene":  # gene has multiple id fields
        str_to_encode = kwargs.get(ontology_id_field)
        if str_to_encode is None or str_to_encode == "":
            str_to_encode = kwargs.get("stable_id")
        if str_to_encode is None or str_to_encode == "":
            str_to_encode = f"{kwargs.get(name_field)}{organism}"  # name + organism
        if str_to_encode is None or str_to_encode == "":
            raise AssertionError(
                f"must provide {ontology_id_field}, stable_id or {name_field}"
            )
    else:
        str_to_encode = kwargs.get(ontology_id_field)
        if str_to_encode is None or str_to_encode == "":
            str_to_encode = f"{kwargs.get(name_field)}{organism}"  # name + organism
        if str_to_encode is None or str_to_encode == "":
            raise AssertionError(f"must provide {ontology_id_field} or {name_field}")

    if str_to_encode is not None and len(str_to_encode) > 0:
        try:
            id_encoder = getattr(ids, name)
        except Exception:
            if ontology_id_field == "ontology_id":
                id_encoder = ids.ontology
            else:
                return kwargs
        kwargs["uid"] = id_encoder(str_to_encode)
    return kwargs


def encode_uid_for_hub(registry_name: str, registry_schema_json: dict, kwargs: dict):
    """Encode the uid for the hub.

    Note that `organism` record must be passed in kwargs instead of `organism_id`.
    """
    from . import ids

    if kwargs.get("uid") is not None:
        # if uid is passed, no encoding is needed
        return kwargs
    name = registry_name.lower()
    # here we need to pass the organism record, not organism_id
    organism = kwargs.get("organism", "")
    if organism:
        organism = organism.get("name", "")

    # default to ontology_id
    ontology_id_field = registry_schema_json.get("_ontology_id_field", "ontology_id")
    name_field = registry_schema_json.get("_name_field", "name")

    str_to_encode = None
    if name == "source":
        str_to_encode = f"{kwargs.get('entity', '')}{kwargs.get('name', '')}{kwargs.get('organism', '')}{kwargs.get('version', '')}"
    elif name == "gene":  # gene has multiple id fields
        str_to_encode = kwargs.get(ontology_id_field)
        if str_to_encode is None or str_to_encode == "":
            str_to_encode = kwargs.get("stable_id")
        if str_to_encode is None or str_to_encode == "":
            str_to_encode = f"{kwargs.get(name_field)}{organism}"  # name + organism
        if str_to_encode is None or str_to_encode == "":
            raise AssertionError(
                f"must provide {ontology_id_field}, stable_id or {name_field}"
            )
    else:
        str_to_encode = kwargs.get(ontology_id_field)
        if str_to_encode is None or str_to_encode == "":
            str_to_encode = f"{kwargs.get(name_field)}{organism}"  # name + organism
        if str_to_encode is None or str_to_encode == "":
            raise AssertionError(f"must provide {ontology_id_field} or {name_field}")

    if str_to_encode is not None and len(str_to_encode) > 0:
        try:
            id_encoder = getattr(ids, name)
        except Exception:
            if ontology_id_field == "ontology_id":
                id_encoder = ids.ontology
            else:
                return kwargs
        kwargs["uid"] = id_encoder(str_to_encode)
    return kwargs

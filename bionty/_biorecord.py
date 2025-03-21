from __future__ import annotations

from typing import TYPE_CHECKING

from . import ids

if TYPE_CHECKING:
    from types import ModuleType

    from .models import BioRecord


def encode_uid(registry: type[BioRecord], kwargs: dict):
    from lamindb.models import Record

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
        elif isinstance(organism, Record):
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


def lookup2kwargs(record: BioRecord, *args, **kwargs) -> dict:
    """Pass bionty search/lookup results."""
    from ._organism import create_or_get_organism_record
    from ._source import get_source_record

    arg = args[0]
    if isinstance(arg, tuple):
        bionty_kwargs = arg._asdict()  # type:ignore
    else:
        bionty_kwargs = arg[0]._asdict()

    if len(bionty_kwargs) > 0:
        # add organism and source
        organism_record = create_or_get_organism_record(
            registry=record.__class__, organism=kwargs.get("organism")
        )
        if organism_record is not None:
            bionty_kwargs["organism"] = organism_record
        bionty_kwargs["source"] = get_source_record(
            registry=record.__class__,
            organism=organism_record,
            source=kwargs.get("source"),
        )

        model_field_names = {i.name for i in record._meta.fields}
        model_field_names.add("parents")
        bionty_kwargs = {
            k: v for k, v in bionty_kwargs.items() if k in model_field_names
        }
    return encode_uid(registry=record.__class__, kwargs=bionty_kwargs)


def list_biorecord_models(schema_module: ModuleType):
    """List all BioRecord models in a given schema module."""
    import inspect

    import lamindb as ln  # needed here

    from .models import BioRecord

    return [
        attr
        for attr in dir(schema_module.models)
        if inspect.isclass(getattr(schema_module.models, attr))
        and issubclass(getattr(schema_module.models, attr), BioRecord)
    ]

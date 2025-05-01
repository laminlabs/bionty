from __future__ import annotations

from typing import TYPE_CHECKING

from .uids import encode_uid

if TYPE_CHECKING:
    from types import ModuleType

    from .models import BioRecord


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

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from lamin_utils import logger
from lamindb.models import Record

import bionty.base as bt_base

from . import ids

if TYPE_CHECKING:
    from types import ModuleType


class OrganismNotSet(SystemExit):
    """The `organism` parameter was not passed or is not globally set."""

    pass


def create_or_get_organism_record(
    organism: str | Record | None, registry: type[Record], field: str | None = None
) -> Record | None:
    # return None if an Record doesn't have organism field
    organism_record = None
    if hasattr(registry, "organism_id"):
        # using global setting of organism
        from .core._settings import settings

        if organism is None and settings.organism is not None:
            logger.debug(f"using global setting organism = {settings.organism.name}")
            return settings.organism

        if isinstance(organism, Record):
            organism_record = organism
        elif isinstance(organism, str):
            from .models import Organism

            try:
                # existing organism record
                organism_record = Organism.objects.get(name=organism)
            except ObjectDoesNotExist:
                try:
                    # create a organism record from bionty reference
                    organism_record = Organism.from_source(name=organism)
                    if organism_record is None:
                        raise ValueError(
                            f"Organism {organism} can't be created from the bionty reference, check your spelling or create it manually."
                        )
                    # link the organism record to the default bionty source
                    organism_record.source = get_source_record(
                        bt_base.Organism(), Organism
                    )  # type:ignore
                    organism_record.save()  # type:ignore
                except KeyError:
                    # no such organism is found in bionty reference
                    organism_record = None

        if organism_record is None:
            if hasattr(registry, "_ontology_id_field") and field in {
                registry._ontology_id_field,
                "uid",
            }:
                return None
            raise OrganismNotSet(
                f"{registry.__name__} requires to specify a organism name via `organism=` or `bionty.settings.organism=`!"
            )

    return organism_record


def get_source_record(
    public_ontology: bt_base.PublicOntology, registry: type[Record]
) -> Record:
    from .models import Source

    if public_ontology.__class__.__name__ == "StaticReference":
        entity_name = registry.__get_name_with_module__()
    else:
        entity_name = (
            f"{registry.__get_module_name__()}.{public_ontology.__class__.__name__}"
        )
    kwargs = {
        "entity": entity_name,
        "organism": public_ontology.organism,
        "name": public_ontology.source,
        "version": public_ontology.version,
    }

    source_record = Source.objects.get(**kwargs)
    return source_record


def list_biorecord_models(schema_module: ModuleType):
    """List all BioRecord models in a given schema module."""
    import inspect

    from .models import BioRecord

    return [
        attr
        for attr in dir(schema_module.models)
        if inspect.isclass(getattr(schema_module.models, attr))
        and issubclass(getattr(schema_module.models, attr), BioRecord)
    ]


def encode_uid(registry: type[Record], kwargs: dict):
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
        str_to_encode = f'{kwargs.get("entity", "")}{kwargs.get("name", "")}{kwargs.get("organism", "")}{kwargs.get("version", "")}'
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


def lookup2kwargs(record: Record, *args, **kwargs) -> dict:
    """Pass bionty search/lookup results."""
    arg = args[0]
    if isinstance(arg, tuple):
        bionty_kwargs = arg._asdict()  # type:ignore
    else:
        bionty_kwargs = arg[0]._asdict()

    if len(bionty_kwargs) > 0:
        import bionty.base as bt_base

        # add organism and source
        organism_record = create_or_get_organism_record(
            registry=record.__class__, organism=kwargs.get("organism")
        )
        if organism_record is not None:
            bionty_kwargs["organism"] = organism_record
        public_ontology = getattr(bt_base, record.__class__.__name__)(
            organism=organism_record.name if organism_record is not None else None
        )
        bionty_kwargs["source"] = get_source_record(public_ontology, record.__class__)

        model_field_names = {i.name for i in record._meta.fields}
        model_field_names.add("parents")
        bionty_kwargs = {
            k: v for k, v in bionty_kwargs.items() if k in model_field_names
        }
    return encode_uid(registry=record.__class__, kwargs=bionty_kwargs)


# backward compat
create_or_get_species_record = create_or_get_organism_record

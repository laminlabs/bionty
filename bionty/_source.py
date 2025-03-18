from lamindb.models import Record

from ._organism import create_or_get_organism_record


def get_source_record(
    registry: type[Record],
    organism: str | Record | None = None,
    source: Record | None = None,
) -> Record:
    """Get a Source record for a given BioRecord model."""
    from .models import Source

    if source is not None:
        return source

    organism_record = create_or_get_organism_record(organism, registry)

    entity_name = registry.__get_name_with_module__()
    filter_kwargs = {"entity": entity_name}
    if isinstance(organism_record, Record):
        filter_kwargs["organism"] = organism_record.name

    sources = Source.filter(**filter_kwargs).all()
    if len(sources) == 0:
        raise ValueError(f"No source record found for {entity_name}")
    if len(sources) == 1:
        return sources.one()

    current_sources = sources.filter(currently_used=True).all()
    if len(current_sources) == 1:
        return current_sources.first()
    elif len(current_sources) > 1:
        if organism is None:
            # for Organism, in most cases we load from the vertebrates source because ncbitaxon is too big
            if entity_name == "bionty.Organism":
                current_sources_vertebrates = current_sources.filter(
                    organism="vertebrates"
                ).all()
                if len(current_sources_vertebrates) > 0:
                    return current_sources_vertebrates.first()
            # return source with organism="all"
            current_sources_all = current_sources.filter(organism="all").all()
            if len(current_sources_all) > 0:
                return current_sources_all.first()
        return current_sources.first()
    else:  # len(current_sources) == 0
        sources_all = sources.filter(organism="all").all()
        if len(sources_all) > 0:
            # return source with organism="all"
            return sources_all.first()
        return sources.first()


# def get_source_record_from_public(
#     public_ontology: bt_base.PublicOntology, registry: type[Record]
# ) -> Record:
#     """Get a Source record from a public ontology object."""
#     from .models import Source

#     entity_name = registry.__get_name_with_module__()
#     kwargs = {
#         "entity": entity_name,
#         "organism": public_ontology.organism,
#         "name": public_ontology.source,
#         "version": public_ontology.version,
#     }

#     return Source.objects.get(**kwargs)

doc_entites = """\
organism: `name` of `Organism` entity.
        source: The key of the source in the local.yml versions file.
                  Get all available databases with `.display_available_sources()`.
        version: The version of the ontology. Typically a date or an actual version.
                  Get available versions with `.display_available_sources()`.
"""
organism_removed_tmp = "\n".join(doc_entites.split("\n")[1:]).split("\n")
organism_removed_tmp[0] = organism_removed_tmp[0].removeprefix("        ")
organism_removed = "\n".join(organism_removed_tmp)


doc_curate = """\
df: DataFrame with a column of identifiers
        column: If `column` is `None`, checks the existing index for compliance with
                  the default identifier.
                If `column` denotes an entity identifier, tries to map that identifier
                  to the default identifier.
        field: The type of identifier for mapping.
"""

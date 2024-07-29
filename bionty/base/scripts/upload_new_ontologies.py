def _upload_ontology_artifacts(instance: str, lamin_user: str, lamin_api_key: str):
    import bionty_base as bt
    import lamindb as ln
    from bionty_base._public_ontology import encode_filenames
    from bionty_base._settings import settings

    ln.setup.login(lamin_user, key=lamin_api_key)
    ln.setup.load(instance)

    queryset = ln.File.select().all()

    files = []
    for entity, row in bt.display_available_sources().iterrows():
        parquet_filename, ontology_filename = encode_filenames(
            organism=row.organism, source=row.source, version=row.version, entity=entity
        )
        if entity == "Organism" or row.url.startswith("s3://bionty-assets"):
            continue

        if not queryset.filter(key=parquet_filename).exists():
            local_parquet_filename = settings.dynamicdir / parquet_filename
            if not local_parquet_filename.exists():
                try:
                    getattr(bt, entity)(
                        organism=row.organism, source=row.source, version=row.version
                    )
                except Exception:  # for renamed classes
                    continue
            file = ln.File(local_parquet_filename, key=parquet_filename)
            files.append(file)

        if not queryset.filter(key=ontology_filename).exists():
            local_ontology_filename = settings.dynamicdir / ontology_filename
            if not local_ontology_filename.exists():
                getattr(bt, entity)(
                    organism=row.organism, source=row.source, version=row.version
                ).to_pronto()
            file = ln.File(local_ontology_filename, key=ontology_filename)
            files.append(file)
    if len(files) > 0:
        ln.save()

    ln.setup.close()

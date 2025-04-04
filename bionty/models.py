from __future__ import annotations

import functools
from typing import overload

import numpy as np
import pandas as pd
from django.db import models
from django.db.models import CASCADE, PROTECT
from lamin_utils import logger
from lamindb.base.fields import (
    BigIntegerField,
    BooleanField,
    CharField,
    ForeignKey,
    TextField,
)
from lamindb.errors import DoesNotExist, InvalidArgument
from lamindb.models import (
    Artifact,
    BasicRecord,
    CanCurate,
    Feature,
    HasParents,
    LinkORM,
    Record,
    Schema,
    TracksRun,
    TracksUpdates,
)

import bionty.base as bt_base
from bionty.base.dev._doc_util import _doc_params

from . import ids
from ._biorecord import encode_uid, lookup2kwargs
from ._shared_docstrings import doc_from_source
from .base import PublicOntology
from .base._public_ontology import InvalidParamError


class StaticReference(PublicOntology):
    def __init__(self, source_record: Source) -> None:
        self._source_record = source_record
        super().__init__(
            source=source_record.name,
            version=source_record.version,
            organism=source_record.organism,
        )

    def _load_df(self) -> pd.DataFrame:
        if self._source_record.dataframe_artifact_id:
            return self._source_record.dataframe_artifact.load(is_run_input=False)
        else:
            return pd.DataFrame()


def pass_to_super(cls_method):
    """Decorator to pass all non-None parameters to the superclass method."""

    @functools.wraps(cls_method)
    def wrapper(cls, *args, **kwargs):
        # Get all non-None kwargs
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        # Call superclass method with filtered kwargs
        return getattr(super(cls, cls), cls_method.__name__)(*args, **filtered_kwargs)

    return wrapper


class Source(Record, TracksRun, TracksUpdates):
    """Versions of ontology sources.

    .. warning::

        Do not modify the records unless you know what you are doing!
    """

    class Meta(Record.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("entity", "name", "organism", "version"),)

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.source)
    """A universal id (base62-encoded hash of defining fields)."""
    entity: str = CharField(max_length=256, db_index=True)
    """Entity class name with schema, e.g. bionty.CellType."""
    organism: str = CharField(max_length=64, db_index=True)
    """Organism name, use 'all' if unknown or none applied."""
    name: str = CharField(max_length=64, db_index=True)
    """Source name, short form, CURIE prefix for ontologies."""
    version: str = CharField(max_length=64, db_index=True)
    """Version of the source."""
    in_db: bool = BooleanField(default=False, db_index=True)
    """Whether this ontology has be added to the database."""
    currently_used: bool = BooleanField(default=False, db_index=True)
    """Whether this record is currently used."""
    description: str | None = TextField(blank=True, db_index=True)
    """Source full name, long form."""
    url: str | None = TextField(null=True, default=None)
    """URL of the source file."""
    md5: str | None = TextField(null=True, default=None)
    """Hash md5 of the source file."""
    source_website: str | None = TextField(null=True, default=None)
    """Website of the source."""
    dataframe_artifact: Artifact = ForeignKey(
        Artifact, PROTECT, null=True, default=None, related_name="_source_dataframe_of"
    )
    """Dataframe artifact that corresponds to this source."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, related_name="_source_artifact_of"
    )
    """Additional files that correspond to this source."""

    @overload
    def __init__(
        self,
        entity: str,
        organism: str,
        name: str,
        version: str,
        currently_used: bool,
        description: str | None,
        url: str | None,
        md5: str | None,
        source_website: str | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        kwargs = encode_uid(registry=Source, kwargs=kwargs)
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs) -> Source:
        """Save the source record."""
        update = self.currently_used and self.pk
        super().save(*args, **kwargs)
        # when update currently_used, set all other records of the same source as not currently used
        if update:
            Source.filter(
                entity=self.entity, organism=self.organism, name=self.name
            ).exclude(id=self.id).update(currently_used=False)
        return self


class BioRecord(Record, HasParents, CanCurate):
    """Base Record of bionty.

    BioRecord inherits all methods from :class:`~lamindb.models.Record` and provides additional methods
    including :meth:`~bionty.core.BioRecord.public` and :meth:`~bionty.core.BioRecord.from_source`.

    Notes:
        For more info, see tutorials:

        - :doc:`docs:bionty`
        - :doc:`docs:bio-registries`
    """

    class Meta:
        abstract = True

    source = ForeignKey(Source, PROTECT, null=True, related_name="+")
    """:class:`~bionty.Source` this record associates with."""

    def __init__(self, *args, **kwargs):
        # DB-facing constructor
        if len(args) == len(self._meta.concrete_fields):
            super().__init__(*args, **kwargs)
            return None

        # passing lookup result from bionty, which is a Tuple or List
        if (
            args
            and len(args) == 1
            and isinstance(args[0], tuple | list)
            and len(args[0]) > 0
        ):
            if isinstance(args[0], list) and len(args[0]) > 1:
                logger.warning(
                    "multiple lookup/search results were passed. Only returning record from the first entry."
                )
            result = lookup2kwargs(self, *args, **kwargs)  # type:ignore
            # exclude "parents" from query arguments
            query_kwargs = {k: v for k, v in result.items() if k != "parents"}
            existing_record = self.__class__.filter(**query_kwargs).one_or_none()
            if existing_record is not None:
                from lamindb._record import init_self_from_db

                init_self_from_db(self, existing_record)
                return None
            else:
                kwargs = result  # result already has encoded id
                args = ()

        # raise error if no organism is passed
        if hasattr(self.__class__, "organism_id"):
            if kwargs.get("organism") is None and kwargs.get("organism_id") is None:
                from .core._settings import settings

                if settings.organism is not None:
                    kwargs["organism"] = settings.organism
                else:
                    raise RuntimeError("please pass a organism!")
            elif kwargs.get("organism") is not None:
                if not isinstance(kwargs.get("organism"), Organism):
                    raise TypeError("organism must be a `bionty.Organism` record.")

        kwargs = encode_uid(registry=self.__class__, kwargs=kwargs)

        # now continue with the user-facing constructor
        # set the direct parents as a private attribute
        # this is a list of strings that store the ontology id
        if "parents" in kwargs:
            parents = kwargs.pop("parents")
            # this checks if we receive a np.ndarray from pandas
            if isinstance(parents, list | np.ndarray) and len(parents) > 0:
                if not isinstance(parents[0], str):
                    raise ValueError(
                        "Invalid parents kwarg passed. Provide a list of ontology ids."
                    )
                self._parents = parents

        super().__init__(*args, **kwargs)

    @classmethod
    def import_source(
        cls,
        source: Source | None = None,
        update_records: bool = False,
        *,
        organism: str | Record | None = None,
        ignore_conflicts: bool = True,
    ):
        """Bulk save records from a Bionty ontology.

        Use this method to initialize your registry with public ontology.

        Args:
            source: Source record to import records from.
            update_records: If True, update existing records with the new source.
                - If a record has the same metadata in the new source, link the record to the new source.
                - If a record has no artifacts associated, update it's metadata and link to the new source.
                - If a record associated artifacts, but different name in the new source, create a new record with the new source.
            organism: Organism name or record.
                Required for entities with a required organism foreign key when no source is passed.
            ignore_conflicts: Whether to ignore conflicts during bulk record creation.

        Example::

            import bionty as bt

            # import all records from a default source
            default_sources = bt.Source.filter(entity="bionty.CellType", currently_used=True).df()
            bt.CellType.import_source()

            # import all records from a specific source
            source = bt.Source.get(entity="bionty.CellType", source="cl", version="2022-08-16")
            bt.CellType.import_source(source)
            bt.CellType.df()  # all records from the source are now in the registry

            # update existing records with a new source (version update)
            source = bt.Source.get(entity="bionty.CellType", source="cl", version="2024-08-16")
            bt.CellType.import_source(source, update_records=True)
        """
        if update_records:
            from .core._source import update_records_to_source

            update_records_to_source(cls, source)
        else:
            from .core._add_ontology import add_ontology_from_df

            add_ontology_from_df(
                registry=cls,
                organism=organism,
                source=source,
                ignore_conflicts=ignore_conflicts,
            )

    @classmethod
    def add_source(
        cls,
        source: Source,
        df: pd.DataFrame | None = None,
    ) -> Source:
        """Link a source record to the entity with a reference DataFrame.

        Args:
            source: Source record to add (this can be from another entity).
            df: DataFrame to add to the source.dataframe_artifact.

        Returns:
            A Source record with this entity.

        Example::

            import bionty as bt

            internal_source = bt.Source(
                entity="bionty.Gene",
                name="internal",
                version="0.0.1",
                organism="rabbit",
                description="internal gene reference",
            ).save()

            source_df = pd.DataFrame(
                {
                    "ensembl_gene_id": ["ENSOCUG00000017195"],
                    "symbol": ["SEL1L3"],
                    "description": ["SEL1L family member 3"],
                }
            )

            bt.Gene.add_source(internal_source, df=df)
        """
        import lamindb as ln

        from ._organism import is_organism_required

        unique_kwargs = {
            "entity": cls.__get_name_with_module__(),
            "name": source.name,
            "version": source.version,
            "organism": source.organism,
        }
        add_kwargs = {
            "currently_used": source.currently_used,
            "description": source.description,
            "url": source.url,
            "source_website": source.source_website,
            "dataframe_artifact_id": source.dataframe_artifact_id,
        }
        # make sure organism is registered
        if is_organism_required(cls):
            Organism.from_source(name=source.organism).save()
        new_source = Source.filter(**unique_kwargs).one_or_none()
        if new_source is None:
            new_source = Source(**unique_kwargs, **add_kwargs).save()
        if new_source.dataframe_artifact_id is not None:
            return new_source

        # register the dataframe artifact
        key = f"df__{unique_kwargs.get('organism')}__{unique_kwargs.get('name')}__{unique_kwargs.get('version')}__{unique_kwargs.get('entity')}.parquet"
        if isinstance(df, pd.DataFrame):
            df_artifact = ln.Artifact.from_df(
                df, key=key, _branch_code=0, run=False
            ).save()
        elif source.url and source.url.startswith("s3://bionty-assets/"):
            df_artifact = ln.Artifact(new_source.url, _branch_code=0, run=False).save()
        else:
            try:
                df = getattr(bt_base, source.entity)(
                    organism=source.organism,
                    source=source.name,
                    version=source.version,
                ).df()
            except Exception as e:
                logger.error(
                    "please first register a DataFrame artifact and link it to source!\n"
                    "    → artifact = ln.Artifact.from_df(df, _branch_code=0, run=False).save()\n"
                    "    → source.dataframe_artifact = artifact\n"
                    "    → source.save()"
                )
                raise ValueError from e
            df_artifact = ln.Artifact.from_df(
                df, key=key, _branch_code=0, run=False
            ).save()

        new_source.dataframe_artifact = df_artifact
        new_source.save()
        logger.important("source added!")

        return new_source

    @classmethod
    def public(
        cls,
        organism: str | Record | None = None,
        source: Source | None = None,
    ) -> PublicOntology | StaticReference:
        """The corresponding :class:`docs:bionty.base.PublicOntology` object.

        Note that the source is auto-configured and tracked via :class:`docs:bionty.Source`.

        See Also:
            :doc:`docs:public-ontologies`

        Example::

            import bionty as bt

            # default source
            celltype_pub = bt.CellType.public()
            celltype_pub
            #> PublicOntology
            #> Entity: CellType
            #> Organism: all
            #> Source: cl, 2023-04-20
            #> #terms: 2698

            # default source of a organism
            gene_pub = bt.Gene.public(organism="mouse")
            gene_pub
            #> PublicOntology
            #> Entity: Gene
            #> Organism: mouse
            #> Source: ensembl, release-112
            #> #terms: 57510
        """
        if isinstance(organism, Organism):
            organism = organism.name

        if source is not None:
            organism = source.organism
            source_name = source.name
            version = source.version
        else:
            from ._source import get_source_record
            from .core._settings import settings

            if hasattr(cls, "organism_id"):
                if organism is None and settings.organism is not None:
                    organism = settings.organism.name
            source_name = None
            version = None
            source = get_source_record(cls, organism=organism)
            if source is not None:
                source_name = source.name
                version = source.version

        try:
            return getattr(bt_base, cls.__name__)(
                organism=organism, source=source_name, version=version
            )
        except InvalidParamError as e:
            raise ValueError(str(e)) from None
        except (AttributeError, ValueError):
            if source is None:
                kwargs = {
                    "entity": cls.__get_name_with_module__(),
                    "currently_used": True,
                }
                if organism is not None:
                    if isinstance(organism, Record):
                        kwargs["organism"] = organism.name
                    else:
                        kwargs["organism"] = organism
                source = Source.filter(**kwargs).first()
            return StaticReference(source)

    @classmethod
    def from_source(
        cls, *, mute: bool = False, **kwargs
    ) -> BioRecord | list[BioRecord] | None:
        """Create a record or records from source based on a single field value.

        Notes:
            For more info, see tutorial :doc:`docs:bionty`

            Bulk create records via :meth:`.from_values`.

        Example::

            import bionty as bt

            # Create a record by passing a field value:
            record = bt.Gene.from_source(symbol="TCF7", organism="human")

            # Create a record from non-default source:
            source = bt.Source.get(entity="CellType", source="cl", version="2022-08-16")
            record = bt.CellType.from_source(name="T cell", source=source)

        """
        # non-relationship kwargs
        kv = {
            k: v
            for k, v in kwargs.items()
            if k not in [i.name for i in cls._meta.fields if i.is_relation]
        }
        if len(kv) > 1:
            raise InvalidArgument(
                "Only one field can be passed to generate records from source"
            )
        elif len(kv) == 0:
            raise InvalidArgument("No field passed to generate records from source")
        else:
            k = next(iter(kv))
            v = kwargs.pop(k)
            results = cls.from_values([v], field=getattr(cls, k), mute=mute, **kwargs)
            if len(results) == 1:
                return results[0]
            elif len(results) == 0:
                raise DoesNotExist(
                    "No record found in source for the given field value"
                )
            else:
                return results

    def save(self, *args, **kwargs) -> BioRecord:
        """Save the record and its parents recursively.

        Example::

            import bionty as bt

            record = bt.CellType.from_source(name="T cell")
            record.save()
        """
        super().save(*args, **kwargs)
        # saving records of parents
        if hasattr(self, "_parents"):
            import lamindb as ln

            # here parents is still a list of ontology ids
            parents = self._parents
            # bulk create parent records
            parents_records = self.from_values(
                parents, self.__class__.ontology_id, source=self.source
            )
            ln.save(parents_records)
            self.parents.set(parents_records)

        return self


class Organism(BioRecord, TracksRun, TracksUpdates):
    """Organism - `NCBI Taxonomy <https://www.ncbi.nlm.nih.gov/taxonomy/>`__, `Ensembl Organism <https://useast.ensembl.org/info/about/species.html>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:organism`.


    Example::

        import bionty as bt

        record = bt.Organism.from_source(name="rabbit")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=64, db_index=True, default=None, unique=True)
    """Name of a organism, required field."""
    ontology_id: str | None = CharField(
        max_length=32, unique=True, db_index=True, null=True, default=None
    )
    """NCBI Taxon ID."""
    scientific_name: str | None = CharField(
        max_length=64, db_index=True, unique=True, null=True, default=None
    )
    """Scientific name of a organism."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this organism."""
    description: str | None = TextField(null=True, default=None)
    """Description of the organism."""
    parents: Organism = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent organism records."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, through="ArtifactOrganism", related_name="organisms"
    )
    """Artifacts linked to the organism."""

    @overload
    def __init__(
        self,
        name: str,
        taxon_id: str | None,
        scientific_name: str | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        scientific_name: str | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> Organism | list[Organism] | None:
        """Create an Organism record from source based on a single identifying field.

        Args:
            name: Common name of the organism (e.g. "human", "mouse", "zebrafish")
            ontology_id: NCBI Taxon ID (e.g. "9606")
            scientific_name: Scientific name (e.g. "Homo sapiens", "Mus musculus")
            {doc_from_source}

        Returns:
            A single Organism record, list of Organism records, or None if not found

        Example::

            import bionty as bt

            record = bt.Organism.from_source(name="human")
            record = bt.Organism.from_source(ontology_id="NCBITaxon:9606")
        """
        pass


class Gene(BioRecord, TracksRun, TracksUpdates):
    """Genes - `Ensembl <https://ensembl.org/>`__, `NCBI Gene <https://www.ncbi.nlm.nih.gov/gene/>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:gene`.

        Bulk create Gene records via `.from_values()`.
        Map legacy ensembl IDs to current ensembl IDs using :meth:`bionty.base.Gene.map_legacy_ids`.

        We discourage validating gene symbols and to work with unique identifiers such as ENSEMBL IDs instead.
        For more details, see :doc:`docs:faq/symbol-mapping`.

    Example::

        import bionty as bt

        record = bt.Gene.from_source(ensembl_gene_id="ENSG00000081059")
        record = bt.Gene.from_source(symbol="TCF7", organism="human")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False

    _name_field: str = "symbol"
    _ontology_id_field: str = "ensembl_gene_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=12, default=ids.gene)
    """A universal id (base62-encoded hash of defining fields)."""
    symbol: str | None = CharField(
        max_length=64, db_index=True, null=True, default=None
    )
    """A unique short form of gene name."""
    stable_id: str | None = CharField(
        max_length=64, db_index=True, null=True, default=None, unique=True
    )
    """Stable ID of a gene that doesn't have ensembl_gene_id, e.g. a yeast gene."""
    ensembl_gene_id: str | None = CharField(
        max_length=64, db_index=True, null=True, default=None, unique=True
    )
    """Ensembl gene stable ID, in the form ENS[organism prefix][feature type prefix][a unique eleven digit number]."""
    ncbi_gene_ids: str | None = TextField(null=True, default=None)
    """Bar-separated (|) NCBI Gene IDs that correspond to this Ensembl Gene ID.
    NCBI Gene ID, also known as Entrez Gene ID, in the form of numeric string, 1 to 9 digits.
    """
    biotype: str | None = CharField(
        max_length=64, db_index=True, null=True, default=None
    )
    """Type of the gene."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this gene."""
    description: str | None = TextField(null=True, default=None)
    """Description of the gene."""
    organism: Organism = ForeignKey(
        Organism, PROTECT, default=None, related_name="genes"
    )
    """:class:`~bionty.Organism` this gene associates with."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, through="ArtifactGene", related_name="genes"
    )
    """Artifacts linked to the gene."""
    schemas: Schema = models.ManyToManyField(
        Schema, through="SchemaGene", related_name="genes"
    )
    """Featuresets linked to this gene."""

    @overload
    def __init__(
        self,
        symbol: str | None,
        stable_id: str | None,
        ensembl_gene_id: str | None,
        ncbi_gene_ids: str | None,
        biotype: str | None,
        description: str | None,
        synonyms: str | None,
        organism: Organism | None,
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        symbol: str | None = None,
        ensembl_gene_id: str | None = None,
        stable_id: str | None = None,
        organism: str | Organism = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> Gene | list[Gene] | None:
        """Create a Gene record from source based on a single identifying field.

        Args:
            symbol: Gene symbol (e.g. "TCF7")
            ensembl_gene_id: Ensembl gene ID (e.g. "ENSG00000081059")
            stable_id: Stable ID for genes without Ensembl IDs (e.g. yeast genes)
            organism: Organism name or Organism record
            {doc_from_source}

        Returns:
            A single Gene record, list of Gene records, or None if not found

        Example::

            import bionty as bt

            record = bt.Gene.from_source(symbol="TCF7", organism="human")
            record = bt.Gene.from_source(ensembl_gene_id="ENSG00000081059")
            record = bt.Gene.from_source(stable_id="YAL001C", organism="yeast")
        """
        pass


class Protein(BioRecord, TracksRun, TracksUpdates):
    """Proteins - `Uniprot <https://www.uniprot.org/>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:protein`.

        Bulk create records via :meth:`.from_values`.

    Example::

        import bionty as bt

        record = bt.Protein.from_source(name="Synaptotagmin-15B", organism="human")
        record = bt.Protein.from_source(gene_symbol="SYT15B", organism="human")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False

    _name_field: str = "name"
    _ontology_id_field: str = "uniprotkb_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=12, default=ids.protein)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str | None = CharField(max_length=256, db_index=True, null=True, default=None)
    """Unique name of a protein."""
    uniprotkb_id: str | None = CharField(
        max_length=10, db_index=True, null=True, default=None, unique=True
    )
    """UniProt protein ID, 6 alphanumeric characters, possibly suffixed by 4 more."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this protein."""
    description: str | None = TextField(null=True, default=None)
    """Description of the protein."""
    length: int | None = BigIntegerField(db_index=True, null=True)
    """Length of the protein sequence."""
    gene_symbol: str | None = CharField(
        max_length=256, db_index=True, null=True, default=None
    )
    """The primary gene symbol corresponds to this protein."""
    ensembl_gene_ids: str | None = TextField(null=True, default=None)
    """Bar-separated (|) Ensembl Gene IDs that correspond to this protein."""
    organism: Organism = ForeignKey(
        Organism, PROTECT, default=None, related_name="proteins"
    )
    """:class:`~bionty.Organism` this protein associates with."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, through="ArtifactProtein", related_name="proteins"
    )
    """Artifacts linked to the protein."""
    schemas: Schema = models.ManyToManyField(
        Schema, through="SchemaProtein", related_name="proteins"
    )
    """Featuresets linked to this protein."""

    @overload
    def __init__(
        self,
        name: str | None,
        uniprotkb_id: str | None,
        synonyms: str | None,
        length: int | None,
        gene_symbol: str | None,
        ensembl_gene_ids: str | None,
        organism: Organism | None,
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        uniprotkb_id: str | None = None,
        gene_symbol: str | None = None,
        organism: str | Organism | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> Protein | list[Protein] | None:
        """Create a Protein record from source based on a single identifying field.

        Args:
            name: Protein name (e.g. "Synaptotagmin-15B")
            uniprotkb_id: UniProt protein ID (e.g. "Q8N6N3")
            gene_symbol: Gene symbol (e.g. "SYT15B")
            organism: Organism name or Organism record
            {doc_from_source}

        Returns:
            A single Protein record, list of Protein records, or None if not found

        Example::

            import bionty as bt

            record = bt.Protein.from_source(name="Synaptotagmin-15B", organism="human")
            record = bt.Protein.from_source(uniprotkb_id="Q8N6N3")
            record = bt.Protein.from_source(gene_symbol="SYT15B", organism="human")
        """
        pass


class CellMarker(BioRecord, TracksRun, TracksUpdates):
    """Cell markers - `CellMarker <http://xteam.xbio.top/CellMarker>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:cell_marker`.

        Bulk create CellMarker records via :meth:`.from_values`.

    Example::

        import bionty as bt

        record = bt.CellMarker.from_source(name="PD1", organism="human")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "organism"),)

    _name_field: str = "name"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=12, default=ids.cellmarker)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=64, db_index=True)
    """Unique name of the cell marker."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this cell marker."""
    description: str | None = TextField(null=True, default=None)
    """Description of the cell marker."""
    gene_symbol: str | None = CharField(
        max_length=64, db_index=True, null=True, default=None
    )
    """Gene symbol that corresponds to this cell marker."""
    ncbi_gene_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """NCBI gene id that corresponds to this cell marker."""
    uniprotkb_id: str | None = CharField(
        max_length=10, db_index=True, null=True, default=None
    )
    """Uniprotkb id that corresponds to this cell marker."""
    organism: Organism = ForeignKey(
        Organism, PROTECT, default=None, related_name="cell_markers"
    )
    """:class:`~bionty.Organism` this cell marker associates with."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact,
        through="ArtifactCellMarker",
        related_name="cell_markers",
    )
    """Artifacts linked to the cell marker."""
    schemas: Schema = models.ManyToManyField(
        Schema, through="SchemaCellMarker", related_name="cell_markers"
    )
    """Featuresets linked to this cell marker."""

    @overload
    def __init__(
        self,
        name: str,
        synonyms: str | None,
        gene_symbol: str | None,
        ncbi_gene_id: str | None,
        uniprotkb_id: str | None,
        organism: Organism | None,
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        gene_symbol: str | None = None,
        ncbi_gene_id: str | None = None,
        uniprotkb_id: str | None = None,
        organism: str | Organism | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> CellMarker | list[CellMarker] | None:
        """Create a CellMarker record from source based on a single identifying field.

        Args:
            name: Cell marker name (e.g. "PD1", "CD19")
            gene_symbol: Gene symbol (e.g. "PDCD1", "CD19")
            ncbi_gene_id: NCBI gene ID that corresponds to this cell marker
            uniprotkb_id: UniProt ID that corresponds to this cell marker
            organism: Organism name or Organism record
            {doc_from_source}

        Returns:
            A single CellMarker record, list of CellMarker records, or None if not found

        Example::

            import bionty as bt

            record = bt.CellMarker.from_source(name="PD1", organism="human")
            record = bt.CellMarker.from_source(gene_symbol="PDCD1", organism="human")
            record = bt.CellMarker.from_source(name="CD19", organism="mouse")
        """
        pass


class Tissue(BioRecord, TracksRun, TracksUpdates):
    """Tissues - `Uberon <http://obophenotype.github.io/uberon/>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` :doc:`docs:tissue`.

        Bulk create Tissue records via :meth:`.from_values`.

    Example::

        import bionty as bt

        record = bt.Tissue.from_source(name="brain")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=256, db_index=True)
    """Name of the tissue."""
    ontology_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """Ontology ID of the tissue."""
    abbr: str | None = CharField(
        max_length=32, db_index=True, unique=True, null=True, default=None
    )
    """A unique abbreviation of tissue."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this tissue."""
    description: str | None = TextField(null=True, default=None)
    """Description of the tissue."""
    parents: Tissue = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent tissues records."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, through="ArtifactTissue", related_name="tissues"
    )
    """Artifacts linked to the tissue."""

    @overload
    def __init__(
        self,
        name: str,
        ontology_id: str | None,
        abbr: str | None,
        synonyms: str | None,
        description: str | None,
        parents: list[Tissue],
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        organism: str | Organism | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> Tissue | list[Tissue] | None:
        """Create a Tissue record from source based on a single identifying field.

        Args:
            name: Tissue name (e.g. "nose")
            ontology_id: Tissue ontology ID (e.g. "UBERON:0000004")
            organism: Organism name or Organism record
            {doc_from_source}

        Returns:
            A single Tissue record, list of Tissue records, or None if not found

        Example::

            import bionty as bt

            record = bt.Tissue.from_source(name="nose")
            record = bt.Tissue.from_source(ontology_id="UBERON:0000004")
        """
        pass


class CellType(BioRecord, TracksRun, TracksUpdates):
    """Cell types - `Cell Ontology <https://obophenotype.github.io/cell-ontology/>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:cell_type`.

        Bulk create CellType records via :meth:`.from_values`.

    Example::

        import bionty as bt

        record = bt.CellType.from_source(name="T cell")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=256, db_index=True)
    """Name of the cell type."""
    ontology_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """Ontology ID of the cell type."""
    abbr: str | None = CharField(
        max_length=32, db_index=True, unique=True, null=True, default=None
    )
    """A unique abbreviation of cell type."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this cell type."""
    description: str | None = TextField(null=True, default=None)
    """Description of the cell type."""
    parents: CellType = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent cell type records."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, through="ArtifactCellType", related_name="cell_types"
    )
    """Artifacts linked to the cell type."""

    @overload
    def __init__(
        self,
        name: str,
        ontology_id: str | None,
        abbr: str | None,
        synonyms: str | None,
        description: str | None,
        parents: list[CellType],
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        abbr: str | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> CellType | list[CellType] | None:
        """Create a CellType record from source based on a single identifying field.

        Args:
            name: Name of the cell type (e.g. "T cell", "B cell")
            ontology_id: Cell Ontology ID (e.g. "CL:0000084")
            abbr: Unique abbreviation of cell type
            {doc_from_source}

        Returns:
            A single CellType record, list of CellType records, or None if not found

        Example::

            import bionty as bt

            record = bt.CellType.from_source(name="T cell")
            record = bt.CellType.from_source(ontology_id="CL:0000084")

            source = bt.Source.get(entity="bionty.CellType", source="cl", version="2024-08-16")
            record = bt.CellType.from_source(name="B cell", source=source)
        """
        pass


class Disease(BioRecord, TracksRun, TracksUpdates):
    """Diseases - `Mondo <https://mondo.monarchinitiative.org/>`__, `Human Disease <https://disease-ontology.org/>`__.

    Notes:
        Bulk create Disease records via :meth:`.from_values`.

        For more info, see tutorials: :doc:`docs:disease`.

    Example::

        import bionty as bt

        record = bt.Disease.from_source(name="Alzheimer disease")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=256, db_index=True)
    """Name of the disease."""
    ontology_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """Ontology ID of the disease."""
    abbr: str | None = CharField(
        max_length=32, db_index=True, unique=True, null=True, default=None
    )
    """A unique abbreviation of disease."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this disease."""
    description: str | None = TextField(null=True, default=None)
    """Description of the disease."""
    parents: Disease = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent disease records."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, through="ArtifactDisease", related_name="diseases"
    )
    """Artifacts linked to the disease."""

    @overload
    def __init__(
        self,
        name: str,
        ontology_id: str | None,
        abbr: str | None,
        synonyms: str | None,
        description: str | None,
        parents: list[Disease],
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        abbr: str | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> Disease | list[Disease] | None:
        """Create a Disease record from source based on a single identifying field.

        Args:
            name: Name of the disease (e.g. "Alzheimer disease", "type 2 diabetes")
            ontology_id: Disease ontology ID (e.g. "MONDO:0004975")
            abbr: Unique abbreviation of disease
            {doc_from_source}

        Returns:
            A single Disease record, list of Disease records, or None if not found

        Example::

            import bionty as bt

            record = bt.Disease.from_source(name="Alzheimer disease")
            record = bt.Disease.from_source(ontology_id="MONDO:0004975")
            record = bt.Disease.from_source(name="type 2 diabetes")
        """
        pass


class CellLine(BioRecord, TracksRun, TracksUpdates):
    """Cell lines - `Cell Line Ontology <https://github.com/CLO-ontology/CLO>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:cell_line`.

        Bulk create CellLine records via :meth:`.from_values`.

    Example::

        import bionty as bt

        standard_name = bt.CellLine.public().standardize(["K562"])[0]
        record = bt.CellLine.from_source(name=standard_name)
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=256, db_index=True)
    """Name of the cell line."""
    ontology_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """Ontology ID of the cell line."""
    abbr: str | None = CharField(
        max_length=32, db_index=True, unique=True, null=True, default=None
    )
    """A unique abbreviation of cell line."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this cell line."""
    description: str | None = TextField(null=True, default=None)
    """Description of the cell line."""
    parents: CellLine = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent cell line records."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, through="ArtifactCellLine", related_name="cell_lines"
    )
    """Artifacts linked to the cell line."""

    @overload
    def __init__(
        self,
        name: str,
        ontology_id: str | None,
        abbr: str | None,
        synonyms: str | None,
        description: str | None,
        parents: list[CellLine],
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        abbr: str | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> CellLine | list[CellLine] | None:
        """Create a CellLine record from source based on a single identifying field.

        Args:
            name: Name of the cell line (e.g. "K562", "HeLa")
            ontology_id: Cell Line Ontology ID (e.g. "CLO:0009477")
            abbr: Unique abbreviation of cell line
            {doc_from_source}

        Returns:
            A single CellLine record, list of CellLine records, or None if not found

        Example::

            import bionty as bt

            record = bt.CellLine.from_source(name="K562")
            record = bt.CellLine.from_source(ontology_id="CLO:0009477")
        """
        pass


class Phenotype(BioRecord, TracksRun, TracksUpdates):
    """Phenotypes - `Human Phenotype <https://hpo.jax.org/app/>`__,
    `Phecodes <https://phewascatalog.org/phecodes_icd10>`__,
    `Mammalian Phenotype <http://obofoundry.org/ontology/mp.html>`__,
    `Zebrafish Phenotype <http://obofoundry.org/ontology/zp.html>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:phenotype`.

        Bulk create Phenotype records via :meth:`.from_values`.

    Example::

        import bionty as bt

        record = bt.Phenotype.from_source(name="Arachnodactyly")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=256, db_index=True)
    """Name of the phenotype."""
    ontology_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """Ontology ID of the phenotype."""
    abbr: str | None = CharField(
        max_length=32, db_index=True, unique=True, null=True, default=None
    )
    """A unique abbreviation of phenotype."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this phenotype."""
    description: str | None = TextField(null=True, default=None)
    """Description of the phenotype."""
    parents: Phenotype = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent phenotype records."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, through="ArtifactPhenotype", related_name="phenotypes"
    )
    """Artifacts linked to the phenotype."""

    @overload
    def __init__(
        self,
        name: str,
        ontology_id: str | None,
        abbr: str | None,
        synonyms: str | None,
        description: str | None,
        parents: list[Phenotype],
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        abbr: str | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> Phenotype | list[Phenotype] | None:
        """Create a Phenotype record from source based on a single identifying field.

        Args:
            name: Name of the phenotype (e.g. "Arachnodactyly", "Cardiomegaly")
            ontology_id: Phenotype ontology ID (e.g. "HP:0001166")
            abbr: Unique abbreviation of phenotype
            {doc_from_source}

        Returns:
            A single Phenotype record, list of Phenotype records, or None if not found

        Example::

            import bionty as bt

            record = bt.Phenotype.from_source(name="Arachnodactyly")
            record = bt.Phenotype.from_source(ontology_id="HP:0001166")
        """
        pass


class Pathway(BioRecord, TracksRun, TracksUpdates):
    """Pathways - `Gene Ontology <https://bioportal.bioontology.org/ontologies/GO>`__,
    `Pathway Ontology <https://bioportal.bioontology.org/ontologies/PW>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:pathway`.

        Bulk create Pathway records via :meth:`.from_values`.

    Example::

        import bionty as bt

        record = bt.Pathway.from_source(ontology_id="GO:1903353")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=256, db_index=True)
    """Name of the pathway."""
    ontology_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """Ontology ID of the pathway."""
    abbr: str | None = CharField(
        max_length=32, db_index=True, unique=True, null=True, default=None
    )
    """A unique abbreviation of pathway."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this pathway."""
    description: str | None = TextField(null=True, default=None)
    """Description of the pathway."""
    parents: Pathway = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent pathway records."""
    genes: Gene = models.ManyToManyField("Gene", related_name="pathways")
    """Genes that signifies the pathway."""
    schemas: Schema = models.ManyToManyField(
        Schema, through="SchemaPathway", related_name="pathways"
    )
    """Featuresets linked to the pathway."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact, through="ArtifactPathway", related_name="pathways"
    )
    """Artifacts linked to the pathway."""

    @overload
    def __init__(
        self,
        name: str,
        ontology_id: str | None,
        abbr: str | None,
        synonyms: str | None,
        description: str | None,
        parents: list[Pathway],
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        abbr: str | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> Pathway | list[Pathway] | None:
        """Create a Pathway record from source based on a single identifying field.

        Args:
            name: Name of the pathway (e.g. "mitotic cell cycle", "glycolysis")
            ontology_id: GO or Pathway Ontology ID (e.g. "GO:1903353", "PW:0000004")
            abbr: Unique abbreviation of pathway
            {doc_from_source}

        Returns:
            A single Pathway record, list of Pathway records, or None if not found

        Example::

            import bionty as bt

            record = bt.Pathway.from_source(name="mitotic cell cycle")
            record = bt.Pathway.from_source(ontology_id="GO:1903353")
        """
        pass


class ExperimentalFactor(BioRecord, TracksRun, TracksUpdates):
    """Experimental factors - `Experimental Factor Ontology <https://www.ebi.ac.uk/ols/ontologies/efo>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:experimental_factor`.

        Bulk create ExperimentalFactor records via :meth:`.from_values`.

    Example::

        import bionty as bt

        standard_name = bt.ExperimentalFactor.public().standardize(["scRNA-seq"])
        record = bt.ExperimentalFactor.from_source(name=standard_name)
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=256, db_index=True)
    """Name of the experimental factor."""
    ontology_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """Ontology ID of the experimental factor."""
    abbr: str | None = CharField(
        max_length=32, db_index=True, unique=True, null=True, default=None
    )
    """A unique abbreviation of experimental factor."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this experimental factor."""
    description: str | None = TextField(null=True, default=None)
    """Description of the experimental factor."""
    molecule: str | None = TextField(null=True, default=None, db_index=True)
    """Molecular experimental factor, parsed from EFO."""
    instrument: str | None = TextField(null=True, default=None, db_index=True)
    """Instrument used to measure the experimental factor, parsed from EFO."""
    measurement: str | None = TextField(null=True, default=None, db_index=True)
    """Phenotypic experimental factor, parsed from EFO."""
    parents: ExperimentalFactor = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent experimental factor records."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact,
        through="ArtifactExperimentalFactor",
        related_name="experimental_factors",
    )
    """Artifacts linked to the experimental_factors."""

    @overload
    def __init__(
        self,
        name: str,
        ontology_id: str | None,
        abbr: str | None,
        synonyms: str | None,
        description: str | None,
        parents: list[ExperimentalFactor],
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        abbr: str | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> ExperimentalFactor | list[ExperimentalFactor] | None:
        """Create an ExperimentalFactor record from source based on a single identifying field.

        Args:
            name: Name of the experimental factor (e.g. "scRNA-seq", "ChIP-seq")
            ontology_id: Experimental Factor Ontology ID (e.g. "EFO:0009922")
            abbr: Unique abbreviation of experimental factor
            {doc_from_source}

        Returns:
            A single ExperimentalFactor record, list of ExperimentalFactor records, or None if not found

        Example::

            import bionty as bt

            record = bt.ExperimentalFactor.from_source(name="scRNA-seq")
            record = bt.ExperimentalFactor.from_source(ontology_id="EFO:0009922")
        """
        pass


class DevelopmentalStage(BioRecord, TracksRun, TracksUpdates):
    """Developmental stages - `Human Developmental Stages <https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv>`__,
    `Mouse Developmental Stages <https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv>`__.  # noqa.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:developmental_stage`.

        Bulk create DevelopmentalStage records via :meth:`.from_values`.

    Example::

        import bionty as bt

        record = bt.DevelopmentalStage.from_source(name="neurula stage")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=256, db_index=True)
    """Name of the developmental stage."""
    ontology_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """Ontology ID of the developmental stage."""
    abbr: str | None = CharField(
        max_length=32, db_index=True, unique=True, null=True, default=None
    )
    """A unique abbreviation of developmental stage."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this developmental stage."""
    description: str | None = TextField(null=True, default=None)
    """Description of the developmental stage."""
    parents: str | None = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent developmental stage records."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact,
        through="ArtifactDevelopmentalStage",
        related_name="developmental_stages",
    )
    """Artifacts linked to the developmental stage."""

    @overload
    def __init__(
        self,
        name: str,
        ontology_id: str | None,
        abbr: str | None,
        synonyms: str | None,
        description: str | None,
        parents: list[DevelopmentalStage],
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        abbr: str | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> DevelopmentalStage | list[DevelopmentalStage] | None:
        """Create a DevelopmentalStage record from source based on a single identifying field.

        Args:
            name: Name of the developmental stage (e.g. "neurula stage", "gastrula stage")
            ontology_id: Developmental stage ontology ID (e.g. "HsapDv:0000004")
            abbr: Unique abbreviation of developmental stage
            {doc_from_source}

        Returns:
            A single DevelopmentalStage record, list of DevelopmentalStage records, or None if not found

        Example::

            import bionty as bt

            record = bt.DevelopmentalStage.from_source(name="neurula stage")
            record = bt.DevelopmentalStage.from_source(ontology_id="HsapDv:0000004")
        """
        pass


class Ethnicity(BioRecord, TracksRun, TracksUpdates):
    """Ethnicity - `Human Ancestry Ontology <https://github.com/EBISPOT/hancestro>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:ethnicity`.

        Bulk create Ethnicity records via :meth:`.from_values`.

    Example::

        import bionty as bt

        record = bt.Ethnicity.from_source(name="European")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (base62-encoded hash of defining fields)."""
    name: str = CharField(max_length=256, db_index=True)
    """Name of the ethnicity."""
    ontology_id: str | None = CharField(
        max_length=32, db_index=True, null=True, default=None
    )
    """Ontology ID of the ethnicity."""
    abbr: str | None = CharField(
        max_length=32, db_index=True, unique=True, null=True, default=None
    )
    """A unique abbreviation of ethnicity."""
    synonyms: str | None = TextField(null=True, default=None)
    """Bar-separated (|) synonyms that correspond to this ethnicity."""
    description: str | None = TextField(null=True, default=None)
    """Description of the ethnicity."""
    parents: Ethnicity = models.ManyToManyField(
        "self", symmetrical=False, related_name="children"
    )
    """Parent ethnicity records."""
    artifacts: Artifact = models.ManyToManyField(
        Artifact,
        through="ArtifactEthnicity",
        related_name="ethnicities",
    )
    """Artifacts linked to the ethnicity."""

    @overload
    def __init__(
        self,
        name: str,
        ontology_id: str | None,
        abbr: str | None,
        synonyms: str | None,
        description: str | None,
        parents: list[Ethnicity],
        source: Source | None,
    ): ...

    @overload
    def __init__(
        self,
        *db_args,
    ): ...

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @classmethod
    @pass_to_super
    @_doc_params(doc_from_source=doc_from_source)
    def from_source(
        cls,
        *,
        name: str | None = None,
        ontology_id: str | None = None,
        abbr: str | None = None,
        source: Source | None = None,
        mute: bool = False,
        **kwargs,
    ) -> Ethnicity | list[Ethnicity] | None:
        """Create an Ethnicity record from source based on a single identifying field.

        Args:
            name: Name of the ethnicity (e.g. "European", "East Asian")
            ontology_id: Human Ancestry Ontology ID (e.g. "HANCESTRO:0005")
            abbr: Unique abbreviation of ethnicity
            {doc_from_source}

        Returns:
            A single Ethnicity record, list of Ethnicity records, or None if not found

        Example::

            import bionty as bt

            record = bt.Ethnicity.from_source(name="European")
            record = bt.Ethnicity.from_source(ontology_id="HANCESTRO:0005")
        """
        pass


class SchemaGene(BasicRecord, LinkORM):
    id: int = models.BigAutoField(primary_key=True)
    # follow the .lower() convention in link models
    schema: Schema = ForeignKey("lamindb.Schema", CASCADE, related_name="links_gene")
    gene: Gene = ForeignKey("Gene", PROTECT, related_name="links_schema")

    class Meta:
        unique_together = ("schema", "gene")


class SchemaProtein(BasicRecord, LinkORM):
    id: int = models.BigAutoField(primary_key=True)
    # follow the .lower() convention in link models
    schema: Schema = ForeignKey("lamindb.Schema", CASCADE, related_name="links_protein")
    protein: Protein = ForeignKey("Protein", PROTECT, related_name="links_schema")

    class Meta:
        unique_together = ("schema", "protein")


class SchemaCellMarker(BasicRecord, LinkORM):
    id: int = models.BigAutoField(primary_key=True)
    # follow the .lower() convention in link models
    schema: Schema = ForeignKey(
        "lamindb.Schema", CASCADE, related_name="links_cellmarker"
    )
    cellmarker: CellMarker = ForeignKey(
        "CellMarker", PROTECT, related_name="links_schema"
    )

    class Meta:
        unique_together = ("schema", "cellmarker")


class SchemaPathway(BasicRecord, LinkORM):
    id: int = models.BigAutoField(primary_key=True)
    # follow the .lower() convention in link models
    schema: Schema = ForeignKey("lamindb.Schema", CASCADE, related_name="links_pathway")
    pathway: Pathway = ForeignKey("Pathway", PROTECT, related_name="links_schema")

    class Meta:
        unique_together = ("schema", "pathway")


class ArtifactOrganism(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_organism")
    organism: Organism = ForeignKey("Organism", PROTECT, related_name="links_artifact")
    feature: Feature = ForeignKey(
        Feature, PROTECT, null=True, default=None, related_name="links_artifactorganism"
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "organism", "feature")


class ArtifactGene(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_gene")
    gene: Gene = ForeignKey("Gene", PROTECT, related_name="links_artifact")
    feature: Feature = ForeignKey(
        Feature, PROTECT, null=True, default=None, related_name="links_artifactgene"
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "gene", "feature")


class ArtifactProtein(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_protein")
    protein: Protein = ForeignKey("Protein", PROTECT, related_name="links_artifact")
    feature: Feature = ForeignKey(
        Feature, PROTECT, null=True, default=None, related_name="links_artifactprotein"
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "protein", "feature")


class ArtifactCellMarker(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_cell_marker")
    # follow the .lower() convention in link models
    cellmarker: CellMarker = ForeignKey(
        "CellMarker", PROTECT, related_name="links_artifact"
    )
    feature: Feature = ForeignKey(
        Feature,
        PROTECT,
        null=True,
        default=None,
        related_name="links_artifactcellmarker",
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "cellmarker", "feature")


class ArtifactTissue(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_tissue")
    tissue: Tissue = ForeignKey("Tissue", PROTECT, related_name="links_artifact")
    feature: Feature = ForeignKey(
        Feature, PROTECT, null=True, default=None, related_name="links_artifacttissue"
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "tissue", "feature")


class ArtifactCellType(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_cell_type")
    # follow the .lower() convention in link models
    celltype: CellType = ForeignKey("CellType", PROTECT, related_name="links_artifact")
    feature: Feature = ForeignKey(
        Feature, PROTECT, null=True, default=None, related_name="links_artifactcelltype"
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "celltype", "feature")


class ArtifactDisease(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_disease")
    disease: Disease = ForeignKey("Disease", PROTECT, related_name="links_artifact")
    feature: Feature = ForeignKey(
        Feature, PROTECT, null=True, default=None, related_name="links_artifactdisease"
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "disease", "feature")


class ArtifactCellLine(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_cell_line")
    # follow the .lower() convention in link models
    cellline: CellLine = ForeignKey("CellLine", PROTECT, related_name="links_artifact")
    feature: Feature = ForeignKey(
        Feature, PROTECT, null=True, default=None, related_name="links_artifactcellline"
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "cellline", "feature")


class ArtifactPhenotype(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_phenotype")
    phenotype: Phenotype = ForeignKey(
        "Phenotype", PROTECT, related_name="links_artifact"
    )
    feature: Feature = ForeignKey(
        Feature,
        PROTECT,
        null=True,
        default=None,
        related_name="links_artifactphenotype",
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "phenotype", "feature")


class ArtifactPathway(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_pathway")
    pathway: Pathway = ForeignKey("Pathway", PROTECT, related_name="links_artifact")
    feature: Feature = ForeignKey(
        Feature, PROTECT, null=True, default=None, related_name="links_artifactpathway"
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "pathway", "feature")


class ArtifactExperimentalFactor(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(
        Artifact, CASCADE, related_name="links_experimental_factor"
    )
    experimentalfactor: ExperimentalFactor = ForeignKey(
        "ExperimentalFactor", PROTECT, related_name="links_artifact"
    )
    feature: Feature = ForeignKey(
        Feature,
        PROTECT,
        null=True,
        default=None,
        related_name="links_artifactexperimentalfactor",
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "experimentalfactor", "feature")


class ArtifactDevelopmentalStage(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(
        Artifact, CASCADE, related_name="links_developmental_stage"
    )
    # follow the .lower() convention in link models
    developmentalstage: DevelopmentalStage = ForeignKey(
        "DevelopmentalStage", PROTECT, related_name="links_artifact"
    )
    feature: Feature = ForeignKey(
        Feature,
        PROTECT,
        null=True,
        default=None,
        related_name="links_artifactdevelopmentalstage",
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "developmentalstage", "feature")


class ArtifactEthnicity(BasicRecord, LinkORM, TracksRun):
    id: int = models.BigAutoField(primary_key=True)
    artifact: Artifact = ForeignKey(Artifact, CASCADE, related_name="links_ethnicity")
    ethnicity: Ethnicity = ForeignKey(
        "Ethnicity", PROTECT, related_name="links_artifact"
    )
    feature: Feature = ForeignKey(
        Feature,
        PROTECT,
        null=True,
        default=None,
        related_name="links_artifactethnicity",
    )
    label_ref_is_name: bool | None = BooleanField(null=True, default=None)
    feature_ref_is_name: bool | None = BooleanField(null=True, default=None)

    class Meta:
        unique_together = ("artifact", "ethnicity", "feature")


# backward compat
Species = Organism
BiontySource = Source
BioRegistry = BioRecord
PublicSource = Source

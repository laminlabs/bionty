from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, overload

import numpy as np
from django.db import models
from django.db.models import CASCADE, PROTECT
from lamin_utils import logger
from lnschema_core.fields import (
    BigIntegerField,
    BooleanField,
    CharField,
    ForeignKey,
    TextField,
)
from lnschema_core.models import (
    Artifact,
    CanCurate,
    Feature,
    FeatureSet,
    HasParents,
    LinkORM,
    Record,
    TracksRun,
    TracksUpdates,
)

import bionty.base as bt_base

from . import ids
from ._bionty import encode_uid, lookup2kwargs
from .base import PublicOntology
from .base._public_ontology import InvalidParamError

if TYPE_CHECKING:
    from pandas import DataFrame


class StaticReference(PublicOntology):
    def __init__(self, source_record: Source) -> None:
        self._source_record = source_record
        super().__init__(
            source=source_record.name,
            version=source_record.version,
            organism=source_record.organism,
        )

    def _load_df(self) -> DataFrame:
        return self._source_record.dataframe_artifact.load(is_run_input=False)  # type:ignore


class Source(Record, TracksRun, TracksUpdates):
    """Versions of ontology sources.

    .. warning::

        Do not modify the records unless you know what you are doing!
    """

    _name_field: str = "name"

    class Meta(Record.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("entity", "name", "organism", "version"),)

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=4, default=ids.source)
    """A universal id (hash of selected field)."""
    entity: str = CharField(max_length=256, db_index=True)
    """Entity class name."""
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

    def set_as_currently_used(self):
        """Set this record as the currently used source.

        Examples:
            >>> record = bionty.Source.get(uid="...")
            >>> record.set_as_currently_used()
        """
        # set this record as currently used
        self.currently_used = True
        self.save()
        # set all other records as not currently used
        Source.filter(
            entity=self.entity, organism=self.organism, name=self.name
        ).exclude(uid=self.uid).update(currently_used=False)
        logger.success(f"set {self} as currently used.")
        logger.warning("please reload your instance to reflect the updates!")


class BioRecord(Record, HasParents, CanCurate):
    """Base Record of bionty.

    BioRecord inherits all methods from :class:`~lamindb.core.Record` and provides additional methods
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
            and isinstance(args[0], (tuple, list))
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
            if isinstance(parents, (list, np.ndarray)) and len(parents) > 0:
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
        ontology_ids: list[str] | None = None,
        organism: str | Record | None = None,
        ignore_conflicts: bool = True,
    ):
        """Bulk save records from a Bionty ontology.

        Use this method to initialize your registry with public ontology.

        Args:
            ontology_ids: List of ontology ids to save.
            organism: Organism name or record.
            source: Source record to import records from.
            ignore_conflicts: Whether to ignore conflicts during bulk record creation.

        Examples:
            >>> bionty.CellType.import_source()
        """
        from .core._add_ontology import add_ontology_from_df, check_source_in_db

        if hasattr(cls, "ontology_id"):
            add_ontology_from_df(
                registry=cls,
                ontology_ids=ontology_ids,
                organism=organism,
                source=source,
                ignore_conflicts=ignore_conflicts,
            )
        else:
            import lamindb as ln

            from ._bionty import get_source_record

            public = cls.public(organism=organism, source=source)
            logger.info(
                f"importing {cls.__name__} records from {public.source}, {public.version}"
            )
            # TODO: consider StaticReference
            source_record = get_source_record(public, cls)  # type:ignore
            df = public.df().reset_index()
            if hasattr(cls, "_ontology_id_field"):
                field = cls._ontology_id_field
            else:
                raise NotImplementedError(
                    f"import_source is not implemented for {cls.__name__}"
                )
            records = cls.from_values(
                ontology_ids or df[field],
                field=field,
                organism=organism,
                source=source_record,
            )

            new_records = [r for r in records if r._state.adding]
            logger.info(f"saving {len(new_records)} new records...")
            ln.save(new_records, ignore_conflicts=ignore_conflicts)
            logger.success("import is completed!")

            # make sure source.in_db is correctly set based on the DB content
            check_source_in_db(registry=cls, source=source_record)

    @classmethod
    def add_source(cls, source: Source, currently_used=True) -> Source:
        """Configure a source of the entity."""
        import lamindb as ln

        unique_kwargs = {
            "entity": cls.__get_name_with_schema__(),
            "name": source.name,
            "version": source.version,
            "organism": source.organism,
        }
        add_kwargs = {
            "currently_used": currently_used,
            "description": source.description,
            "url": source.url,
            "source_website": source.source_website,
            "dataframe_artifact_id": source.dataframe_artifact_id,
        }
        new_source = Source.filter(**unique_kwargs).one_or_none()
        if new_source is None:
            try:
                ln.settings.creation.search_names = False
                new_source = Source(**unique_kwargs, **add_kwargs).save()
            finally:
                ln.settings.creation.search_names = True
        else:
            logger.warning("source already exists!")
            return new_source
        # get the dataframe from laminlabs/bionty-assets
        bionty_source = (
            Source.using("laminlabs/bionty-assets")
            .filter(
                **{
                    "entity": source.entity,
                    "name": source.name,
                    "version": source.version,
                    "organism": source.organism,
                }
            )
            .one_or_none()
        )
        if bionty_source is None:
            logger.warning(
                "please register a DataFrame artifact!   \n"
                "→ artifact = ln.Artifact(df, visibility=0, run=False).save()   \n"
                "→ source.dataframe_artifact = artifact   \n"
                "→ source.save()"
            )
        else:
            df_artifact = ln.Artifact(
                bionty_source.dataframe_artifact.path, visibility=0, run=False
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

        Examples:
            >>> celltype_pub = bionty.CellType.public()
            >>> celltype_pub
            PublicOntology
            Entity: CellType
            Organism: all
            Source: cl, 2023-04-20
            #terms: 2698
        """
        if isinstance(organism, Organism):
            organism = organism.name

        if source is not None:
            organism = source.organism
            source_name = source.name
            version = source.version
        else:
            from .core._settings import settings

            if hasattr(cls, "organism_id"):
                if organism is None and settings.organism is not None:
                    organism = settings.organism.name
            source_name = None
            version = None

        try:
            return getattr(bt_base, cls.__name__)(
                organism=organism, source=source_name, version=version
            )
        except InvalidParamError as e:
            raise ValueError(str(e)) from None
        except (AttributeError, ValueError):
            if source is None:
                kwargs = {
                    "entity": cls.__get_name_with_schema__(),
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
    def _from_public(cls, *args, **kwargs) -> BioRecord | list[BioRecord] | None:
        """Deprecated in favor of `from_source`."""
        warnings.warn(
            "`.from_public()` is deprecated and will be removed in a future version. Use `.from_source()` instead!",
            DeprecationWarning,
            stacklevel=2,
        )
        return cls.from_source(*args, **kwargs)

    @classmethod
    def _import_from_source(
        cls,
        source: Source | None = None,
        ontology_ids: list[str] | None = None,
        organism: str | Record | None = None,
        ignore_conflicts: bool = True,
    ):
        """Deprecated in favor of `import_source`."""
        warnings.warn(
            "`.import_from_source()` is deprecated and will be removed in a future version. Use `.import_source()` instead!",
            DeprecationWarning,
            stacklevel=2,
        )
        return cls.import_source(
            source=source,
            ontology_ids=ontology_ids,
            organism=organism,
            ignore_conflicts=ignore_conflicts,
        )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        import sys

        # Deprecated methods
        if "sphinx" not in sys.modules:
            cls.from_public = cls._from_public
            cls.import_from_source = cls._import_from_source

    @classmethod
    def from_source(
        cls, *, mute: bool = False, **kwargs
    ) -> BioRecord | list[BioRecord] | None:
        """Create a record or records from source based on a single field value.

        Notes:
            For more info, see tutorial :doc:`docs:bionty`

            Bulk create records via :meth:`.from_values`.

        Examples:
            Create a record by passing a field value:

            >>> record = bionty.Gene.from_source(symbol="TCF7", organism="human")

            Create a record from non-default source:

            >>> source = bionty.Source.get(entity="CellType", source="cl", version="2022-08-16")  # noqa
            >>> record = bionty.CellType.from_source(name="T cell", source=source)

        """
        # non-relationship kwargs
        kv = {
            k: v
            for k, v in kwargs.items()
            if k not in [i.name for i in cls._meta.fields if i.is_relation]
        }
        if len(kv) > 1:
            raise AssertionError(
                "Only one field can be passed to generate record from public reference"
            )
        elif len(kv) == 0:
            return None
        else:
            k = next(iter(kv))
            v = kwargs.pop(k)
            results = cls.from_values([v], field=getattr(cls, k), mute=mute, **kwargs)
            if len(results) == 1:
                return results[0]
            elif len(results) == 0:
                return None
            else:
                return results

    def save(self, *args, **kwargs) -> BioRecord:
        """Save the record and its parents recursively."""
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


    Examples:
        >>> record = bionty.Organism.from_source(name="rabbit")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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


class Gene(BioRecord, TracksRun, TracksUpdates):
    """Genes - `Ensembl <https://ensembl.org/>`__, `NCBI Gene <https://www.ncbi.nlm.nih.gov/gene/>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:gene`.

        Bulk create Gene records via `.from_values()`.
        Map legacy ensembl IDs to current ensembl IDs using :meth:`bionty.base.Gene.map_legacy_ids`.

        We discourage validating gene symbols and to work with unique identifiers such as ENSEMBL IDs instead.
        For more details, see :doc:`docs:faq/symbol-mapping`.

    Examples:
        >>> record = bionty.Gene.from_source(symbol="TCF7", organism="human")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False

    _name_field: str = "symbol"
    _ontology_id_field: str = "ensembl_gene_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=12, default=ids.gene)
    """A universal id (hash of selected field)."""
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
    feature_sets: FeatureSet = models.ManyToManyField(
        FeatureSet, through="FeatureSetGene", related_name="genes"
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


class Protein(BioRecord, TracksRun, TracksUpdates):
    """Proteins - `Uniprot <https://www.uniprot.org/>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:protein`.

        Bulk create records via :meth:`.from_values`.

    Examples:
        >>> record = bionty.Protein.from_source(name="Synaptotagmin-15B", organism="human")
        >>> record = bionty.Protein.from_source(gene_symbol="SYT15B", organism="human")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False

    _name_field: str = "name"
    _ontology_id_field: str = "uniprotkb_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=12, default=ids.protein)
    """A universal id (hash of selected field)."""
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
    feature_sets: FeatureSet = models.ManyToManyField(
        FeatureSet, through="FeatureSetProtein", related_name="proteins"
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


class CellMarker(BioRecord, TracksRun, TracksUpdates):
    """Cell markers - `CellMarker <http://xteam.xbio.top/CellMarker>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:cell_marker`.

        Bulk create CellMarker records via :meth:`.from_values`.

    Examples:
        >>> record = bionty.CellMarker.from_source(name="PD1", organism="human")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "organism"),)

    _name_field: str = "name"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=12, default=ids.cellmarker)
    """A universal id (hash of selected field)."""
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
    feature_sets: FeatureSet = models.ManyToManyField(
        FeatureSet, through="FeatureSetCellMarker", related_name="cell_markers"
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


class Tissue(BioRecord, TracksRun, TracksUpdates):
    """Tissues - `Uberon <http://obophenotype.github.io/uberon/>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` :doc:`docs:tissue`.

        Bulk create Tissue records via :meth:`.from_values`.

    Examples:
        >>> record = bionty.Tissue.from_source(name="brain")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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


class CellType(BioRecord, TracksRun, TracksUpdates):
    """Cell types - `Cell Ontology <https://obophenotype.github.io/cell-ontology/>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:cell_type`.

        Bulk create CellType records via :meth:`.from_values`.

    Examples:
        >>> record = bionty.CellType.from_source(name="T cell")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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


class Disease(BioRecord, TracksRun, TracksUpdates):
    """Diseases - `Mondo <https://mondo.monarchinitiative.org/>`__, `Human Disease <https://disease-ontology.org/>`__.

    Notes:
        Bulk create Disease records via :meth:`.from_values`.

        For more info, see tutorials: :doc:`docs:disease`.

    Examples:
        >>> record = bionty.Disease.from_source(name="Alzheimer disease")
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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


class CellLine(BioRecord, TracksRun, TracksUpdates):
    """Cell lines - `Cell Line Ontology <https://github.com/CLO-ontology/CLO>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:cell_line`.

        Bulk create CellLine records via :meth:`.from_values`.

    Examples:
        >>> standard_name = bionty.CellLine.public().standardize(["K562"])[0]
        >>> record = bionty.CellLine.from_source(name=standard_name)
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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


class Phenotype(BioRecord, TracksRun, TracksUpdates):
    """Phenotypes - `Human Phenotype <https://hpo.jax.org/app/>`__,
    `Phecodes <https://phewascatalog.org/phecodes_icd10>`__,
    `Mammalian Phenotype <http://obofoundry.org/ontology/mp.html>`__,
    `Zebrafish Phenotype <http://obofoundry.org/ontology/zp.html>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:phenotype`.

        Bulk create Phenotype records via :meth:`.from_values`.

    Examples:
        >>> record = bionty.Phenotype.from_source(name="Arachnodactyly")
        >>> record.save()
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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


class Pathway(BioRecord, TracksRun, TracksUpdates):
    """Pathways - `Gene Ontology <https://bioportal.bioontology.org/ontologies/GO>`__,
    `Pathway Ontology <https://bioportal.bioontology.org/ontologies/PW>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:pathway`.

        Bulk create Pathway records via :meth:`.from_values`.

    Examples:
        >>> record = bionty.Pathway.from_source(ontology_id="GO:1903353")
        >>> record.save()
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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
    feature_sets: FeatureSet = models.ManyToManyField(
        FeatureSet, through="FeatureSetPathway", related_name="pathways"
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


class ExperimentalFactor(BioRecord, TracksRun, TracksUpdates):
    """Experimental factors - `Experimental Factor Ontology <https://www.ebi.ac.uk/ols/ontologies/efo>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:experimental_factor`.

        Bulk create ExperimentalFactor records via :meth:`.from_values`.

    Examples:
        >>> standard_name = bionty.ExperimentalFactor.public().standardize(["scRNA-seq"])
        >>> record = bionty.ExperimentalFactor.from_source(name=standard_name)
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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


class DevelopmentalStage(BioRecord, TracksRun, TracksUpdates):
    """Developmental stages - `Human Developmental Stages <https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv>`__,
    `Mouse Developmental Stages <https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv>`__.  # noqa.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:developmental_stage`.

        Bulk create DevelopmentalStage records via :meth:`.from_values`.

    Examples:
        >>> record = bionty.DevelopmentalStage.from_source(name="neurula stage")
        >>> record.save()
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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


class Ethnicity(BioRecord, TracksRun, TracksUpdates):
    """Ethnicity - `Human Ancestry Ontology <https://github.com/EBISPOT/hancestro>`__.

    Notes:
        For more info, see tutorials :doc:`docs:bio-registries` and :doc:`docs:ethnicity`.

        Bulk create Ethnicity records via :meth:`.from_values`.

    Examples:
        >>> record = bionty.Ethnicity.from_source(name="European")
        >>> record.save()
    """

    class Meta(BioRecord.Meta, TracksRun.Meta, TracksUpdates.Meta):
        abstract = False
        unique_together = (("name", "ontology_id"),)

    _name_field: str = "name"
    _ontology_id_field: str = "ontology_id"

    id: int = models.AutoField(primary_key=True)
    """Internal id, valid only in one DB instance."""
    uid: str = CharField(unique=True, max_length=8, default=ids.ontology)
    """A universal id (hash of selected field)."""
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


class FeatureSetGene(Record, LinkORM):
    id: int = models.BigAutoField(primary_key=True)
    # follow the .lower() convention in link models
    featureset: FeatureSet = ForeignKey(
        "lnschema_core.FeatureSet", CASCADE, related_name="+"
    )
    gene: Gene = ForeignKey("Gene", PROTECT, related_name="+")

    class Meta:
        unique_together = ("featureset", "gene")


class FeatureSetProtein(Record, LinkORM):
    id: int = models.BigAutoField(primary_key=True)
    # follow the .lower() convention in link models
    featureset: FeatureSet = ForeignKey(
        "lnschema_core.FeatureSet", CASCADE, related_name="+"
    )
    protein: Protein = ForeignKey("Protein", PROTECT, related_name="+")

    class Meta:
        unique_together = ("featureset", "protein")


class FeatureSetCellMarker(Record, LinkORM):
    id: int = models.BigAutoField(primary_key=True)
    # follow the .lower() convention in link models
    featureset: FeatureSet = ForeignKey(
        "lnschema_core.FeatureSet", CASCADE, related_name="+"
    )
    # follow the .lower() convention in link models
    cellmarker: CellMarker = ForeignKey("CellMarker", PROTECT, related_name="+")

    class Meta:
        unique_together = ("featureset", "cellmarker")


class FeatureSetPathway(Record, LinkORM):
    id: int = models.BigAutoField(primary_key=True)
    # follow the .lower() convention in link models
    featureset: FeatureSet = ForeignKey(
        "lnschema_core.FeatureSet", CASCADE, related_name="+"
    )
    pathway: Pathway = ForeignKey("Pathway", PROTECT, related_name="+")

    class Meta:
        unique_together = ("featureset", "pathway")


class ArtifactOrganism(Record, LinkORM, TracksRun):
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


class ArtifactGene(Record, LinkORM, TracksRun):
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


class ArtifactProtein(Record, LinkORM, TracksRun):
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


class ArtifactCellMarker(Record, LinkORM, TracksRun):
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


class ArtifactTissue(Record, LinkORM, TracksRun):
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


class ArtifactCellType(Record, LinkORM, TracksRun):
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


class ArtifactDisease(Record, LinkORM, TracksRun):
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


class ArtifactCellLine(Record, LinkORM, TracksRun):
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


class ArtifactPhenotype(Record, LinkORM, TracksRun):
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


class ArtifactPathway(Record, LinkORM, TracksRun):
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


class ArtifactExperimentalFactor(Record, LinkORM, TracksRun):
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


class ArtifactDevelopmentalStage(Record, LinkORM, TracksRun):
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


class ArtifactEthnicity(Record, LinkORM, TracksRun):
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

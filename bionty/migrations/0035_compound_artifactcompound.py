# Generated by Django 5.0.3 on 2024-08-08 15:27

import django.db.models.deletion
import lnschema_core.models
import lnschema_core.users
from django.db import migrations, models

import bionty.ids


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0034_alter_source_unique_together"),
        (
            "lnschema_core",
            "0059_alter_artifact__accessor_alter_artifact__hash_type_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Compound",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uid",
                    models.CharField(
                        default=bionty.ids.ontology, max_length=8, unique=True
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=256)),
                (
                    "ontology_id",
                    models.CharField(
                        db_index=True, default=None, max_length=32, null=True
                    ),
                ),
                (
                    "abbr",
                    models.CharField(
                        db_index=True,
                        default=None,
                        max_length=32,
                        null=True,
                        unique=True,
                    ),
                ),
                ("synonyms", models.TextField(default=None, null=True)),
                ("description", models.TextField(default=None, null=True)),
                (
                    "_previous_runs",
                    models.ManyToManyField(related_name="+", to="lnschema_core.run"),
                ),
                (
                    "artifacts",
                    models.ManyToManyField(
                        related_name="compounds",
                        through="bionty.ArtifactEthnicity",
                        to="lnschema_core.artifact",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        default=lnschema_core.users.current_user_id,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="lnschema_core.user",
                    ),
                ),
                (
                    "parents",
                    models.ManyToManyField(
                        related_name="children", to="bionty.compound"
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        default=lnschema_core.models.current_run,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="lnschema_core.run",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="compounds",
                        to="bionty.source",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("name", "ontology_id")},
            },
            bases=(
                models.Model,
                lnschema_core.models.HasParents,
                lnschema_core.models.CanValidate,
            ),
        ),
        migrations.CreateModel(
            name="ArtifactCompound",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("label_ref_is_name", models.BooleanField(default=None, null=True)),
                ("feature_ref_is_name", models.BooleanField(default=None, null=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="links_compound",
                        to="lnschema_core.artifact",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        default=lnschema_core.users.current_user_id,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="lnschema_core.user",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="links_artifactcompound",
                        to="lnschema_core.feature",
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        default=lnschema_core.models.current_run,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="lnschema_core.run",
                    ),
                ),
                (
                    "compound",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="links_artifact",
                        to="bionty.compound",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(lnschema_core.models.LinkORM, models.Model),
        ),
    ]

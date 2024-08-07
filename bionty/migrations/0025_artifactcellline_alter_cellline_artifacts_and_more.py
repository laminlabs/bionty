# Generated by Django 5.0.6 on 2024-05-16 06:06

import django.db.models.deletion
import lnschema_core.models
import lnschema_core.users
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0024_remove_cellline_collections_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArtifactOrganism",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "organism",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.Organism"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactGene",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "gene",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.Gene"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactProtein",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "protein",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.Protein"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactCellMarker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "cell_marker",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.CellMarker"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactTissue",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "tissue",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.Tissue"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactCellType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "cell_type",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.CellType"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactDisease",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "disease",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.Disease"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactCellLine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "cell_line",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.CellLine"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactPhenotype",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "phenotype",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.Phenotype"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactPathway",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "pathway",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.Pathway"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactExperimentalFactor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "experimental_factor",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        to="bionty.ExperimentalFactor",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactDevelopmentalStage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "developmental_stage",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        to="bionty.DevelopmentalStage",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactEthnicity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        null=True,
                        default=None,
                        to="lnschema_core.Feature",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        default=lnschema_core.users.current_user_id,
                        to="lnschema_core.User",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="lnschema_core.Artifact"
                    ),
                ),
                (
                    "ethnicity",
                    models.ForeignKey(on_delete=models.CASCADE, to="bionty.Ethnicity"),
                ),
            ],
        ),
        # Insert data into the new through models
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactorganism (artifact_id, organism_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, organism_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_organism_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactgene (artifact_id, gene_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, gene_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_gene_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactprotein (artifact_id, protein_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, protein_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_protein_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactcellmarker (artifact_id, cell_marker_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, cellmarker_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_cellmarker_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifacttissue (artifact_id, tissue_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, tissue_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_tissue_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactcelltype (artifact_id, cell_type_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, celltype_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_celltype_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactdisease (artifact_id, disease_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, disease_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_disease_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactcellline (artifact_id, cell_line_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, cellline_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_cellline_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactphenotype (artifact_id, phenotype_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, phenotype_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_phenotype_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactpathway (artifact_id, pathway_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, pathway_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_pathway_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactexperimentalfactor (artifact_id, experimental_factor_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, experimentalfactor_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_experimentalfactor_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactdevelopmentalstage (artifact_id, developmental_stage_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, developmentalstage_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_developmentalstage_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        migrations.RunSQL(
            f"""
            INSERT INTO bionty_artifactethnicity (artifact_id, ethnicity_id, feature_id, created_by_id, created_at)
            SELECT artifact_id, ethnicity_id, NULL, {1}, CURRENT_TIMESTAMP
            FROM bionty_ethnicity_artifacts;
            """  # Replace with appropriate user_id logic
        ),
        # Remove the old ManyToMany fields and replace them with the new through models
        migrations.RemoveField(
            model_name="organism",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="organism",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactOrganism",
                to="lnschema_core.Artifact",
                related_name="organisms",
            ),
        ),
        migrations.RemoveField(
            model_name="gene",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="gene",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactGene",
                to="lnschema_core.Artifact",
                related_name="genes",
            ),
        ),
        migrations.RemoveField(
            model_name="protein",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="protein",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactProtein",
                to="lnschema_core.Artifact",
                related_name="proteins",
            ),
        ),
        migrations.RemoveField(
            model_name="cellmarker",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="cellmarker",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactCellMarker",
                to="lnschema_core.Artifact",
                related_name="cell_markers",
            ),
        ),
        migrations.RemoveField(
            model_name="tissue",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="tissue",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactTissue",
                to="lnschema_core.Artifact",
                related_name="tissues",
            ),
        ),
        migrations.RemoveField(
            model_name="celltype",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="celltype",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactCellType",
                to="lnschema_core.Artifact",
                related_name="cell_types",
            ),
        ),
        migrations.RemoveField(
            model_name="disease",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="disease",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactDisease",
                to="lnschema_core.Artifact",
                related_name="diseases",
            ),
        ),
        migrations.RemoveField(
            model_name="cellline",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="cellline",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactCellLine",
                to="lnschema_core.Artifact",
                related_name="cell_lines",
            ),
        ),
        migrations.RemoveField(
            model_name="phenotype",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="phenotype",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactPhenotype",
                to="lnschema_core.Artifact",
                related_name="phenotypes",
            ),
        ),
        migrations.RemoveField(
            model_name="pathway",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="pathway",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactPathway",
                to="lnschema_core.Artifact",
                related_name="pathways",
            ),
        ),
        migrations.RemoveField(
            model_name="experimentalfactor",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="experimentalfactor",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactExperimentalFactor",
                to="lnschema_core.Artifact",
                related_name="experimental_factors",
            ),
        ),
        migrations.RemoveField(
            model_name="developmentalstage",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="developmentalstage",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactDevelopmentalStage",
                to="lnschema_core.Artifact",
                related_name="developmental_stages",
            ),
        ),
        migrations.RemoveField(
            model_name="ethnicity",
            name="artifacts",
        ),
        migrations.AddField(
            model_name="ethnicity",
            name="artifacts",
            field=models.ManyToManyField(
                through="bionty.ArtifactEthnicity",
                to="lnschema_core.Artifact",
                related_name="ethnicities",
            ),
        ),
    ]

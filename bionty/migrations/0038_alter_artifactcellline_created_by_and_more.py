# Generated by Django 5.2 on 2024-09-09 07:52

import django.db.models.deletion
import lamidb.base.users
import lamindb.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0037_alter_cellline_source_alter_cellmarker_source_and_more"),
        ("lamindb", "0066_alter_artifact__feature_values_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="artifactcellline",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcellline",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcellmarker",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcellmarker",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcelltype",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcelltype",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdevelopmentalstage",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdevelopmentalstage",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdisease",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdisease",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactethnicity",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactethnicity",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactexperimentalfactor",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactexperimentalfactor",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactgene",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactgene",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactorganism",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactorganism",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactpathway",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactpathway",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactphenotype",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactphenotype",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifactprotein",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifactprotein",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="artifacttissue",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="artifacttissue",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="cellline",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="cellline",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="cellmarker",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="cellmarker",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="celltype",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="celltype",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="developmentalstage",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="developmentalstage",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="disease",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="disease",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="ethnicity",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="ethnicity",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="experimentalfactor",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="experimentalfactor",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="gene",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="gene",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="organism",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="organism",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="pathway",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="pathway",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="phenotype",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="phenotype",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="protein",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="protein",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="source",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="source",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
        migrations.AlterField(
            model_name="tissue",
            name="created_by",
            field=models.ForeignKey(
                default=lamidb.base.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.user",
            ),
        ),
        migrations.AlterField(
            model_name="tissue",
            name="run",
            field=models.ForeignKey(
                default=lamindb.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lamindb.run",
            ),
        ),
    ]

# Generated by Django 5.0.6 on 2024-05-19 11:26

import django.db.models.deletion
import django.utils.timezone
import lnschema_core.models
import lnschema_core.users
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0027_remove_artifactcellline_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="artifactcellline",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactcellline",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactcellline",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactcellmarker",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactcellmarker",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactcellmarker",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactcelltype",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactcelltype",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactcelltype",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactdevelopmentalstage",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactdevelopmentalstage",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactdevelopmentalstage",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactdisease",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactdisease",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactdisease",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactethnicity",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactethnicity",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactethnicity",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactexperimentalfactor",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactexperimentalfactor",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactexperimentalfactor",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactgene",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactgene",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactgene",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactorganism",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactorganism",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactorganism",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactpathway",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactpathway",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactpathway",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactphenotype",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactphenotype",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactphenotype",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifactprotein",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifactprotein",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifactprotein",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="artifacttissue",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="artifacttissue",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AddField(
            model_name="artifacttissue",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="cellline",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="cellline",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="cellmarker",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="cellmarker",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="celltype",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="celltype",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="developmentalstage",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="developmentalstage",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="disease",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="disease",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="ethnicity",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="ethnicity",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="experimentalfactor",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="experimentalfactor",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="gene",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="gene",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="organism",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="organism",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="pathway",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="pathway",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="phenotype",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="phenotype",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="protein",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="protein",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="publicsource",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="publicsource",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AddField(
            model_name="tissue",
            name="previous_runs",
            field=models.ManyToManyField(to="lnschema_core.run"),
        ),
        migrations.AddField(
            model_name="tissue",
            name="run",
            field=models.ForeignKey(
                default=lnschema_core.models.current_run,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.run",
            ),
        ),
        migrations.AlterField(
            model_name="cellline",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="cellmarker",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="celltype",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="developmentalstage",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="disease",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="ethnicity",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="experimentalfactor",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="gene",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="organism",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="pathway",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="phenotype",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="protein",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="publicsource",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
        migrations.AlterField(
            model_name="tissue",
            name="created_by",
            field=models.ForeignKey(
                default=lnschema_core.users.current_user_id,
                on_delete=django.db.models.deletion.PROTECT,
                to="lnschema_core.user",
            ),
        ),
    ]

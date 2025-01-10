# Generated by Django 5.2 on 2025-01-07 14:37

import django.db.models.deletion
import lamindb.base.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0041_squashed"),
    ]

    operations = [
        migrations.AddField(
            model_name="cellline",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="cellmarker",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="celltype",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="developmentalstage",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="disease",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="ethnicity",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="experimentalfactor",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="gene",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="organism",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="pathway",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="phenotype",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="protein",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="source",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="tissue",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, default=1, db_default=1),
        ),
        migrations.AddField(
            model_name="cellline",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="cellmarker",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="celltype",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="developmentalstage",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="disease",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="ethnicity",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="experimentalfactor",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="gene",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="organism",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="pathway",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="phenotype",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="protein",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="source",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="tissue",
            name="aux",
            field=models.JSONField(default=None, db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="cellline",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="cellmarker",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="celltype",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="developmentalstage",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="disease",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="ethnicity",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="experimentalfactor",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="gene",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="organism",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="pathway",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="phenotype",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="protein",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="source",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
        migrations.AddField(
            model_name="tissue",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="space",
            ),
        ),
    ]

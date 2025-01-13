# Generated by Django 5.2 on 2025-01-10 23:59

import django.db.models.deletion
import lamindb.base.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0042_lamindbv1"),
    ]

    operations = [
        migrations.AddField(
            model_name="cellline",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="cellmarker",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="celltype",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="developmentalstage",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="disease",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="ethnicity",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="experimentalfactor",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="gene",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="organism",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="pathway",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="phenotype",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="protein",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="source",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
        migrations.AddField(
            model_name="tissue",
            name="space",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="lamindb.space",
            ),
        ),
    ]

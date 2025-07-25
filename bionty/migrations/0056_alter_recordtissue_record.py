# Generated by Django 5.2 on 2025-07-05 15:36

import django.db.models.deletion
import lamindb.base.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0055_rename_cellline_recordcellline_value_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recordtissue",
            name="record",
            field=lamindb.base.fields.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="values_tissue",
                to="lamindb.record",
            ),
        ),
    ]

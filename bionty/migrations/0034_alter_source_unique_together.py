# Generated by Django 5.1 on 2024-08-02 07:53

from django.db import migrations, models

import bionty.ids


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0033_alter_artifactcellline_artifact_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="source", unique_together=(("entity", "name", "organism", "version"),)
        ),
    ]

# Generated by Django 5.2 on 2025-01-07 14:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0041_squashed"),
    ]

    operations = [
        migrations.AddField(
            model_name="cellline",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="cellmarker",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="celltype",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="developmentalstage",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="disease",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="ethnicity",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="experimentalfactor",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="gene",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="organism",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="pathway",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="phenotype",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="protein",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="source",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="tissue",
            name="_branch_code",
            field=models.SmallIntegerField(db_index=True, db_default=1),
        ),
        migrations.AddField(
            model_name="cellline",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="cellmarker",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="celltype",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="developmentalstage",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="disease",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="ethnicity",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="experimentalfactor",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="gene",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="organism",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="pathway",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="phenotype",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="protein",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="source",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
        migrations.AddField(
            model_name="tissue",
            name="aux",
            field=models.JSONField(db_default=None, null=True),
        ),
    ]

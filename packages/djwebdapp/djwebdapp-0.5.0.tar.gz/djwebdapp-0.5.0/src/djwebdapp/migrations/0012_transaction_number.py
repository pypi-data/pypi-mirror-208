# Generated by Django 4.1.1 on 2022-09-23 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djwebdapp", "0011_rename_max_level_blockchain_index_level"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="number",
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]

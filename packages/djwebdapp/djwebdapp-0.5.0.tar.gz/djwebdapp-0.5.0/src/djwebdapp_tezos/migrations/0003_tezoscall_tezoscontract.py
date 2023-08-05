# Generated by Django 4.1.1 on 2023-01-20 16:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("djwebdapp_tezos", "0002_tezostransaction_caller"),
    ]

    operations = [
        migrations.CreateModel(
            name="TezosCall",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("djwebdapp_tezos.tezostransaction",),
        ),
        migrations.CreateModel(
            name="TezosContract",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("djwebdapp_tezos.tezostransaction",),
        ),
    ]

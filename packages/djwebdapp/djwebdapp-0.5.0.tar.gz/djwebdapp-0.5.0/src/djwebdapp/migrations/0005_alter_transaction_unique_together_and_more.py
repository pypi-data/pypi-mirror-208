# Generated by Django 4.0.5 on 2022-06-14 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djwebdapp', '0004_alter_transaction_options'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='transaction',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='transaction',
            name='counter',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='nonce',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterUniqueTogether(
            name='transaction',
            unique_together={('blockchain', 'hash', 'counter', 'nonce')},
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='txgroup',
        ),
    ]

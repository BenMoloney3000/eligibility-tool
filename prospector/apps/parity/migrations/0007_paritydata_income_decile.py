# Generated by Django 3.2.15 on 2024-12-18 15:49
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("parity", "0006_paritydata_tax_band"),
    ]

    operations = [
        migrations.AddField(
            model_name="paritydata",
            name="income_decile",
            field=models.SmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]

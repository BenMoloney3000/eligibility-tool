# Generated by Django 4.0.1 on 2022-06-09 15:10
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0028_add_income_confirmation_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="answers",
            name="has_solar_pv",
            field=models.BooleanField(
                blank=True, null=True, verbose_name="Property has solar PV"
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="has_solar_pv_orig",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Property has solar PV before correction",
            ),
        ),
    ]

# Generated by Django 3.2.15 on 2025-01-06 15:36
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0086_answers_income_decile"),
    ]

    operations = [
        migrations.AddField(
            model_name="answers",
            name="household_income_after_tax",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Household income after tax"
            ),
        ),
    ]

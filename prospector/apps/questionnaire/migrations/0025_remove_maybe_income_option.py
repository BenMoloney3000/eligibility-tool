# Generated by Django 4.0.1 on 2022-03-07 10:57
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0024_add_individual_income_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="answers",
            name="take_home_lt_30k",
            field=models.CharField(
                blank=True,
                choices=[
                    ("YES", "Yes, it's under that figure"),
                    ("NO", "No, it's over that figure"),
                    ("UNKNOWN", "I don't know"),
                ],
                max_length=7,
                verbose_name="Total household take home pay is under £30,000 pa",
            ),
        ),
        migrations.AlterField(
            model_name="answers",
            name="total_income_lt_30k",
            field=models.CharField(
                blank=True,
                choices=[
                    ("YES", "Yes, it's under that figure"),
                    ("NO", "No, it's over that figure"),
                    ("UNKNOWN", "I don't know"),
                ],
                max_length=7,
                verbose_name="Total gross household income is under £30,000 pa",
            ),
        ),
    ]

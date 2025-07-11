# Generated by Django 3.2.15 on 2024-01-22 14:30
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0081_auto_20240109_2110"),
    ]

    operations = [
        migrations.AddField(
            model_name="answers",
            name="council_tax_band",
            field=models.CharField(
                blank=True,
                choices=[
                    ("A", "A"),
                    ("B", "B"),
                    ("C", "C"),
                    ("D", "D"),
                    ("E", "E"),
                    ("F", "F"),
                    ("G", "G"),
                    ("H", "H"),
                ],
                max_length=1,
                null=True,
            ),
        ),
    ]

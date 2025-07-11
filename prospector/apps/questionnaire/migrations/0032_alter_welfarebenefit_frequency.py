# Generated by Django 4.0.1 on 2022-06-17 14:44
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0031_merge_20220617_1544"),
    ]

    operations = [
        migrations.AlterField(
            model_name="welfarebenefit",
            name="frequency",
            field=models.CharField(
                blank=True,
                choices=[
                    ("WEEKLY", "weekly"),
                    ("TWO_WEEKLY", "two weekly"),
                    ("FOUR_WEEKLY", "four weekly"),
                    ("ANNUALLY", "annually"),
                    ("MONTHLY", "monthly"),
                ],
                max_length=12,
            ),
        ),
    ]

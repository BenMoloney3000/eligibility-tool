# Generated by Django 4.0.1 on 2022-06-17 14:08
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0029_answers_has_solar_pv_answers_has_solar_pv_orig"),
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
                    ("ANNUALLY", "annually"),
                    ("MONTHLY", "monthly"),
                ],
                max_length=10,
            ),
        ),
    ]

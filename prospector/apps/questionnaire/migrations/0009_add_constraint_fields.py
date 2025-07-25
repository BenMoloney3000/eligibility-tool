# Generated by Django 4.0.1 on 2022-02-08 14:27
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0008_more_flat_roof_and_ch_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="answers",
            name="in_conservation_area",
            field=models.BooleanField(
                blank=True, null=True, verbose_name="Property is in a conservation area"
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="motivation_better_comfort",
            field=models.BooleanField(
                blank=True, null=True, verbose_name="Motivated by improving comfort"
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="motivation_environment",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Motivated to make the home more environmentally friendly",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="motivation_lower_bills",
            field=models.BooleanField(
                blank=True, null=True, verbose_name="Motivated by reducing bills"
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="tolerated_disruption",
            field=models.CharField(
                blank=True,
                choices=[
                    (
                        "UP_TO_ONE_DAY",
                        "Jobs that take up to three hours inside home, up to one day outside home",
                    ),
                    (
                        "ONE_TO_FOUR_DAYS",
                        "One or two days of work inside home, or three to four days taking place on exterior to property (involving scaffolding etc.)",
                    ),
                    (
                        "THREE_TO_TEN_DAYS",
                        "Up to five days of work inside home, up to ten days outside the home",
                    ),
                    (
                        "TWO_WEEKS_TO_A_MONTH",
                        "Up to two weeks of work inside home, up to one month outside the home",
                    ),
                ],
                max_length=20,
                verbose_name="Maximum length of disruption tolerated",
            ),
        ),
        migrations.AlterField(
            model_name="answers",
            name="smart_thermostat",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Property has a smart thermostat control",
            ),
        ),
    ]

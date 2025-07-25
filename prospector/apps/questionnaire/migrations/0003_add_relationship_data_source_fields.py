# Generated by Django 4.0.1 on 2022-01-27 17:32
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0002_add_respondent_property_details_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="answers",
            name="data_source",
            field=models.CharField(
                blank=True,
                choices=[("EPC", "EPC"), ("HA", "Home Analytics")],
                max_length=10,
                verbose_name="Initial property data source",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="respondent_has_permission",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="answers",
            name="respondent_relationship",
            field=models.CharField(
                blank=True,
                choices=[
                    ("FRIEND", "I am a friend of the occupant"),
                    ("PARENT", "I am a parent of the occupant"),
                    ("CHILD", "I am a child of the occupant"),
                    ("FAMILY", "I am another relative of the occupant"),
                    ("OTHER", "Other"),
                ],
                max_length=6,
                verbose_name="Relationship of responder to occupant",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="respondent_relationship_other",
            field=models.CharField(
                blank=True, max_length=128, verbose_name="'Other' relationship detail"
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="selected_epc",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="answers",
            name="uprn",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]

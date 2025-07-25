# Generated by Django 3.2.15 on 2022-11-11 12:27
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("questionnaire", "0045_auto_20221104_1127"),
    ]

    operations = [
        migrations.CreateModel(
            name="CrmResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "state",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("SUCESS", "Status Success"),
                            ("FAILURE", "Status Failure"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("result", models.JSONField(null=True)),
                (
                    "answers",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="questionnaire.answers",
                    ),
                ),
            ],
        ),
    ]

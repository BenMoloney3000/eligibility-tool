# Generated by Django 3.2.15 on 2023-12-13 11:44
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("questionnaire", "0076_remove_answers_savings"),
    ]

    operations = [
        migrations.AddField(
            model_name="answers",
            name="advice_needed_bills",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Advice needed: respondent's energy bills make them feel anxious",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="advice_needed_from_team",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Advice needed from Energy Advice Team",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="advice_needed_supplier",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Advice needed: issues with supplier, meter or energy debt",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="advice_needed_warm",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Advice needed: respondent struggles to keep their home warm or damp free",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="consented_callback",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Respondent consent to call or email them to offer advice and help",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="consented_future_schemes",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="Respondent consent to contact them in the future when there are relevant grants or programmes",
            ),
        ),
    ]

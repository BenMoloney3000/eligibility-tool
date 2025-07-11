# Generated by Django 4.0.1 on 2022-06-16 11:32
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0029_answers_has_solar_pv_answers_has_solar_pv_orig"),
    ]

    operations = [
        migrations.AddField(
            model_name="answers",
            name="child_benefit_claimant_type",
            field=models.CharField(
                blank=True,
                choices=[("SINGLE", "Single Claimant"), ("JOINT", "Joint Claimant")],
                max_length=10,
                null=True,
                verbose_name="The person receiving child benefit is a single claimant (not member of a couple), or joint claimant.",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="child_benefit_eligibility_complete",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="This is a full account of child benefit eligibility",
            ),
        ),
        migrations.AddField(
            model_name="answers",
            name="child_benefit_number_elsewhere",
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(0, "None"), (1, "1"), (2, "2"), (3, "3"), (4, "4 or more")],
                null=True,
                verbose_name="The number of children that live elsewhere (more than 50%% of the time) and benefits are receivived or paid for.",
            ),
        ),
    ]

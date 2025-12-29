from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0088_alter_udprn_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="answers",
            name="past_means_tested_benefits",
        ),
        migrations.RemoveField(
            model_name="answers",
            name="disability_benefits",
        ),
        migrations.RemoveField(
            model_name="answers",
            name="child_benefit",
        ),
        migrations.RemoveField(
            model_name="answers",
            name="child_benefit_number",
        ),
        migrations.RemoveField(
            model_name="answers",
            name="child_benefit_claimant_type",
        ),
    ]

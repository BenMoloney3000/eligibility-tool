from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0089_remove_legacy_benefit_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="answers",
            name="council_tax_reduction",
        ),
        migrations.RemoveField(
            model_name="answers",
            name="free_school_meals_eligibility",
        ),
    ]

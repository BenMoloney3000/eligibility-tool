from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0087_answers_household_income_after_tax"),
    ]

    operations = [
        migrations.AlterField(
            model_name="answers",
            name="respondent_udprn",
            field=models.CharField(
                blank=True, max_length=12, verbose_name="Respondent UPRN from API"
            ),
        ),
        migrations.AlterField(
            model_name="answers",
            name="property_udprn",
            field=models.CharField(
                blank=True, max_length=12, verbose_name="Property UPRN from API"
            ),
        ),
    ]

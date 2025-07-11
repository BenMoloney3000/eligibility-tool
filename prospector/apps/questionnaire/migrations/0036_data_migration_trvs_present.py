# Generated by Django 4.0.1 on 2022-07-04 12:13
from django.db import migrations

from prospector.apps.questionnaire.enums import TRVsPresent


def bool_to_trv_choice(value):
    if value is True:
        return TRVsPresent("ALL")
    if value is False:
        return TRVsPresent("NONE")
    return None


def migrate_trvs_present(apps, schema_editor):
    Answers = apps.get_model("questionnaire", "Answers")

    for answer in Answers.objects.all():
        answer.trvs_present = bool_to_trv_choice(answer.trvs_present_old)
        answer.trvs_present_orig = bool_to_trv_choice(answer.trvs_present_orig_old)
        answer.save()


class Migration(migrations.Migration):
    dependencies = [
        ("questionnaire", "0035_answers_trvs_present_answers_trvs_present_orig"),
    ]

    operations = [
        migrations.RunPython(migrate_trvs_present),
    ]

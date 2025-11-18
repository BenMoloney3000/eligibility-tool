import csv
import datetime

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import models
from django.utils import timezone

from ...models import Answers


class Command(BaseCommand):
    help = (
        "Dump a CSV of the questionnaire_answers table.\n"
        "Supply a from date using e.g. --from-date=\"2025-11-06 14:11\" \n"
        "--to-date can also be supplied in the same format, or omitted to assume latest entry."
    )

    def add_arguments(self, parser):
        parser.add_argument("--from-date", type=str, required=True)
        parser.add_argument("--to-date", type=str)

    def handle(self, *args, **options):
        try:
            filter_from_date = timezone.make_aware(datetime.datetime.strptime(options['from_date'], "%Y-%m-%d %H:%M"))
            filter_to_date = None
            if options['to_date'] is not None:
                filter_to_date = timezone.make_aware(datetime.datetime.strptime(options['to_date'], "%Y-%m-%d %H:%M"))
        except ValueError:
            raise CommandError('"Invalid date format provided. Format must be "YYYY-MM-DD H24:MM", e.g. "2025-11-06 14:11"')

        print(f"Generating CSV with answers from {filter_from_date} to {'now' if filter_to_date is None else filter_to_date}.")

        if filter_to_date is not None:
            answers = (Answers.objects.filter(created_at__gte=filter_from_date, created_at__lte=filter_to_date).
                       order_by("created_at"))
        else:
            answers = (Answers.objects.filter(created_at__gte=filter_from_date).order_by("created_at"))

        field_names = [field.name for field in Answers._meta.get_fields() if isinstance(field, models.Field)]

        try:
            with open('answers_dump.csv', 'w', newline='') as csv_file:
                dump_writer = csv.writer(csv_file)
                dump_writer.writerow(field_names)
                for answer in answers:
                     dump_writer.writerow([getattr(answer, field_name) for field_name in field_names])

            print('Successfully dumped filtered answers to answers_dump.csv.')

        except Exception as e:
            raise CommandError(str(e))



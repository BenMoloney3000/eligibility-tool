import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from ...models import CrmResult
from prospector.apps.questionnaire.models import Answers


class Command(BaseCommand):
    help = "Upload CrmResult data from CSV"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str)

    def handle(self, *args, **options):
        temp_data = []
        with open(f"{options['file']}") as file:
            reader = csv.reader(file)
            next(reader)  # Skip headers

            for row in reader:
                csv_data = CrmResult()
                csv_data.id = row[0]
                csv_data.answers = Answers.objects.get(id=row[1])
                csv_data.created_at = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                csv_data.state = row[3]
                csv_data.result = row[4]

                temp_data.append(csv_data)

        if len(temp_data) > 0:
            CrmResult.objects.bulk_create(temp_data)

import csv

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ...models import Answers


class Command(BaseCommand):
    help = (
        "Upload deprivation index data from CSV and add it to existing Answers dataset"
    )

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str)

    def handle(self, *args, **options):
        temp_data = []

        with open(f"{options['file']}") as file:
            reader = csv.reader(file)
            next(reader)  # Skip headers
            try:
                for row in reader:
                    items = Answers.objects.filter(property_postcode=row[0])
                    if items:
                        for item in items:
                            item.income_decile = row[2]
                            temp_data.append(item)
            except Exception:
                raise CommandError(f"No data for postcode {row[0]} in dataset")

        if len(temp_data) > 0:
            Answers.objects.bulk_update(
                temp_data,
                ["income_decile"],
                batch_size=500,
            )

import csv

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ...models import ParityData


class Command(BaseCommand):
    help = (
        "Upload deprivation index data from CSV and add it to existing Parity dataset"
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
                    items = ParityData.objects.filter(postcode=row[0])
                    if items:
                        for item in items:
                            item.multiple_deprivation_index = row[1]
                            temp_data.append(item)
            except Exception:
                raise CommandError(f"No data for postcode {row[0]} in dataset")

        if len(temp_data) > 0:
            ParityData.objects.bulk_update(
                temp_data, ["multiple_deprivation_index"], batch_size=500
            )

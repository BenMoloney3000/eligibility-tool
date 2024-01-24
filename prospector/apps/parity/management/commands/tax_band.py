import csv

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ...models import ParityData


class Command(BaseCommand):
    help = (
        "Upload council tax bands data from CSV and add it to existing Parity dataset"
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
                    if len(row[3]) > 1:  # Pass row without valid UPRN value
                        item = ParityData.objects.filter(uprn=row[3]).first()
                        if item:
                            item.tax_band = row[2]
                            temp_data.append(item)

            except Exception:
                raise CommandError("Operation aborted due to data error.")

        if len(temp_data) > 0:
            ParityData.objects.bulk_update(temp_data, ["tax_band"], batch_size=500)

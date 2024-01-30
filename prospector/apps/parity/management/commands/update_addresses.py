from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ...models import ParityData


class Command(BaseCommand):
    help = "Update address lines to match the CRM needs"

    def handle(self, *args, **options):
        temp_data = []
        objects = ParityData.objects.all()

        for object in objects:
            try:
                address_titled = object.address_1.title()

                if "," in address_titled:
                    two_address_lines_list = address_titled.split(",")
                    object.address_1 = two_address_lines_list[0].strip()
                    object.address_2 = two_address_lines_list[1].strip()
                else:
                    object.address_1 = address_titled.strip()

                    if object.address_2 == "PLYMOUTH":
                        object.address_2 = ""
                    elif ", PLYMOUTH" in object.address_2:
                        new_address_2 = object.address_2.replace(", PLYMOUTH", "")
                        object.address_2 = new_address_2.strip().title()
                    else:
                        object.address_2 = object.address_2.strip().title()

                temp_data.append(object)

            except Exception:
                raise CommandError("Internal error while reformatting addresses")

        if len(temp_data) > 0:
            ParityData.objects.bulk_update(
                temp_data, ["address_1", "address_2"], batch_size=500
            )

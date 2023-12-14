import csv

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ...models import ParityData


class Command(BaseCommand):
    help = "Upload Parity data from CSV"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str)

    def handle(self, *args, **options):
        ParityData.objects.all().delete()
        temp_data = []
        with open(f"{options['file']}") as file:
            reader = csv.reader(file)
            next(reader)  # Skip headers

            try:
                for row in reader:
                    csv_data = ParityData()
                    csv_data.org_ref = row[0]
                    csv_data.address_link = row[1]
                    csv_data.googlemaps = row[2]
                    csv_data.address_1 = row[3]
                    csv_data.address_2 = row[4]
                    csv_data.address_3 = row[5]
                    csv_data.postcode = row[6]
                    csv_data.sap_score = row[7]
                    csv_data.sap_band = row[8]
                    csv_data.lodged_epc_score = row[9] or None
                    csv_data.lodged_epc_band = row[10] or None
                    csv_data.tco2_current = row[11]
                    csv_data.realistic_fuel_bill = row[12]
                    csv_data.type = row[13]
                    csv_data.attachment = row[14]
                    csv_data.construction_years = row[15]
                    csv_data.heated_rooms = row[16]
                    csv_data.wall_construction = row[17]
                    csv_data.wall_insulation = row[18]
                    csv_data.floor_construction = row[19]
                    csv_data.floor_insulation = row[20]
                    csv_data.roof_construction = row[21]
                    csv_data.roof_insulation = row[22]
                    csv_data.glazing = row[23]
                    csv_data.heating = row[24]
                    csv_data.boiler_efficiency = row[25]
                    csv_data.main_fuel = row[26]
                    csv_data.controls_adequacy = row[27]
                    csv_data.local_authority = row[28]
                    csv_data.ward = row[29]
                    csv_data.parliamentary_constituency = row[30]
                    csv_data.region_name = row[31]
                    csv_data.tenure = row[32]
                    csv_data.uprn = row[33] or None
                    csv_data.lat_coordinate = row[34] or None
                    csv_data.long_coordinate = row[35] or None
                    csv_data.lower_super_output_area_code = row[36]
                    csv_data.multiple_deprivation_index = 0

                    temp_data.append(csv_data)

            except Exception:
                raise CommandError("An error occured during uploading csv data")

        if len(temp_data) > 0:
            ParityData.objects.bulk_create(temp_data, batch_size=500)

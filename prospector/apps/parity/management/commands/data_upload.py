import csv
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError

from ...models import ParityData


def parse_uprn(value: str) -> str | None:
    """Parse a UPRN from a CSV value.

    The source data sometimes stores UPRNs in scientific notation.  Using
    ``Decimal`` avoids the pitfalls of floating point conversion and ensures we
    preserve the full digit string.  Any fractional part is discarded as UPRNs
    are integer identifiers.

    Args:
        value: Raw value from the CSV.

    Returns:
        The normalised UPRN as a string, or ``None`` if ``value`` is empty.

    Raises:
        CommandError: If ``value`` cannot be parsed as a decimal number.
    """

    if not value:
        return None
    try:
        # ``Decimal`` handles both integer and scientific notation reliably.
        uprn = Decimal(value)
    except InvalidOperation as exc:
        raise CommandError(f"Invalid UPRN: {value}") from exc

    # ``'f'`` formats without exponent. Split on the decimal point and take
    # the integer component to remove any fractional part.
    return format(uprn, "f").split(".")[0]


class Command(BaseCommand):
    help = "Upload Parity data from CSV"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, required=True)

    # ──────────────────────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        ParityData.objects.all().delete()

        temp_data = []
        csv_path = options["file"]
        expected_cols = 48                       # highest index used is 47

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)                    # skip header row

                for idx, row in enumerate(reader, start=2):  # row 2 = first data row
                    if len(row) < expected_cols:
                        raise CommandError(
                            f"Row {idx} too short: {len(row)} columns found, "
                            f"{expected_cols} required"
                        )

                    try:
                        pd = ParityData(
                            org_ref=row[0],
                            address_link=row[1],
                            googlemaps=row[2],
                            address_1=row[3],
                            address_2=row[4],
                            address_3=row[5],
                            postcode=row[6],
                            sap_score=Decimal(row[7] or 0),
                            sap_band=row[8],
                            lodged_epc_score=int(row[9]) if row[9] else None,
                            lodged_epc_band=row[10] or None,
                            tco2_current=Decimal(row[12] or 0),
                            realistic_fuel_bill=row[16],
                            type=row[17],
                            attachment=row[18],
                            construction_years=row[19],
                            heated_rooms=int(row[20] or 0),
                            wall_construction=row[22],
                            wall_insulation=row[23],
                            roof_construction=row[24],
                            roof_insulation=row[25],
                            floor_construction=row[26],
                            floor_insulation=row[27],
                            glazing=row[29],
                            heating=row[30],
                            boiler_efficiency=row[31],
                            main_fuel=row[32],
                            controls_adequacy=row[34],
                            local_authority=row[35],
                            ward=row[36],
                            parliamentary_constituency=row[37],
                            region_name=row[38],
                            tenure=row[39],
                            uprn=parse_uprn(row[40]),
                            lat_coordinate=(
                                Decimal(row[41]) if row[41] else None
                            ),
                            long_coordinate=(
                                Decimal(row[42]) if row[42] else None
                            ),
                            lower_super_output_area_code=row[43],
                            multiple_deprivation_index=int(row[47] or 0),
                            income_decile=int(row[46] or 0),
                        )

                        temp_data.append(pd)

                    except (ValueError, InvalidOperation) as e:
                        raise CommandError(f"Row {idx} value error: {e}")

        except FileNotFoundError:
            raise CommandError(f"CSV file not found: {csv_path}")

        if temp_data:
            ParityData.objects.bulk_create(temp_data, batch_size=500)
            self.stdout.write(
                self.style.SUCCESS(f"Imported {len(temp_data)} rows successfully.")
            )
        else:
            self.stdout.write(self.style.WARNING("No data rows imported."))

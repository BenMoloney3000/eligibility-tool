import csv
import uuid as uuid_lib
from datetime import datetime

from django.core.management.base import BaseCommand

from ...models import Answers


class Command(BaseCommand):
    help = "Upload Answers data from CSV"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str)

    def handle(self, *args, **options):
        temp_data = []
        with open(f"{options['file']}") as file:
            reader = csv.reader(file)
            next(reader)  # Skip headers

            for row in reader:
                csv_data = Answers()
                csv_data.id = row[0]
                csv_data.created_at = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                csv_data.updated_at = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                csv_data.completed_at = (
                    datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S") if row[3] else None
                )
                csv_data.uuid = uuid_lib.uuid4()
                csv_data.terms_accepted_at = (
                    datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S") if row[5] else None
                )
                csv_data.email = row[6]
                csv_data.first_name = row[7]
                csv_data.last_name = row[8]
                csv_data.respondent_role = row[9]
                csv_data.respondent_role_other = row[10]
                csv_data.respondent_address_1 = row[11]
                csv_data.respondent_address_2 = row[12]
                csv_data.respondent_address_3 = row[13]
                csv_data.respondent_udprn = row[14]
                csv_data.respondent_postcode = row[15]
                csv_data.contact_phone = row[16]
                csv_data.contact_mobile = row[17]
                csv_data.occupant_first_name = row[18]
                csv_data.occupant_last_name = row[19]
                csv_data.property_address_1 = row[20]
                csv_data.property_address_2 = row[21]
                csv_data.property_address_3 = row[22]
                csv_data.property_postcode = row[23]
                csv_data.property_udprn = row[24]
                csv_data.property_ownership = row[25]
                csv_data.uprn = row[26] or None
                csv_data.respondent_has_permission = row[27]
                csv_data.selected_epc = row[28]
                csv_data.sap_rating = row[29] or None
                csv_data.data_source = row[30]
                csv_data.property_type = row[31]
                csv_data.property_type_orig = row[32]
                csv_data.property_form = row[33]
                csv_data.property_form_orig = row[34]
                csv_data.property_age_band = row[35]
                csv_data.property_age_band_orig = row[36]
                csv_data.wall_type = row[37]
                csv_data.wall_type_orig = row[38]
                csv_data.walls_insulated = row[39]
                csv_data.walls_insulated_orig = row[40]
                csv_data.suspended_floor = row[41]
                csv_data.suspended_floor_orig = row[42]
                csv_data.suspended_floor_insulated = row[43]
                csv_data.suspended_floor_insulated_orig = row[44]
                csv_data.unheated_loft = row[45]
                csv_data.unheated_loft_orig = row[46]
                csv_data.room_in_roof = row[47]
                csv_data.room_in_roof_orig = row[48]
                csv_data.rir_insulated = row[49]
                csv_data.rir_insulated_orig = row[50]
                csv_data.roof_space_insulated = row[51]
                csv_data.roof_space_insulated_orig = row[52]
                csv_data.flat_roof = row[53]
                csv_data.flat_roof_orig = row[54]
                csv_data.flat_roof_insulated = row[55]
                csv_data.gas_boiler_present = row[56]
                csv_data.gas_boiler_present_orig = row[57]
                csv_data.gas_boiler_age = row[58]
                csv_data.gas_boiler_broken = row[59]
                csv_data.on_mains_gas = row[60]
                csv_data.on_mains_gas_orig = row[61]
                csv_data.other_heating_present = row[62]
                csv_data.other_heating_present_orig = row[63]
                csv_data.heat_pump_present = row[64]
                csv_data.heat_pump_present_orig = row[65]
                csv_data.other_heating_fuel = row[66]
                csv_data.other_heating_fuel_orig = row[67]
                csv_data.storage_heaters_present = row[68]
                csv_data.storage_heaters_present_orig = row[69]
                csv_data.hhrshs_present = row[70]
                csv_data.hhrshs_present_orig = row[71]
                csv_data.electric_radiators_present = row[72]
                csv_data.electric_radiators_present_orig = row[73]
                csv_data.hwt_present = row[74]
                csv_data.trvs_present_old = row[75]
                csv_data.trvs_present_orig_old = row[76]
                csv_data.trvs_present = row[77]
                csv_data.trvs_present_orig = row[78]
                csv_data.room_thermostat = row[79]
                csv_data.room_thermostat_orig = row[80]
                csv_data.ch_timer = row[81]
                csv_data.ch_timer_orig = row[82]
                csv_data.programmable_thermostat = row[83]
                csv_data.programmable_thermostat_orig = row[84]
                csv_data.smart_thermostat = row[85]
                csv_data.has_solar_pv = row[86]
                csv_data.has_solar_pv_orig = row[87]
                csv_data.will_correct_type = row[88]
                csv_data.will_correct_walls = row[89]
                csv_data.will_correct_roof = row[90]
                csv_data.will_correct_floor = row[91]
                csv_data.will_correct_heating = row[92]
                csv_data.tolerated_disruption = row[93]
                csv_data.state_of_repair = row[94]
                csv_data.motivation_better_comfort = row[95]
                csv_data.motivation_lower_bills = row[96]
                csv_data.motivation_environment = row[97]
                csv_data.motivation_unknown = row[98]
                csv_data.contribution_capacity = row[99]
                csv_data.consented_callback = row[100]
                csv_data.consented_future_schemes = row[101]
                csv_data.adults = row[102] or None
                csv_data.children = row[103] or None
                csv_data.total_income_lt_31k = row[104]
                csv_data.take_home_lt_31k = row[105]
                csv_data.disability_benefits = row[106]
                csv_data.child_benefit = row[107]
                csv_data.child_benefit_number = row[108] or None
                csv_data.child_benefit_claimant_type = row[109]
                csv_data.child_benefit_eligibility_complete = row[110]
                csv_data.child_benefit_threshold = row[111] or None
                csv_data.income_lt_child_benefit_threshold = row[112]
                csv_data.vulnerable_cariovascular = row[113]
                csv_data.vulnerable_respiratory = row[114]
                csv_data.vulnerable_mental_health = row[115]
                csv_data.vulnerable_cns = row[116]
                csv_data.vulnerable_disability = row[117]
                csv_data.vulnerable_age = row[118]
                csv_data.vulnerable_child_pregnancy = row[119]
                csv_data.incomes_complete = row[120]
                csv_data.take_home_lt_31k_confirmation = row[121]
                csv_data.income_rating = row[122]
                csv_data.property_rating = row[123]

                temp_data.append(csv_data)

        if len(temp_data) > 0:
            Answers.objects.bulk_create(temp_data)

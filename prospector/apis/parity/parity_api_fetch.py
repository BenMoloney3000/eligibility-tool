import csv
import json
import logging
import os
import re
import urllib.parse
from decimal import Decimal
from pathlib import Path
import pydash
import requests
from django.conf import settings
from prospector.apis.parity import ParityData
from prospector.apps.parity.models import ParityData as ParityDataModel

def get_for_uprn(uprn, output_results=False):

    logger = logging.getLogger(__name__)

    try:
        access_token = get_access_token(settings.PORTFOLIOS_API_ID, settings.PORTFOLIOS_API_SECRET)
        address_id = get_address_id(access_token, uprn)
        characteristics = get_characteristics(access_token, address_id)
        results = get_results(access_token, address_id)
        lodged_data = get_lodged_data_from_results(results)
        rdsap_data = get_rdsap(access_token, address_id)
        postcodes_io_data = get_data_from_postcodes_io(pydash.get(rdsap_data, 'address.postcode'))
        imd_deciles = get_deciles(pydash.get(postcodes_io_data, 'codes.lsoa'))

        # Dump these results into files for inspection if in output_results mode:
        if output_results:
            comparisons_dir = os.path.join(settings.SRC_DIR, 'apps', 'parity', 'management', 'commands',
                                           'comparisons', str(uprn))
            Path(comparisons_dir).mkdir(parents=True, exist_ok=True)

            with open(os.path.join(comparisons_dir, 'characteristics.json'), 'w') as json_file:
                json.dump(characteristics, json_file)

            with open(os.path.join(comparisons_dir, 'results.json'), 'w') as json_file:
                json.dump(results, json_file)

            with open(os.path.join(comparisons_dir, 'lodged_data.json'), 'w') as json_file:
                json.dump(lodged_data, json_file)

            with open(os.path.join(comparisons_dir, 'rdsap_data.json'), 'w') as json_file:
                json.dump(rdsap_data, json_file)

            with open(os.path.join(comparisons_dir, 'postcodes_io_data.json'), 'w') as json_file:
                json.dump(postcodes_io_data, json_file)

            with open(os.path.join(comparisons_dir, 'imd_deciles.json'), 'w') as json_file:
                json.dump(imd_deciles, json_file)

        pd = ParityData(
            id=address_id,
            org_ref=uprn,
            address_link=f"https://crohm.parityprojects.com/Address/Details/{address_id}",
            googlemaps=f"https://maps.google.com/maps?q={urllib.parse.quote_plus(pydash.get(rdsap_data, 'address.line1', "") +
                                                                                 ' ' + pydash.get(rdsap_data, 'address.postcode', ""))}",
            address_1=pydash.get(rdsap_data, 'address.line1', ""),
            address_2=pydash.get(rdsap_data, 'address.line2', ""),
            address_3=pydash.get(rdsap_data, 'address.line3', ""),
            postcode=pydash.get(rdsap_data, 'address.postcode', ""),
            sap_score=pydash.get(rdsap_data, 'calculationsFromParity.sapScore', 0),
            sap_band=map_sap_score_to_band(pydash.get(rdsap_data, 'calculationsFromParity.sapScore', 0)),
            lodged_epc_score=lodged_data['lodged_epc_score'],
            lodged_epc_band=lodged_data['lodged_epc_band'],
            tco2_current=get_tco2_current_from_results(results),
            realistic_fuel_bill=get_fuel_bill_from_results(results),
            type=pydash.get(rdsap_data, 'propertyType.description'),
            attachment=pydash.get(rdsap_data, 'builtForm.description'),
            construction_years=map_age_band_to_period(pydash.get(rdsap_data, 'buildingParts[0].constructionAgeBand.description')),
            heated_rooms=int(rdsap_data['heatedRoomCount'] or 0),
            wall_construction=pydash.get(rdsap_data, 'buildingParts[0].wall.construction.description', ""),
            wall_insulation=pydash.get(rdsap_data, 'buildingParts[0].wall.insulationType.description', ""),
            roof_construction=pydash.get(rdsap_data, 'buildingParts[0].roof.construction.description', ""),
            roof_insulation=pydash.get(rdsap_data, 'buildingParts[0].roof.insulationThickness.description', "Unknown"),
            floor_construction=pydash.get(rdsap_data, 'buildingParts[0].floor.construction.description', ""),
            floor_insulation=pydash.get(rdsap_data, 'buildingParts[0].floor.insulation.description', ""),
            glazing=pydash.get(rdsap_data, 'glazing.multipleGlazingType.description', ""),
            heating=pydash.get(rdsap_data, 'heating.mainDetails[0].category.description', ""),
            boiler_efficiency=get_boiler_efficiency_from_characteristics(characteristics),
            main_fuel=pydash.get(rdsap_data, 'heating.mainDetails[0].fuelType.description', ""),
            heating_controls_detail=pydash.get(rdsap_data, "heating.mainDetails[0].control.description", "Unknown"),
            local_authority=postcodes_io_data['bua'] or None,
            ward=postcodes_io_data['admin_ward'] or None,
            parliamentary_constituency=pydash.get(postcodes_io_data, 'codes.parliamentary_constituency'),
            region_name=postcodes_io_data['region'] or None,
            tenure=pydash.get(rdsap_data, 'tenure.description', ""),
            uprn=uprn,
            lat_coordinate=float(round(postcodes_io_data['latitude'], 6)) if postcodes_io_data['latitude'] else None,
            long_coordinate=float(round(postcodes_io_data['longitude'], 6)) if postcodes_io_data['longitude'] else None,
            lower_super_output_area_code=pydash.get(postcodes_io_data, 'codes.lsoa'),
            multiple_deprivation_index=int(pydash.get(imd_deciles, 'IMD_Decile') or 0),
            income_decile=int(pydash.get(imd_deciles, 'IncDec') or 0),
        )

        if output_results:

            parity_object = ParityDataModel.objects.filter(uprn=uprn).first()
            if parity_object is not None:
                with open(os.path.join(comparisons_dir, 'result_comparison.csv'), 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',')
                    csv_writer.writerow(['Field', 'Spreadsheet', 'API result', 'Different?'])
                    for field in parity_object._meta.get_fields():
                        spreadsheet_field = getattr(parity_object, field.name) or ''
                        try:
                            api_result_field = getattr(pd, field.name) or ''
                        except Exception:
                            api_result_field = 'Not present'

                        diff = ' '
                        if spreadsheet_field != api_result_field:
                            diff = ' <<<<<'
                        csv_writer.writerow([field.name, spreadsheet_field, api_result_field, diff])

        return pd

    except Exception as e:
        logger.error(f"Failed to fetch parity data via API, falling back to database lookup. Error: {e}")
        return None


def get_access_token(client_id, client_secret):
    payload = {
        "id": client_id,
        "secret": client_secret,
    }
    response = requests.post(
        settings.PORTFOLIOS_API_BASE_URL + 'token',
        json=payload,
        headers={"Accept": "text/plain"},
    )
    return response.text


def get_address_id(access_token, uprn):
    response = requests.get(
        settings.PORTFOLIOS_API_BASE_URL + 'addresses/organisationreference/' + uprn,
        headers={'Authorization': 'Bearer ' + access_token},
    )
    return response.text


def get_characteristics(access_token, address_id):
    response = requests.get(
        settings.PORTFOLIOS_API_BASE_URL + 'characteristics/' + str(address_id),
        headers={'Authorization': 'Bearer ' + access_token},
    )
    return response.json()


def get_results(access_token, address_id):
    response = requests.post(
        settings.PORTFOLIOS_API_BASE_URL + 'results/' + str(address_id),
        json={},
        headers={'Authorization': 'Bearer ' + access_token},
    )
    return response.json()


def get_rdsap(access_token, address_id):
    response = requests.get(
        settings.PORTFOLIOS_API_BASE_URL + 'rdsapdata/' + str(address_id),
        headers={'Authorization': 'Bearer ' + access_token},
    )
    return response.json()


def get_data_from_postcodes_io(postcode):
    if postcode is None:
        raise ValueError("postcode cannot be None")
    response = requests.get(settings.POSTCODES_IO_API_BASE_URL + postcode)
    data = response.json()
    return data['result']


def get_deciles(lsoa):
    response = requests.get(settings.IMD_DECILES_API_BASE_URL + f"'{lsoa}'")
    data = response.json()
    return data['features'][0]['attributes']


def map_age_band_to_period(age_band):
    mapping = {
        "A": "Before 1900",
        "B": "1900-1929",
        "C": "1930-1949",
        "D": "1950-1966",
        "E": "1967-1975",
        "F": "1976-1982",
        "G": "1983-1990",
        "H": "1991-1995",
        "I": "1996-2002",
        "J": "2003-2006",
        "K": "2007-2011",
        "L": "2012 onwards",
    }
    return mapping[age_band]


def map_sap_score_to_band(sap_score):
    mappings = {
        "A": [92, 100],
        "B": [81, 91],
        "C": [69, 80],
        "D": [55, 68],
        "E": [39, 54],
        "F": [21, 38],
        "G": [1, 20],
    }
    for mapping in mappings:
        min_score = mappings[mapping][0]
        max_score = mappings[mapping][1]
        if sap_score >= min_score and sap_score <= max_score:
            return mapping

    return "Unknown"


def get_boiler_efficiency_from_characteristics(characteristics):
    """
    Extract the rating letter from the heating characteristic that looks like "Boiler: E rated Regular Boiler".
    """
    try:
        for metric in characteristics['metrics']:
            if metric['key'] == 'heating' and 'boiler' in metric['value'].lower():
                search = re.search(r':\s+([A-G])\+*\s+rated', metric['value'])
                if search is not None:
                    return search.group(1)
    except KeyError:
        pass

    return 'A'


def get_lodged_data_from_results(results):
    lodged_data = {
        "lodged_epc_score": 0,
        "lodged_epc_band": '',
    }
    try:
        for metric in results['metrics']:
            if metric['key'] == 'lodged-data':
                for lodged_metric in metric['value']:
                    if lodged_metric['key'] == 'sap-score':
                        lodged_data['lodged_epc_score'] = lodged_metric['value']
                    if lodged_metric['key'] == 'sap-rating':
                        lodged_data['lodged_epc_band'] = lodged_metric['value']
    except KeyError:
        pass

    return lodged_data


def get_tco2_current_from_results(results):
    """
    Extract the current t-co2 value (hard coded for 2025 - may need periodic updating)
    """
    tco2_current = 0
    try:
        for metric in results['metrics']:
            if str(metric['key']) == 't-co2-2025':
                tco2_current = Decimal(metric['value'])
                tco2_current = round(tco2_current, 1)
    except Exception:
        pass

    return tco2_current


def get_fuel_bill_from_results(results):
    fuel_bill = 0
    try:
        for metric in results['metrics']:
            if str(metric['key']) == 'fuel-bill':
                fuel_bill = metric['value']
    except KeyError:
        pass
    return f"£{round(fuel_bill,2)}"

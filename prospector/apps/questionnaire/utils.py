import csv
import logging
import random
import os

from django.core.management.base import CommandError

from . import enums

logger = logging.getLogger(__name__)


def generate_id():
    """
    Generate string to be utilised as the short UUID-like value.

    Composed from 5 uppercase letters and 5 numbers.
    """

    id_string = ""
    chars = "ABCDEFGHIJKLMNPQRSTUVWXYZ123456789"
    for i in range(10):
        if i < 5:
            index = random.randint(0, 24)
            id_string += chars[index]
        else:
            index = random.randint(25, len(chars) - 1)
            id_string += chars[index]

    return "".join(random.sample(id_string, len(id_string)))


def get_disruption(measure: enums.PossibleMeasures) -> str:
    if measure in [
        enums.PossibleMeasures.HEAT_PUMP_INSTALLATION,
        enums.PossibleMeasures.SOLID_WALL_INSULATION,
    ]:
        return "High"
    elif measure in [
        enums.PossibleMeasures.RIR_INSULATION,
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
        enums.PossibleMeasures.BOILER_UPGRADE,
    ]:
        return "Medium"
    else:
        return "Low"


def get_comfort_benefit(measure: enums.PossibleMeasures) -> str:
    if measure in [
        enums.PossibleMeasures.CAVITY_WALL_INSULATION,
        enums.PossibleMeasures.SOLID_WALL_INSULATION,
        enums.PossibleMeasures.RIR_INSULATION,
        enums.PossibleMeasures.LOFT_INSULATION,
    ]:
        return "High"
    elif measure in [
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
        enums.PossibleMeasures.HEAT_PUMP_INSTALLATION,
    ]:
        return "Medium"
    else:
        return "Low"


def get_bill_impact(measure: enums.PossibleMeasures) -> str:
    if measure in [
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
        enums.PossibleMeasures.BATTERY_STORAGE,
        enums.PossibleMeasures.HEATING_CONTROLS,
    ]:
        return "Medium"
    else:
        return "High"


def get_whlg_eligible_postcodes():
    path = "external_data/WHLG-eligible-postcodes.csv"
    
    if not os.path.exists(path):
        print("⚠️ Skipping postcode loading: file not found")
        return []

    postcodes = []
    with open(path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                postcodes.append(row[0])
            except Exception:
                raise CommandError("Operation aborted due to data error.")
    return postcodes
import logging
import random
from typing import List

from . import enums
from . import models

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
            index = random.randint(0, 25)
            id_string += chars[index]
        else:
            index = random.randint(25, len(chars) - 1)
            id_string += chars[index]

    return "".join(random.sample(id_string, len(id_string)))


def determine_recommended_measures(
    answers: models.Answers,
) -> List[enums.PossibleMeasures]:
    measures = []

    if answers.is_cavity_wall_insulation_recommended:
        measures.append(enums.PossibleMeasures.CAVITY_WALL_INSULATION)

    if answers.is_solid_wall_insulation_recommended:
        measures.append(enums.PossibleMeasures.SOLID_WALL_INSULATION)

    if answers.is_underfloor_insulation_recommended:
        measures.append(enums.PossibleMeasures.UNDERFLOOR_INSULATION)

    if answers.is_loft_insulation_recommended:
        measures.append(enums.PossibleMeasures.LOFT_INSULATION)

    if answers.is_rir_insulation_recommended:
        measures.append(enums.PossibleMeasures.RIR_INSULATION)

    if answers.is_boiler_upgrade_recommended:
        measures.append(enums.PossibleMeasures.BOILER_UPGRADE)

    if answers.is_heatpump_installation_recommended:
        measures.append(enums.PossibleMeasures.HEAT_PUMP_INSTALLATION)

    if answers.is_solar_pv_installation_recommended:
        measures.append(enums.PossibleMeasures.SOLAR_PV_INSTALLATION)

    return measures


def get_child_benefit_threshold(answers: models.Answers) -> int:
    total_qualifying = answers.child_benefit_number

    if (
        answers.child_benefit_claimant_type
        == enums.ChildBenefitClaimantType.SINGLE.value
    ):
        if total_qualifying < 2:
            return 18500
        elif total_qualifying == 2:
            return 23000
        elif total_qualifying == 3:
            return 27500
        else:
            return 32000
    elif (
        answers.child_benefit_claimant_type
        == enums.ChildBenefitClaimantType.JOINT.value
    ):
        if total_qualifying < 2:
            return 25500
        elif total_qualifying == 2:
            return 30000
        elif total_qualifying == 3:
            return 34500
        else:
            return 39000


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
    ]:
        return "Medium"
    else:
        return "High"

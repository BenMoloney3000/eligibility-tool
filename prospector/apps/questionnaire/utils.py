import logging
from typing import List

from . import enums
from . import models


logger = logging.getLogger(__name__)


def determine_recommended_measures(
    answers: models.Answers,
) -> List[enums.PossibleMeasures]:
    # From logic by JB in "Copy of SWEH Tool Rag Rating.xlsx" supplied 2022-03-03
    measures = []

    if answers.wall_type == enums.WallType.CAVITY and answers.walls_insulated is False:
        measures.append(enums.PossibleMeasures.CAVITY_WALL_INSULATION)

    if answers.unheated_loft is True and answers.roof_space_insulated is False:
        measures.append(enums.PossibleMeasures.LOFT_INSULATION)

    party_walled_forms = [
        enums.PropertyForm.SEMI_DETACHED,
        enums.PropertyForm.MID_TERRACE,
        enums.PropertyForm.END_TERRACE,
    ]
    if (
        answers.wall_type == enums.WallType.CAVITY
        and answers.property_form in party_walled_forms
    ):
        measures.append(enums.PossibleMeasures.PARTY_WALL_INSULATION)

    if answers.suspended_floor is True and answers.suspended_floor_insulated is False:
        measures.append(enums.PossibleMeasures.UNDERFLOOR_INSULATION)

    if answers.wall_type == enums.WallType.SOLID and answers.walls_insulated is False:
        measures.append(enums.PossibleMeasures.SOLID_WALL_INSULATION)

    if answers.room_in_roof is True and answers.rir_insulated is False:
        measures.append(enums.PossibleMeasures.RIR_INSULATION)

    if answers.flat_roof is True and answers.flat_roof_insulated in [
        enums.InsulationConfidence.PROBABLY_NOT.value,
        enums.InsulationConfidence.DEFINITELY_NOT.value,
    ]:
        measures.append(enums.PossibleMeasures.FLAT_ROOF_INSULATION)

    if (
        answers.gas_boiler_present is True
        and answers.gas_boiler_age == enums.BoilerAgeBand.BEFORE_2004
    ):
        measures.append(enums.PossibleMeasures.BOILER_UPGRADE)

    if answers.gas_boiler_present and answers.gas_boiler_broken:
        measures.append(enums.PossibleMeasures.BROKEN_BOILER_UPGRADE)

    if answers.storage_heaters_present is True and answers.hhrshs_present is False:
        measures.append(enums.PossibleMeasures.STORAGE_HEATER_UPGRADE)

    if answers.gas_boiler_present is False and answers.other_heating_present is False:
        measures.append(enums.PossibleMeasures.CENTRAL_HEATING_INSTALL)
        measures.append(enums.PossibleMeasures.HEAT_PUMP_INSTALL)

    return measures


def get_child_benefit_threshold(answers: models.Answers) -> int:
    if answers.adults == 1:
        if answers.children < 2:
            return 18500
        elif answers.children == 2:
            return 23000
        elif answers.children == 3:
            return 27500
        else:
            return 32000
    else:
        if answers.children < 2:
            return 25500
        elif answers.children == 2:
            return 30000
        elif answers.children == 3:
            return 34500
        else:
            return 39000


def get_disruption(measure: enums.PossibleMeasures) -> str:
    if measure in [
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
        enums.PossibleMeasures.SOLID_WALL_INSULATION,
        enums.PossibleMeasures.FLAT_ROOF_INSULATION,
    ]:
        return "High"
    elif measure in [
        enums.PossibleMeasures.RIR_INSULATION,
        enums.PossibleMeasures.CENTRAL_HEATING_INSTALL,
        enums.PossibleMeasures.HEAT_PUMP_INSTALL,
    ]:
        return "Medium"
    else:
        return "Low"


def get_comfort_benefit(measure: enums.PossibleMeasures) -> str:
    if measure in [
        enums.PossibleMeasures.CAVITY_WALL_INSULATION,
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
        enums.PossibleMeasures.SOLID_WALL_INSULATION,
        enums.PossibleMeasures.BROKEN_BOILER_UPGRADE,
    ]:
        return "High"
    elif measure in [
        enums.PossibleMeasures.LOFT_INSULATION,
        enums.PossibleMeasures.PARTY_WALL_INSULATION,
        enums.PossibleMeasures.RIR_INSULATION,
        enums.PossibleMeasures.FLAT_ROOF_INSULATION,
    ]:
        return "Medium"
    else:
        return "Low"


def get_bill_impact(measure: enums.PossibleMeasures) -> str:
    if measure in [
        enums.PossibleMeasures.PARTY_WALL_INSULATION,
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
        enums.PossibleMeasures.BROKEN_BOILER_UPGRADE,
    ]:
        return "Low"
    elif measure in [
        enums.PossibleMeasures.LOFT_INSULATION,
        enums.PossibleMeasures.RIR_INSULATION,
        enums.PossibleMeasures.FLAT_ROOF_INSULATION,
    ]:
        return "Medium"
    else:
        return "High"


def get_funding_likelihood(measure: enums.PossibleMeasures) -> str:
    if measure in [
        enums.PossibleMeasures.CAVITY_WALL_INSULATION,
        enums.PossibleMeasures.LOFT_INSULATION,
        enums.PossibleMeasures.PARTY_WALL_INSULATION,
    ]:
        return "High"
    elif measure in [
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
        enums.PossibleMeasures.SOLID_WALL_INSULATION,
        enums.PossibleMeasures.RIR_INSULATION,
        enums.PossibleMeasures.BROKEN_BOILER_UPGRADE,
        enums.PossibleMeasures.STORAGE_HEATER_UPGRADE,
        enums.PossibleMeasures.HEAT_PUMP_INSTALL,
    ]:
        return "Medium"
    else:
        return "Low"

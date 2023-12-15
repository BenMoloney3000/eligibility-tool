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

    if (
        answers.wall_construction == enums.WallConstruction.CAVITY
        and answers.walls_insulation == enums.WallInsulation.AS_BUILT
    ):
        measures.append(enums.PossibleMeasures.CAVITY_WALL_INSULATION)

    solid_walls = [
        enums.WallConstruction.GRANITE,
        enums.WallConstruction.SANDSTONE,
        enums.WallConstruction.SOLID_BRICK,
        enums.WallConstruction.SYSTEM,
    ]

    if (
        answers.floor_construction in solid_walls
        and answers.walls_insulation == enums.WallInsulation.AS_BUILT
    ):
        measures.append(enums.PossibleMeasures.SOLID_WALL_INSULATION)

    floor_insulation_options = [
        enums.FloorInsulation.AS_BUILT,
        enums.FloorInsulation.UNKNOWN,
    ]

    if (
        answers.floor_construction == enums.FloorConstruction.ST
        and answers.floor_insulation in floor_insulation_options
    ):
        measures.append(enums.PossibleMeasures.UNDERFLOOR_INSULATION)

    roof_construction_for_ri = [
        enums.RoofConstruction.PNLA,
        enums.RoofConstruction.PNNLA,
    ]

    roof_insulation_for_ri = [
        enums.RoofInsulation.MM_100,
        enums.RoofInsulation.MM_12,
        enums.RoofInsulation.MM_150,
        enums.RoofInsulation.MM_25,
        enums.RoofInsulation.MM_50,
        enums.RoofInsulation.MM_75,
        enums.RoofInsulation.NO_INSULATION,
    ]

    if (
        answers.roof_construction in roof_construction_for_ri
        and answers.roof_insulation in roof_insulation_for_ri
    ):
        measures.append(enums.PossibleMeasures.LOFT_INSULATION)

    roof_insulation_for_rir = [
        enums.RoofInsulation.AS_BUILD,
        enums.RoofInsulation.MM_12,
        enums.RoofInsulation.MM_25,
        enums.RoofInsulation.MM_50,
        enums.RoofInsulation.MM_75,
        enums.RoofInsulation.NO_INSULATION,
    ]

    if (
        answers.roof_insulation in roof_insulation_for_rir
        and answers.roof_construction == enums.RoofConstruction.PWSC
    ):
        measures.append(enums.PossibleMeasures.RIR_INSULATION)

    main_fuel_for_bu = [
        enums.MainFuel.MGC,
        enums.MainFuel.MGNC,
    ]

    boiler_efficiency_for_bu = [
        enums.EfficiencyBand.C,
        enums.EfficiencyBand.D,
        enums.EfficiencyBand.E,
        enums.EfficiencyBand.F,
        enums.EfficiencyBand.G,
    ]

    if (
        answers.main_fuel in main_fuel_for_bu
        and answers.boiler_efficiency in boiler_efficiency_for_bu
        and answers.heating == enums.Heating.BOILERS
    ):
        measures.append(enums.PossibleMeasures.BOILER_UPGRADE)

    fuel_1_for_hpi = [
        enums.MainFuel.ANTHRACITE,
        enums.MainFuel.GBLPG,
        enums.MainFuel.HCNC,
        enums.MainFuel.LPGC,
        enums.MainFuel.LPGNC,
        enums.MainFuel.LPGSC,
        enums.MainFuel.OC,
        enums.MainFuel.ONC,
        enums.MainFuel.SC,
    ]

    fuel_2_for_hpi = [
        enums.MainFuel.EC,
        enums.MainFuel.ENC,
    ]

    heating_for_hpi = [
        enums.Heating.BOILERS,
        enums.Heating.EUF,
        enums.Heating.OTHER,
        enums.Heating.RH,
        enums.Heating.SH,
        enums.Heating.AIR,
    ]

    if answers.main_fuel in fuel_1_for_hpi or (
        answers.main_fuel in fuel_2_for_hpi and answers.heating in heating_for_hpi
    ):
        measures.append(enums.PossibleMeasures.HEAT_PUMP_INSTALLATION)

    roof_for_PV = [
        enums.RoofConstruction.PNLA,
        enums.RoofConstruction.PNNLA,
        enums.RoofConstruction.PWSC,
    ]

    if answers.floor_construction in roof_for_PV:
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

import logging
import random
from typing import List

from . import enums
from . import models

logger = logging.getLogger(__name__)


def generate_id():
    """
    Generate string to be utilised as the "uuid" value.

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

    if answers.child_benefit_claimant_type == enums.ChildBenefitClaimantType.SINGLE:
        if total_qualifying < 2:
            return 18500
        elif total_qualifying == 2:
            return 23000
        elif total_qualifying == 3:
            return 27500
        else:
            return 32000
    elif answers.child_benefit_claimant_type == enums.ChildBenefitClaimantType.JOINT:
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
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
        enums.PossibleMeasures.SOLID_WALL_INSULATION,
    ]:
        return "High"
    elif measure in [
        enums.PossibleMeasures.RIR_INSULATION,
        enums.PossibleMeasures.HEAT_PUMP_INSTALLATION,
    ]:
        return "Medium"
    else:
        return "Low"


def get_comfort_benefit(measure: enums.PossibleMeasures) -> str:
    if measure in [
        enums.PossibleMeasures.CAVITY_WALL_INSULATION,
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
        enums.PossibleMeasures.SOLID_WALL_INSULATION,
    ]:
        return "High"
    elif measure in [
        enums.PossibleMeasures.LOFT_INSULATION,
        enums.PossibleMeasures.RIR_INSULATION,
    ]:
        return "Medium"
    else:
        return "Low"


def get_bill_impact(measure: enums.PossibleMeasures) -> str:
    if measure in [
        enums.PossibleMeasures.UNDERFLOOR_INSULATION,
    ]:
        return "Low"
    elif measure in [
        enums.PossibleMeasures.LOFT_INSULATION,
        enums.PossibleMeasures.RIR_INSULATION,
    ]:
        return "Medium"
    else:
        return "High"


def get_property_rating(answers: models.Answers) -> enums.RAYG:
    """Property rating.

    Can only be RED / AMBER / GREEN.
    """

    if answers.sap_score:
        # Based on having an EPC result
        if answers.sap_score >= 65:
            # Property unlikely to be eligible for free or discounted schemes
            return enums.RAYG.RED
        elif answers.sap_score >= 50:
            # Property eligible for some free or discounted schemes
            return enums.RAYG.AMBER
        else:
            # Property eligible for free or discounted schemes
            return enums.RAYG.GREEN


def get_income_rating(answers: models.Answers) -> enums.RAYG:
    # Household income rating
    if answers.total_income == enums.IncomeIsUnderThreshold.YES:
        # Gross household income below £31k therefore the Household is eligible
        # for free or discounted schemes (based on info given).
        income_rating = enums.RAYG.GREEN
    else:
        # Gross household income more than £31k, but may still be eligible for
        # some free or discounted schemes (based on info given)
        benefit_qualifies = answers.disability_benefits or (
            answers.child_benefit and answers.income_lt_child_benefit_threshold
        )
        if benefit_qualifies:
            income_rating = enums.RAYG.YELLOW
        else:
            if answers.take_home == enums.IncomeIsUnderThreshold.NO:
                income_rating = enums.RAYG.RED
            else:
                # Household take home pay below £31k.
                income_rating = enums.RAYG.AMBER

    return income_rating


def get_overall_rating(answers: models.Answers) -> enums.RAYG:
    """Determine the application rating.

    Used to decide the path taken for the final section of questions and the
    text shown to the user.

        Overall rating for a EPC rating (has a sap_rating):

            Green (Ig,Pg)
            Amber (Ig,Pa)
            Red (Ia|g,Pr)

            Amber (Ia,Pg)
            Amber (Ia,Pa)
            Red (Ia|g,Pr)

            Red (Ir,Pa|g)
            Red (Ir,Pa|g)
            Red (Ir,Pr)

        Overall rating for no sap score:

            Green2
            Amber2 (Ig,Pa)
            Red (Ia|g,Pr)

            Amber2 (Ia,Pg)
            Amber2 (Ia,Pa)
            Red (Ia|g,Pr)

            Red (Ir,Pa|g)
            Red (Ir,Pa|g)
            Red (Ir,Pr)
    """
    property_rating = get_property_rating(answers)
    income_rating = get_income_rating(answers)

    if property_rating == enums.RAYG.RED:
        # Interpretation:
        # - There's little potential for improvement (the property rating is
        # already is already good).
        return enums.RAYG.RED
    else:
        # Interpretation:
        # - There's some potential for improvement (the property rating could
        # be improved on).
        if income_rating == enums.RAYG.GREEN:
            # - Likely an eligible recipient for funding
            return property_rating
        else:
            return income_rating


def calculate_household_income(answers: models.Answers) -> int:
    """Calculate the annual income for all adults in the household."""

    total_income = 0

    for adult in answers.householdadult_set.all():
        total_income += calculate_adult_income(adult)

    return total_income


def calculate_adult_income(adult: models.HouseholdAdult) -> int:
    income = (
        _annualise_income(adult, "employed_income")
        + _annualise_income(adult, "self_employed_income")
        + _annualise_income(adult, "business_income")
        + _annualise_income(adult, "private_pension_income")
        + _annualise_income(adult, "state_pension_income")
        + _annualise_income(adult, "saving_investment_income")
    )

    # Add in any benefits
    benefit_income = sum(
        [
            _annualise_benefit_income(benefit)
            for benefit in adult.welfarebenefit_set.all()
        ]
    )

    return income + benefit_income


def _annualise_income(adult: models.HouseholdAdult, income_name: str) -> int:
    freq_name = f"{income_name}_frequency"
    income = getattr(adult, income_name, 0)
    if not income:
        # (zero or null, in either case don't case about frequency
        return 0
    elif getattr(adult, freq_name) == enums.PaymentFrequency.ANNUALLY:
        return income
    else:
        return income * 12


def _annualise_benefit_income(benefit: models.WelfareBenefit):
    income = benefit.amount
    if not income:
        # (zero or null, in either case don't case about frequency
        return 0
    elif benefit.frequency == enums.BenefitPaymentFrequency.WEEKLY:
        return round(income * 52.2)
    elif benefit.frequency == enums.BenefitPaymentFrequency.TWO_WEEKLY:
        return round(income * (52.2 / 2))
    elif benefit.frequency == enums.BenefitPaymentFrequency.FOUR_WEEKLY:
        return round(income * (52.2 / 4))
    elif benefit.frequency == enums.BenefitPaymentFrequency.MONTHLY:
        return income * 12
    else:
        return income


def get_financial_eligibility(answers: models.Answers) -> enums.FinancialEligibility:
    total_household_income = calculate_household_income(answers)

    if total_household_income < 31000:
        return enums.FinancialEligibility.ALL
    else:
        benefit_present = models.WelfareBenefit.objects.filter(
            recipient__answers=answers
        ).exists()
        if answers.take_home_lt_31k_confirmation or benefit_present:
            return enums.FinancialEligibility.SOME
        else:
            return enums.FinancialEligibility.NONE

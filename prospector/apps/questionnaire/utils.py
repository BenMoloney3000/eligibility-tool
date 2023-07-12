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


def get_property_rating(answers: models.Answers) -> enums.RAYG:
    """Property rating.

    Can only be RED / AMBER / GREEN.
    """

    if answers.sap_rating:
        # Based on having an EPC result
        if answers.sap_rating >= 65:
            # Property unlikely to be eligible for free or discounted schemes
            return enums.RAYG.RED
        elif answers.sap_rating >= 50:
            # Property eligible for some free or discounted schemes
            return enums.RAYG.AMBER
        else:
            # Property eligible for free or discounted schemes
            return enums.RAYG.GREEN
    else:
        """
        Without an EPC construct the property RAG rating as follows:

        G: Heating is Gas (gas_boiler_present)
        I: Walls are insulated (walls_insulated)
        S: Has Solar PV (has_solar_pv)

            G I S  Interpretation:
        G   N N N  - Large potential for improvement.
        Y   Y N N
        Y   N Y N
        Y   N N Y
        R   Y Y N
        R   Y N Y
        R   N Y Y
        R   Y Y Y  - Little potential for improvement.
        """

        RAG_LOOKUP = {
            #  (G, I, S) -> RAG value
            (False, False, False): enums.RAYG.GREEN,
            (True, False, False): enums.RAYG.AMBER,
            (False, True, False): enums.RAYG.AMBER,
            (False, False, True): enums.RAYG.AMBER,
            (True, True, False): enums.RAYG.RED,
            (True, False, True): enums.RAYG.RED,
            (False, True, True): enums.RAYG.RED,
            (True, True, True): enums.RAYG.RED,
        }

        return RAG_LOOKUP.get(
            (
                answers.gas_boiler_present,
                answers.walls_insulated,
                answers.has_solar_pv,
            )
        )


def get_income_rating(answers: models.Answers) -> enums.RAYG:
    # Household income rating
    if answers.total_income_lt_31k == enums.IncomeIsUnderThreshold.YES:
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
            if answers.take_home_lt_31k == enums.IncomeIsUnderThreshold.NO:
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

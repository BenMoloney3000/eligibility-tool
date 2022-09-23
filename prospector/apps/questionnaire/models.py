import uuid as uuid_lib
from typing import Optional

from django.db import models

from . import enums


class Answers(models.Model):
    class Meta:
        verbose_name_plural = "answers"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    uuid = models.UUIDField(
        db_index=True, default=uuid_lib.uuid4, editable=False, unique=True
    )

    """
    # "YOUR DETAILS"
    """

    terms_accepted_at = models.DateTimeField(blank=True, null=True)

    email = models.CharField(max_length=128, blank=True)

    first_name = models.CharField(verbose_name="First name", max_length=64, blank=True)
    last_name = models.CharField(verbose_name="Last name", max_length=64, blank=True)

    # The relationship of the respondent to the property
    respondent_role = models.CharField(
        max_length=24,
        choices=enums.RespondentRole.choices,
        blank=True,
        verbose_name="Relationship of respondent to property",
    )
    respondent_role_other = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Relationship of respondent to occupant",
    )

    # Repondent address details are not used if respondent lives in the property
    respondent_address_1 = models.CharField(max_length=128, blank=True)
    respondent_address_2 = models.CharField(max_length=128, blank=True)
    respondent_address_3 = models.CharField(max_length=128, blank=True)

    respondent_udprn = models.CharField(
        max_length=10, blank=True, verbose_name="Respondent UDPRN from API"
    )

    respondent_postcode = models.CharField(max_length=16, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_mobile = models.CharField(max_length=20, blank=True)

    """
    # PROPERTY DETAILS
    """

    occupant_first_name = models.CharField(
        verbose_name="Occupant first name", max_length=64, blank=True
    )
    occupant_last_name = models.CharField(
        verbose_name="Occupant last name", max_length=64, blank=True
    )
    property_address_1 = models.CharField(max_length=128, blank=True)
    property_address_2 = models.CharField(max_length=128, blank=True)
    property_address_3 = models.CharField(max_length=128, blank=True)
    property_postcode = models.CharField(max_length=16, blank=True)
    property_udprn = models.CharField(
        max_length=10, blank=True, verbose_name="Property UDPRN from API"
    )

    property_ownership = models.CharField(
        max_length=10, choices=enums.PropertyOwnership.choices, blank=True
    )
    # UPRN is 12 digits, too big for a PositiveIntegerField
    uprn = models.PositiveBigIntegerField(null=True, blank=True)

    respondent_has_permission = models.BooleanField(null=True, blank=True)

    """
    # DATA SOURCE DETAILS
    """
    selected_epc = models.CharField(max_length=100, blank=True)

    sap_rating = models.PositiveSmallIntegerField(blank=True, null=True)

    data_source = models.CharField(
        max_length=10,
        choices=enums.PropertyDataSource.choices,
        blank=True,
        verbose_name="Initial property data source",
    )

    # PROPERTY ENERGY PERFORMANCE DETAILS

    # All below fields are duplicated for user data and original data
    # If the user agrees with the presented data, the _orig field is left empty

    property_type = models.CharField(
        max_length=10, choices=enums.PropertyType.choices, blank=True
    )
    property_type_orig = models.CharField(
        max_length=10,
        choices=enums.PropertyType.choices,
        blank=True,
        verbose_name="Property type according to property data source before correction",
    )
    property_form = models.CharField(
        max_length=15, choices=enums.PropertyForm.choices, blank=True
    )
    property_form_orig = models.CharField(
        max_length=15,
        choices=enums.PropertyForm.choices,
        blank=True,
        verbose_name="Property form according to property data source before correction",
    )

    property_age_band = models.CharField(
        max_length=10, choices=enums.PropertyAgeBand.choices, blank=True, null=True
    )
    property_age_band_orig = models.CharField(
        max_length=10,
        choices=enums.PropertyAgeBand.choices,
        blank=True,
        null=True,
        verbose_name="Property age band according to property data source before correction",
    )

    wall_type = models.CharField(
        max_length=10, choices=enums.WallType.choices, blank=True
    )
    wall_type_orig = models.CharField(
        max_length=10,
        choices=enums.WallType.choices,
        blank=True,
        verbose_name="Wall type according to property data source before correction",
    )
    walls_insulated = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Walls are predominantly insulated",
    )
    walls_insulated_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Walls are predominantly insulated, according to property data source before correction",
    )

    suspended_floor = models.BooleanField(
        null=True, blank=True, verbose_name="Property has a suspended timber floor"
    )
    suspended_floor_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a suspended timber floor, according to property data source before correction",
    )

    suspended_floor_insulated = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has an insulated suspended timber floor",
    )
    suspended_floor_insulated_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has an insulated suspended floor, according to property data source before correction",
    )

    unheated_loft = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has an unheated loft space with exposed rafters and joists",
    )
    unheated_loft_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has an unheated loft space, according to property data source before correction",
    )

    room_in_roof = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a room in the roof space",
    )
    room_in_roof_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a room in the roof space, according to property data source before correction",
    )

    rir_insulated = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Room-in-roof is insulated",
    )
    rir_insulated_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Room-in-roof is insulated, according to property data source before correction",
    )

    roof_space_insulated = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Roof space is insulated",
    )
    roof_space_insulated_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Roof space is insulated, according to property data source before correction",
    )

    flat_roof = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Main part of property has a flat roof",
    )
    flat_roof_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Main part of property has a flat roof, according to property data source before correction",
    )
    flat_roof_insulated = models.CharField(
        max_length=14,
        choices=enums.InsulationConfidence.choices,
        blank=True,
        verbose_name="The property's flat roof is well insulated",
    )
    gas_boiler_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a mains gas central heating boiler",
    )
    gas_boiler_present_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a mains gas central heating boiler according to property data before correction",
    )
    gas_boiler_age = models.CharField(
        max_length=11, choices=enums.BoilerAgeBand.choices, blank=True
    )
    gas_boiler_broken = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property's mains gas central heating boiler is currently not working",
    )
    on_mains_gas = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property is connected to the mains gas network",
    )
    on_mains_gas_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property is connected to the mains gas network according to property data before correction",
    )
    other_heating_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a non-gas-powered central heating system",
    )
    other_heating_present_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has non-gas-powered central heating according to property data before correction",
    )
    heat_pump_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a heat pump",
    )
    heat_pump_present_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a heat pump, according to property data before correction",
    )
    other_heating_fuel = models.CharField(
        max_length=11,
        choices=enums.NonGasFuel.choices,
        blank=True,
        verbose_name="Non-gas central heating fuel used in property",
    )
    other_heating_fuel_orig = models.CharField(
        max_length=11,
        choices=enums.NonGasFuel.choices,
        blank=True,
    )
    storage_heaters_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has electric storage heaters",
    )
    storage_heaters_present_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has electric storage heaters according to property data before correction",
    )
    hhrshs_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has high heat retention storage heaters",
    )
    hhrshs_present_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has high heat retention storage heaters according to property data before correction",
    )
    electric_radiators_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has instantaneous electric heaters",
    )
    electric_radiators_present_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has instantaneous electric heaters according to property data before correction",
    )
    hwt_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a hot water tank",
    )
    trvs_present_old = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has themostatic radiator valves",
    )
    trvs_present_orig_old = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has thermostatic radiator valves according to property data before correction",
    )
    trvs_present = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name="Property has themostatic radiator valves",
    )
    trvs_present_orig = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name="Property has thermostatic radiator valves according to property data before correction",
    )
    room_thermostat = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a room thermostat",
    )
    room_thermostat_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a room thermostat according to property data before correction",
    )
    ch_timer = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a heating timer control",
    )
    ch_timer_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a heating timer control according to property data before correction",
    )
    programmable_thermostat = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a programmable thermostat control",
    )
    programmable_thermostat_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a programmable thermostat control according to property data before correction",
    )
    smart_thermostat = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a smart thermostat control",
    )
    has_solar_pv = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has solar PV",
    )
    has_solar_pv_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has solar PV before correction",
    )

    """
    # Store whether the user wishes to correct the inferred data.
    # We need this to know whether to jump ahead at the end of each section.
    """
    will_correct_type = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent chose to correct property type or age fields",
    )
    will_correct_walls = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent chose to correct walls characteristics",
    )
    will_correct_roof = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent chose to correct roof characteristics",
    )
    will_correct_floor = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent chose to correct floor characteristics",
    )
    will_correct_heating = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent chose to correct heating system fields",
    )

    """
    # CONSTRAINTS: planning area and owner preferences
    """

    tolerated_disruption = models.CharField(
        max_length=20,
        choices=enums.ToleratedDisruption.choices,
        blank=True,
        verbose_name="Maximum length of disruption tolerated",
    )
    state_of_repair = models.CharField(
        choices=enums.StateOfRepair.choices, blank=True, max_length=9
    )
    motivation_better_comfort = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Motivated by improving comfort",
    )
    motivation_lower_bills = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Motivated by reducing bills",
    )
    motivation_environment = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Motivated to make the home more environmentally friendly",
    )
    motivation_unknown = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent cannot give motivations of the homeowner",
    )
    contribution_capacity = models.CharField(
        choices=enums.ContributionCapacity.choices,
        max_length=9,
        blank=True,
    )
    consented_callback = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent consented to being called / emailed back to provide advice",
    )
    consented_future_schemes = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent consented to being contacted regarding relevant schemes in future.",
    )

    """
    # Top level household income assessment
    """

    adults = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Number of adults living in the property",
        choices=enums.OneToFourOrMore.choices,
    )
    children = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Number of children living in the property",
        choices=enums.UpToFourOrMore.choices,
    )

    total_income_lt_30k = models.CharField(
        choices=enums.IncomeIsUnderThreshold.choices,
        max_length=7,
        blank=True,
        verbose_name="Total gross household income is under £30,000 pa",
    )
    take_home_lt_30k = models.CharField(
        choices=enums.IncomeIsUnderThreshold.choices,
        blank=True,
        max_length=7,
        verbose_name="Total household take home pay is under £30,000 pa",
    )
    disability_benefits = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is receiving any disability related benefit",
    )
    child_benefit = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is receiving child benefit",
    )
    child_benefit_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=(
            "How many children child benefit is claimed for, or for which "
            "at least £21.80 per week of maintenance payments are made?"
        ),
        choices=enums.UpToFourOrMore.choices,
    )
    child_benefit_claimant_type = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=(
            "The person receiving child benefit is a single claimant (not "
            "member of a couple), or joint claimant."
        ),
        choices=enums.ChildBenefitClaimantType.choices,
    )
    child_benefit_eligibility_complete = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="This is a full account of child benefit eligibility",
    )
    child_benefit_threshold = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Relevant income threshold for child benefit recipient(s)",
    )
    income_lt_child_benefit_threshold = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Total household income is under the relevant child benefit threshold",
    )
    vulnerable_cariovascular = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is vulnerable due to a cardiovascular condition",
    )
    vulnerable_respiratory = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is vulnerable due to a respiratory condition",
    )
    vulnerable_mental_health = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is vulnerable due to a mental health condition",
    )
    vulnerable_cns = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is vulnerable due to central nervous system condition",
    )
    vulnerable_disability = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is vulnerable due to disability",
    )
    vulnerable_age = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is vulnerable due to being aged over 65",
    )
    vulnerable_child_pregnancy = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is under five years old or pregnant",
    )
    incomes_complete = models.BooleanField(
        blank=True, null=True, verbose_name="This is a full account of household income"
    )
    take_home_lt_30k_confirmation = models.BooleanField(
        blank=True,
        null=True,
        verbose_name=(
            "Household take home pay after tax, national insurance, energy bills "
            "and housing costs is less than £30k"
        ),
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_occupant(self) -> Optional[bool]:
        if self.respondent_role is None:
            return None

        return self.respondent_role in [
            enums.RespondentRole.OWNER_OCCUPIER.value,
            enums.RespondentRole.TENANT.value,
        ]

    @property
    def is_owner(self) -> Optional[bool]:
        if self.respondent_role is None:
            return None

        return self.respondent_role in [
            enums.RespondentRole.LANDLORD.value,
            enums.RespondentRole.OWNER_OCCUPIER.value,
        ]

    """
    # The following logic is used to determine if the user can skip sections
    # of the questionnaire.
    """

    def type_inferences_complete(self):
        # Includes age
        return (
            self.property_type_orig is not None
            and self.property_form_orig is not None
            and self.property_age_band_orig is not None
        )

    def wall_inferences_complete(self):
        return self.wall_type_orig is not None and self.walls_insulated_orig is not None

    def floor_inferences_complete(self):
        # Bit more complicated.
        return self.suspended_floor_orig is False or (
            self.suspended_floor_orig is True
            and self.suspended_floor_insulated_orig is not None
        )

    def roof_inferences_complete(self):
        # Yet more complicated.
        if self.unheated_loft_orig is None:
            return False
        elif self.unheated_loft_orig is True:
            return self.roof_space_insulated_orig is not None
        else:
            # We think there's no loft
            if self.room_in_roof_orig is None:
                return False
            elif self.room_in_roof_orig is True:
                return self.rir_insulated_orig is not None
            else:
                # No room in roof
                if self.flat_roof_orig is None:
                    return False
                elif self.flat_roof_orig is True:
                    # can't infer certainty on insulation
                    return False
                else:
                    return True

    def heating_inferences_complete(self):
        # More complicated still
        if self.gas_boiler_present_orig is None:
            return False
        elif self.gas_boiler_present_orig is True:
            # Can't infer presence of HWT, boiler age or state.
            return False
        else:
            # No gas boiler then.
            if self.on_mains_gas_orig is None:
                return False
            elif self.other_heating_present_orig is False:
                if self.storage_heaters_present_orig is False:
                    # A very narrow window of possibility!
                    return self.electric_radiators_present_orig is not None
                else:
                    return self.hhrshs_present_orig is not None
            else:
                # Either couldn't tell if there is another CH system, or we think
                # there is, in which case we can't infer presence of HWT.
                return False


# enough with that model! about time we had a different one.


class HouseholdAdult(models.Model):
    answers = models.ForeignKey(
        Answers, on_delete=models.CASCADE, blank=False, null=False
    )
    adult_number = models.PositiveSmallIntegerField(blank=False, null=False)
    first_name = models.CharField(verbose_name="First name", max_length=64, blank=True)
    last_name = models.CharField(verbose_name="Last name", max_length=64, blank=True)
    employment_status = models.CharField(
        choices=enums.EmploymentStatus.choices, max_length=13, blank=True
    )
    employed_income = models.PositiveIntegerField(blank=True, null=True)
    employed_income_frequency = models.CharField(
        choices=enums.PaymentFrequency.choices, max_length=8, blank=True
    )
    self_employed_income = models.PositiveIntegerField(blank=True, null=True)
    self_employed_income_frequency = models.CharField(
        choices=enums.PaymentFrequency.choices, max_length=8, blank=True
    )
    business_income = models.PositiveIntegerField(blank=True, null=True)
    business_income_frequency = models.CharField(
        choices=enums.PaymentFrequency.choices, max_length=8, blank=True
    )
    private_pension_income = models.PositiveIntegerField(blank=True, null=True)
    private_pension_income_frequency = models.CharField(
        choices=enums.PaymentFrequency.choices, max_length=8, blank=True
    )
    state_pension_income = models.PositiveIntegerField(blank=True, null=True)
    state_pension_income_frequency = models.CharField(
        choices=enums.PaymentFrequency.choices, max_length=8, blank=True
    )
    saving_investment_income = models.PositiveIntegerField(blank=True, null=True)
    saving_investment_income_frequency = models.CharField(
        choices=enums.PaymentFrequency.choices, max_length=8, blank=True
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class WelfareBenefit(models.Model):
    recipient = models.ForeignKey(
        HouseholdAdult, on_delete=models.CASCADE, blank=False, null=False
    )
    benefit_type = models.CharField(
        choices=enums.BenefitType.choices, max_length=20, blank=False
    )
    frequency = models.CharField(
        choices=enums.BenefitPaymentFrequency.choices, max_length=12, blank=True
    )
    amount = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipient", "benefit_type"],
                name="no_duplicated_benefits_per_recipient",
            )
        ]

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
    short_uid = models.CharField(
        db_index=True,
        max_length=10,
        default=None,
        editable=False,
        unique=True,
        verbose_name="Client's unique reference number to be passed in email for reference purpose",
    )

    """
    # "YOUR DETAILS"
    """

    terms_accepted_at = models.DateTimeField(blank=True, null=True)

    consented_callback = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="Respondent consent to call or email them to offer advice and help",
    )

    consented_future_schemes = models.BooleanField(
        blank=True,
        null=True,
        verbose_name=(
            "Respondent consent to contact them in the future when there are relevant grants or programmes"
        ),
    )

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

    company_name = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Landlord company name (if applicable)",
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

    respondent_comments = models.TextField(blank=True, null=True)

    source_of_info_about_pec = models.CharField(
        max_length=128,
        choices=enums.HowDidYouHearAboutPEC.choices,
        default=enums.HowDidYouHearAboutPEC.LABEL,
        blank=True,
    )

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
    lower_super_output_area_code = models.CharField(max_length=50, blank=True)

    tenure = models.CharField(
        max_length=128,
        choices=enums.Tenure.choices,
        blank=True,
        verbose_name="Property ownership",
    )
    # UPRN is 12 digits, too big for a PositiveIntegerField
    uprn = models.CharField(max_length=120, blank=True, null=True)
    respondent_has_permission = models.BooleanField(null=True, blank=True)

    """
    # DATA SOURCE DETAILS
    """
    # selected_epc = models.CharField(max_length=100, blank=True)

    sap_score = models.PositiveSmallIntegerField(blank=True, null=True)
    sap_band = models.CharField(
        max_length=1, choices=enums.EfficiencyBand.choices, blank=True, null=True
    )
    lodged_epc_score = models.PositiveSmallIntegerField(blank=True, null=True)
    lodged_epc_band = models.CharField(
        max_length=1, choices=enums.EfficiencyBand.choices, blank=True, null=True
    )
    multiple_deprivation_index = models.SmallIntegerField(blank=True, null=True)

    # PROPERTY ENERGY PERFORMANCE DETAILS

    # All below fields are duplicated for user data and original data
    # If the user agrees with the presented data, the _orig field is left empty

    property_type = models.CharField(
        max_length=128,
        choices=enums.PropertyType.choices,
        blank=True,
    )

    property_attachment = models.CharField(
        max_length=128,
        choices=enums.PropertyAttachment.choices,
        blank=True,
    )

    property_construction_years = models.CharField(
        max_length=12,
        choices=enums.PropertyConstructionYears.choices,
        blank=True,
        null=True,
    )

    wall_construction = models.CharField(
        max_length=128,
        choices=enums.WallConstruction.choices,
        blank=True,
    )

    walls_insulation = models.CharField(
        max_length=128,
        choices=enums.WallInsulation.choices,
        blank=True,
    )

    roof_construction = models.CharField(
        max_length=128,
        choices=enums.RoofConstruction.choices,
        blank=True,
    )

    roof_insulation = models.CharField(
        max_length=128,
        choices=enums.RoofInsulation.choices,
        blank=True,
    )

    floor_construction = models.CharField(
        max_length=128, choices=enums.FloorConstruction.choices, blank=True
    )

    floor_insulation = models.CharField(
        max_length=128, choices=enums.FloorInsulation.choices, blank=True
    )

    glazing = models.CharField(
        max_length=128, choices=enums.Glazing.choices, blank=True
    )

    heating = models.CharField(
        max_length=128, choices=enums.Heating.choices, blank=True
    )

    main_fuel = models.CharField(
        max_length=128, choices=enums.MainFuel.choices, blank=True
    )

    boiler_efficiency = models.CharField(
        max_length=1, choices=enums.EfficiencyBand.choices, blank=True
    )

    controls_adequacy = models.CharField(
        max_length=128, choices=enums.ControlsAdequacy.choices, blank=True
    )

    heated_rooms = models.IntegerField(blank=True, null=True)
    t_co2_current = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True
    )

    realistic_fuel_bill = models.CharField(max_length=9, blank=True, null=True)

    """
    # Top level household income assessment
    """

    adults = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Number of adults living in the property",
        choices=enums.OneToTen.choices,
    )
    children = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Number of children living in the property",
        choices=enums.OneToTenOrNone.choices,
    )

    seniors = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Number of seniors (over 60 years old) living in the property",
        choices=enums.OneToTenOrNone.choices,
    )

    household_income = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Total gross household income before tax",
    )

    means_tested_benefits = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent receives means tested benefits",
    )
    past_means_tested_benefits = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Respondent received means tested benefits in the past 18 months",
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
        choices=enums.OneToFiveOrMore.choices,
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
    free_school_meals_eligibility = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Children living in household eligible for free school meals",
    )
    vulnerabilities_general = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is vulnerable",
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
    vulnerable_children = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is with young children (from new-born to school age)",
    )
    vulnerable_pregnancy = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is pregnant",
    )
    vulnerable_immunosuppression = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Anyone in the house is vulnerable due to immunosuppression",
    )
    vulnerable_comments = models.CharField(
        max_length=400,
        null=True,
        blank=True,
        verbose_name="User's input on other vulnerabilities",
    )
    housing_costs = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Housing costs",
    )
    council_tax_reduction = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Is the household entitled to a Council Tax reduction",
    )
    nmt4properties = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="No more than 4 properties in landlord's portfolio",
    )
    willing_to_contribute = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Landlord be willing to contribute 33% of all spending",
    )

    advice_needed_warm = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Advice needed: respondent struggles to keep their home warm or damp free",
    )

    advice_needed_bills = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Advice needed: respondent's energy bills make them feel anxious",
    )

    advice_needed_supplier = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Advice needed: issues with supplier, meter or energy debt",
    )

    advice_needed_from_team = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Advice needed from Energy Advice Team",
    )

    def save(self, *args, **kwargs):
        from prospector.apps.questionnaire import utils

        if not self.short_uid:
            # Generate short_uid value once, then check the db. If already exists, keep trying.
            self.short_uid = utils.generate_id()  # noqa
            while Answers.objects.filter(short_uid=self.short_uid).exists():
                self.short_uid = utils.generate_id()  # noqa
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def income_after_housing_costs(self):
        return self.household_income - self.housing_costs

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

    @property
    def is_property_in_lower_sap_band(self) -> Optional[bool]:
        if self.sap_band is None:
            return None

        return self.sap_band in [
            enums.EfficiencyBand.D.value,
            enums.EfficiencyBand.E.value,
            enums.EfficiencyBand.F.value,
            enums.EfficiencyBand.G.value,
        ]

    @property
    def is_property_not_heated_by_main_gas(self) -> Optional[bool]:
        if self.main_fuel is None:
            return None

        return self.main_fuel not in [
            enums.MainFuel.MGC.value,
            enums.MainFuel.MGNC.value,
        ]

    @property
    def is_property_privately_owned(self) -> Optional[bool]:
        if self.tenure is None:
            return None

        return self.tenure == enums.Tenure.OWNER_OCCUPIED.value

    @property
    def is_property_privately_rented(self) -> Optional[bool]:
        if self.tenure is None:
            return None

        return self.tenure == enums.Tenure.RENTED_PRIVATE.value

    @property
    # Returns True even if value of nmt4properties is None
    # because while respond by tenant we do not ask this straightforward
    # rather assuming landlord's positive answer
    def does_landlord_own_no_more_than_4_properties(self) -> bool:
        return self.nmt4properties in [None, True]

    @property
    # Returns True even if value of willing_to_contribute is None
    # because when respond by tenant we do not ask this straightforward
    # rather assuming landlord's positive answer
    def will_landlord_contribute(self) -> bool:
        return self.willing_to_contribute in [None, True]

    @property
    def is_deprivation_index_upto_3(self) -> Optional[bool]:
        if self.multiple_deprivation_index is None:
            return None

        return self.multiple_deprivation_index in [1, 2, 3]

    @property
    def is_income_less_than_31K(self) -> Optional[bool]:
        if self.household_income is None:
            return None
        return self.household_income < 31000

    @property
    def is_income_under_max_based_on_occupants(self) -> Optional[bool]:
        if self.children is not None and self.seniors is None:
            dependents = self.children
        elif self.seniors is not None and self.children is None:
            dependents = self.seniors
        elif self.children is None and self.seniors is None:
            dependents = None
        else:
            dependents = self.children + self.seniors

        if self.household_income is None:
            return None
        elif self.adults is None:
            return None
        elif self.adults >= 2:
            if dependents in [None, 0]:
                return self.household_income <= 20000
            elif dependents == 1:
                return self.household_income <= 24000
            elif dependents == 2:
                return self.household_income <= 28000
            elif dependents == 3:
                return self.household_income <= 32000
            elif dependents == 4:
                return self.household_income <= 36000
            elif dependents >= 5:
                return self.household_income <= 40000
        elif self.adults == 1:
            if dependents in [None, 0]:
                return self.household_income <= 20000
            elif dependents == 1:
                return self.household_income <= 20000
            elif dependents == 2:
                return self.household_income <= 20000
            elif dependents == 3:
                return self.household_income <= 23000
            elif dependents == 4:
                return self.household_income <= 27600
            elif dependents >= 5:
                return self.household_income <= 31600

        return None

    @property
    def is_hug2_eligible(self) -> Optional[bool]:
        if self.tenure == enums.Tenure.OWNER_OCCUPIED.value:
            return (
                self.is_property_in_lower_sap_band
                and self.is_property_not_heated_by_main_gas
                and (
                    self.is_deprivation_index_upto_3
                    or self.is_income_less_than_31K
                    or self.is_income_under_max_based_on_occupants
                )
            )
        elif self.tenure == enums.Tenure.RENTED_PRIVATE.value:
            return (
                self.is_property_in_lower_sap_band
                and self.is_property_not_heated_by_main_gas
                and self.does_landlord_own_no_more_than_4_properties
                and self.will_landlord_contribute
                and (
                    self.is_deprivation_index_upto_3
                    or self.is_income_less_than_31K
                    or self.is_income_under_max_based_on_occupants
                )
            )
        return False

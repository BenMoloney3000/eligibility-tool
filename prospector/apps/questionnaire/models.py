import uuid as uuid_lib
from typing import Optional

from django.db import models

from . import enums
from .utils import get_whlg_eligible_postcodes

SAP_BANDS = [
    enums.EfficiencyBand.D,
    enums.EfficiencyBand.E,
    enums.EfficiencyBand.F,
    enums.EfficiencyBand.G,
]

TAX_BANDS = [
    enums.CouncilTaxBand.A,
    enums.CouncilTaxBand.B,
    enums.CouncilTaxBand.C,
    enums.CouncilTaxBand.D,
]

EPC_BANDS = [
    enums.EfficiencyBand.D,
    enums.EfficiencyBand.E,
    enums.EfficiencyBand.F,
    enums.EfficiencyBand.G,
]

TENURES = [
    enums.Tenure.OWNER_OCCUPIED,
    enums.Tenure.RENTED_PRIVATE,
]

WHLG_ELIGIBLE_POSTCODES = get_whlg_eligible_postcodes()


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

    parity_object_id = models.CharField(
        max_length=20, editable=False, blank=True, null=True
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

    council_tax_band = models.CharField(
        max_length=1, choices=enums.CouncilTaxBand.choices, blank=True, null=True
    )
    sap_score = models.PositiveSmallIntegerField(blank=True, null=True)
    sap_band = models.CharField(
        max_length=1, choices=enums.EfficiencyBand.choices, blank=True, null=True
    )
    lodged_epc_score = models.PositiveSmallIntegerField(blank=True, null=True)
    lodged_epc_band = models.CharField(
        max_length=1, choices=enums.EfficiencyBand.choices, blank=True, null=True
    )
    multiple_deprivation_index = models.SmallIntegerField(blank=True, null=True)
    income_decile = models.SmallIntegerField(blank=True, null=True)

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

    household_income_after_tax = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Household income after tax",
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

    advice_needed_details = models.TextField(blank=True, null=True)

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
    def landlord_details(self) -> Optional[dict]:
        if (
            self.respondent_role is None
            or self.respondent_role != enums.RespondentRole.LANDLORD.value
        ):
            return {
                "address1": None,
                "address2": None,
                "city": None,
                "postcode": None,
                "phone": None,
            }
        else:
            if self.contact_phone:
                phone = self.contact_phone
            else:
                phone = self.contact_mobile
            return {
                "address1": self.respondent_address_1,
                "address2": self.respondent_address_2,
                "city": self.respondent_address_3,
                "postcode": self.respondent_postcode,
                "phone": phone,
            }

    @property
    def is_owner(self) -> Optional[bool]:
        if self.respondent_role is None:
            return None

        return self.respondent_role in [
            enums.RespondentRole.LANDLORD.value,
            enums.RespondentRole.OWNER_OCCUPIER.value,
        ]

    @property
    def is_property_in_lower_band(self) -> Optional[bool]:
        if self.lodged_epc_band:
            return self.lodged_epc_band in [
                enums.EfficiencyBand.D.value,
                enums.EfficiencyBand.E.value,
                enums.EfficiencyBand.F.value,
                enums.EfficiencyBand.G.value,
            ]
        elif self.sap_band:
            return self.sap_band in [
                enums.EfficiencyBand.D.value,
                enums.EfficiencyBand.E.value,
                enums.EfficiencyBand.F.value,
                enums.EfficiencyBand.G.value,
            ]
        else:
            return None

    @property
    def is_property_not_heated_by_mains_gas(self) -> Optional[bool]:
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
    def is_property_among_whlg_eligible_postcodes(self) -> bool:
        return self.property_postcode in WHLG_ELIGIBLE_POSTCODES

    @property
    def is_income_less_than_or_equal_to_36K(self) -> Optional[bool]:
        if self.household_income is None:
            return None
        return self.household_income <= 36000

    @property
    def is_income_under_or_equal_to_max_for_eco4_flex(self) -> Optional[bool]:
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
            if dependents == 3:
                return self.household_income <= 32000
            elif dependents == 4:
                return self.household_income <= 36000
            elif dependents >= 5:
                return self.household_income <= 40000
        elif self.adults == 1:
            if dependents >= 5:
                return self.household_income <= 31600
        return False

    @property
    def is_income_under_or_equal_to_max_for_whlg(self) -> Optional[bool]:
        if self.children is not None and self.seniors is None:
            dependents = self.children
        elif self.seniors is not None and self.children is None:
            dependents = self.seniors
        elif self.children is None and self.seniors is None:
            return None
        else:
            dependents = self.children + self.seniors

        if self.housing_costs is None:
            return None
        else:
            housing_annual_cost = self.housing_costs * 12

        if self.household_income_after_tax is None:
            return None
        elif self.adults is None:
            return None
        elif self.adults >= 2:
            if dependents == 1:
                return self.household_income_after_tax - housing_annual_cost <= 24000
            elif dependents == 2:
                return self.household_income_after_tax - housing_annual_cost <= 28000
            elif dependents == 3:
                return self.household_income_after_tax - housing_annual_cost <= 32000
            elif dependents == 4:
                return self.household_income_after_tax - housing_annual_cost <= 36000
            elif dependents >= 5:
                return self.household_income_after_tax - housing_annual_cost <= 40000
            else:
                return False
        elif self.adults == 1:
            if dependents == 3:
                return self.household_income_after_tax - housing_annual_cost <= 23600
            elif dependents == 4:
                return self.household_income_after_tax - housing_annual_cost <= 27600
            elif dependents >= 5:
                return self.household_income_after_tax - housing_annual_cost <= 31600
            else:
                return False
        return False

    """
    # Funding schemes eligibility
    """

    @property
    def is_bus_eligible(self) -> Optional[bool]:
        if self.tenure is None:
            return None
        return self.tenure == enums.Tenure.OWNER_OCCUPIED.value

    @property
    def is_connected_for_warmth_eligible(self) -> Optional[bool]:
        if self.tenure is None:
            return None

        return (
            self.tenure in TENURES
            and (
                self.is_cavity_wall_insulation_recommended
                or self.is_loft_insulation_recommended
            )
            and (self.council_tax_band is None or self.council_tax_band in TAX_BANDS)
        )

    @property
    def is_eco4_eligible(self) -> Optional[bool]:
        if (
            self.means_tested_benefits is None
            or (
                self.means_tested_benefits is False
                and self.past_means_tested_benefits is None
            )
            or self.sap_band is None
            or self.tenure is None
        ):
            return None

        return (
            (self.means_tested_benefits or self.past_means_tested_benefits)
            and self.sap_band in SAP_BANDS
            and self.tenure in TENURES
        )

    @property
    def is_eco4_flex_eligible_route_1(self) -> Optional[bool]:
        if (
            self.household_income is None
            or self.child_benefit is None
            or self.sap_band is None
            or self.tenure is None
        ):
            return None

        return (
            (
                self.household_income <= 31000
                or (
                    self.child_benefit
                    and self.is_income_under_or_equal_to_max_for_eco4_flex
                )
            )
            and self.sap_band in SAP_BANDS
            and self.tenure in TENURES
        )

    @property
    def is_eco4_flex_eligible_route_2_a(self) -> Optional[bool]:
        if (
            self.council_tax_reduction is None
            or self.vulnerabilities_general is None
            or self.multiple_deprivation_index is None
            or self.sap_band is None
            or self.tenure is None
            or self.free_school_meals_eligibility is None
        ):
            return None

        return (
            self.council_tax_reduction
            and (
                self.vulnerabilities_general
                or self.multiple_deprivation_index in [1, 2, 3]
            )
            and self.sap_band in SAP_BANDS
            and self.tenure in TENURES
        )

    @property
    def is_eco4_flex_eligible_route_2_b(self) -> Optional[bool]:
        if (
            self.free_school_meals_eligibility is None
            or self.vulnerabilities_general is None
            or self.multiple_deprivation_index is None
            or self.sap_band is None
            or self.tenure is None
        ):
            return None

        return (
            self.free_school_meals_eligibility
            and (
                self.vulnerabilities_general
                or self.multiple_deprivation_index in [1, 2, 3]
            )
            and self.sap_band in SAP_BANDS
            and self.tenure in TENURES
        )

    @property
    def is_eco4_flex_eligible(self) -> Optional[bool]:
        return (
            self.is_eco4_flex_eligible_route_1
            or self.is_eco4_flex_eligible_route_2_a
            or self.is_eco4_flex_eligible_route_2_b
        )

    @property
    def is_gbis_eligible__common_conditions(self) -> Optional[bool]:
        return (
            (
                (
                    self.tenure == enums.Tenure.OWNER_OCCUPIED.value
                    and self.sap_band in SAP_BANDS
                )
                or (
                    self.tenure == enums.Tenure.RENTED_PRIVATE.value
                    and self.sap_band in SAP_BANDS[:2]  # D-E only
                )
                or (
                    self.tenure == enums.Tenure.RENTED_SOCIAL.value
                    and self.sap_band in SAP_BANDS[1:]  # E-G only
                )
            )
            and (
                self.is_cavity_wall_insulation_recommended
                or self.is_loft_insulation_recommended
            )
            and self.property_type != enums.PropertyType.PARK_HOME.value
        )

    @property
    def is_gbis_eligible_route_1(self) -> Optional[bool]:
        if self.tenure is None or self.sap_band is None or self.property_type is None:
            return None

        return self.is_gbis_eligible__common_conditions and (
            self.council_tax_band is None or self.council_tax_band in TAX_BANDS
        )

    @property
    def is_gbis_eligible_route_2(self) -> Optional[bool]:
        if (
            self.tenure is None
            or self.sap_band is None
            or self.property_type is None
            or self.means_tested_benefits is None
        ):
            return None

        return self.is_gbis_eligible__common_conditions and self.means_tested_benefits

    @property
    def is_gbis_eligible(self) -> Optional[bool]:
        return self.is_gbis_eligible_route_1 or self.is_gbis_eligible_route_2

    @property
    def is_whlg_eligible(self) -> Optional[bool]:
        return (
            self.sap_band in SAP_BANDS
            and self.tenure in [enums.Tenure.RENTED_PRIVATE, enums.Tenure.OWNER_OCCUPIED]
            and (
                self.is_property_among_whlg_eligible_postcodes
                or self.means_tested_benefits
                or self.household_income < 36000
                or self.is_income_under_or_equal_to_max_for_whlg
                or self.is_eco4_flex_eligible_route_2_a
                or self.is_eco4_flex_eligible_route_2_b
                or (
                    (
                        self.vulnerabilities_general
                        or self.multiple_deprivation_index in [1, 2, 3]
                    )
                    and self.council_tax_reduction
                    or self.free_school_meals_eligibility
                )
            )
        )


    @property
    def is_any_scheme_eligible(self) -> Optional[bool]:
        return (
            self.is_bus_eligible
            or self.is_connected_for_warmth_eligible
            or self.is_eco4_eligible
            or self.is_eco4_flex_eligible
            or self.is_gbis_eligible
            or self.is_whlg_eligible
        )

    @property
    def if_off_mains_gas_and_given_sap_score(self) -> Optional[bool]:
        return (
            self.is_property_not_heated_by_mains_gas
            and self.sap_band in SAP_BANDS[1:3]  # E-F only
        )

    """
    # Measure recommendations
    """

    @property
    def is_cavity_wall_insulation_recommended(self) -> bool:
        return (self.wall_construction == enums.WallConstruction.CAVITY) and (
            self.walls_insulation == enums.WallInsulation.AS_BUILT
        )

    @property
    def is_solid_wall_insulation_recommended(self) -> bool:
        solid_walls = [
            enums.WallConstruction.GRANITE,
            enums.WallConstruction.SANDSTONE,
            enums.WallConstruction.SOLID_BRICK,
            enums.WallConstruction.SYSTEM,
        ]

        return (
            self.floor_construction in solid_walls
            and self.walls_insulation == enums.WallInsulation.AS_BUILT
        )

    @property
    def is_underfloor_insulation_recommended(self) -> bool:
        floor_insulation_options = [
            enums.FloorInsulation.AS_BUILT,
            enums.FloorInsulation.UNKNOWN,
        ]

        return (
            self.floor_construction == enums.FloorConstruction.ST
            and self.floor_insulation in floor_insulation_options
        )

    @property
    def is_loft_insulation_recommended(self) -> bool:
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

        return (
            self.roof_construction in roof_construction_for_ri
            and self.roof_insulation in roof_insulation_for_ri
        )

    @property
    def is_rir_insulation_recommended(self) -> bool:
        roof_insulation_for_rir = [
            enums.RoofInsulation.AS_BUILD,
            enums.RoofInsulation.MM_12,
            enums.RoofInsulation.MM_25,
            enums.RoofInsulation.MM_50,
            enums.RoofInsulation.MM_75,
            enums.RoofInsulation.NO_INSULATION,
        ]

        return (
            self.roof_insulation in roof_insulation_for_rir
            and self.roof_construction == enums.RoofConstruction.PWSC
        )

    @property
    def is_boiler_upgrade_recommended(self) -> bool:
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

        return (
            self.main_fuel in main_fuel_for_bu
            and self.boiler_efficiency in boiler_efficiency_for_bu
            and self.heating == enums.Heating.BOILERS
        )

    @property
    def is_heatpump_installation_recommended(self) -> bool:
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

        return self.main_fuel in fuel_1_for_hpi or (
            self.main_fuel in fuel_2_for_hpi and self.heating in heating_for_hpi
        )

    @property
    def is_solar_pv_installation_recommended(self) -> bool:
        """Check for both solar PV and battery storage recommendation."""
        roof_for_PV = [
            enums.RoofConstruction.PNLA,
            enums.RoofConstruction.PNNLA,
            enums.RoofConstruction.PWSC,
        ]

        return self.floor_construction in roof_for_PV

    @property
    def is_heating_controls_installation_recommended(self) -> bool:
        return self.heating == enums.Heating.BOILERS

    @property
    def occupant_details(self) -> dict:
        occupants = [
            enums.RespondentRole.OWNER_OCCUPIER,
            enums.RespondentRole.TENANT,
        ]

        if self.respondent_role in occupants:
            return {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email,
                "phone": self.contact_phone,
                "mobile": self.contact_mobile,
            }
        else:
            return {
                "first_name": self.occupant_first_name,
                "last_name": self.occupant_last_name,
                "email": None,
                "phone": None,
                "mobile": None,
            }

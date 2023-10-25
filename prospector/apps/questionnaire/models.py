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
        choices=enums.OneToFourOrMore.choices,
    )
    children = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Number of children living in the property",
        choices=enums.UpToFourOrMore.choices,
    )

    total_income = models.CharField(
        choices=enums.IncomeIsUnderThreshold.choices,
        max_length=7,
        blank=True,
        verbose_name="Total gross household income is under £31,000 pa",
    )
    take_home = models.CharField(
        choices=enums.IncomeIsUnderThreshold.choices,
        blank=True,
        max_length=7,
        verbose_name="Total household take home pay is under £31,000 pa",
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
    take_home_lt_31k_confirmation = models.BooleanField(
        blank=True,
        null=True,
        verbose_name=(
            "Household take home pay after tax, national insurance, energy bills "
            "and housing costs is less than £31k"
        ),
    )

    # Computed Fields
    income_rating = models.CharField(
        choices=enums.RAYG.choices,
        max_length=8,
        null=True,
        blank=True,
        verbose_name="Income rating (computed field)",
    )
    property_rating = models.CharField(
        choices=enums.RAYG.choices,
        max_length=8,
        null=True,
        blank=True,
        verbose_name="Property rating (computed field)",
    )

    def save(self, *args, **kwargs):
        from prospector.apps.questionnaire import utils

        self.income_rating = utils.get_income_rating(self)
        self.property_rating = utils.get_property_rating(self)
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
    def is_owner(self) -> Optional[bool]:
        if self.respondent_role is None:
            return None

        return self.respondent_role in [
            enums.RespondentRole.LANDLORD.value,
            enums.RespondentRole.OWNER_OCCUPIER.value,
        ]

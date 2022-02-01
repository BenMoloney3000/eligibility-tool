import uuid as uuid_lib

from django.db import models

from . import enums


class Answers(models.Model):
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

    address_1 = models.CharField(max_length=128, blank=True)
    address_2 = models.CharField(max_length=128, blank=True)
    address_3 = models.CharField(max_length=128, blank=True)

    postcode = models.CharField(max_length=16, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_preference = models.CharField(max_length=128, blank=True)

    # Whether all the above details are those of the occupant/property
    is_occupant = models.BooleanField(null=True, blank=True)

    """
    # PROPERTY DETAILS
    """

    # Occupant/property details are only used if respondent != occupant
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

    property_ownership = models.CharField(
        max_length=10, choices=enums.PropertyOwnership.choices, blank=True
    )

    respondent_relationship = models.CharField(
        max_length=6,
        choices=enums.RespondentRelationship.choices,
        blank=True,
        verbose_name="Relationship of responder to occupant",
    )

    respondent_relationship_other = models.CharField(
        max_length=128, blank=True, verbose_name="'Other' relationship detail"
    )

    respondent_has_permission = models.BooleanField(null=True, blank=True)

    """
    # DATA SOURCE DETAILS
    """
    selected_epc = models.CharField(max_length=100, blank=True)

    # UPRN is 12 digits, too big for a PositiveIntegerField
    uprn = models.PositiveBigIntegerField(null=True, blank=True)

    data_source = models.CharField(
        max_length=10,
        choices=enums.PropertyDataSource.choices,
        blank=True,
        verbose_name="Initial property data source",
    )

    """
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
        max_length=12, choices=enums.PropertyForm.choices, blank=True
    )
    property_form_orig = models.CharField(
        max_length=12,
        choices=enums.PropertyForm.choices,
        blank=True,
        verbose_name="Property form according to property data source before correction",
    )
    property_age_band = models.CharField(
        max_length=12, choices=enums.PropertyAgeBand.choices, blank=True
    )
    property_age_band_orig = models.CharField(
        max_length=12,
        choices=enums.PropertyAgeBand.choices,
        blank=True,
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
    # Wall type can be inferred from the age band
    wall_type_inferred = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Wall type before correction was inferred from property age"
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
        null=True,
        blank=True,
        verbose_name="Property has a suspended timber floor"
    )
    suspended_floor_orig = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a suspended timber floor, according to property data source before correction",
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

    # TODO: heating systems, planning constraints, preferences, income assessment
    """


class ConsentGranted(models.Model):
    granted_for = models.ForeignKey(
        Answers, on_delete=models.CASCADE, blank=False, null=False
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    consent = models.CharField(
        max_length=10, choices=enums.Consent.choices, blank=False
    )

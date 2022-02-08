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

    udprn = models.CharField(
        max_length=10, blank=True, verbose_name="Respondent UDPRN from API"
    )

    postcode = models.CharField(max_length=16, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_mobile = models.CharField(max_length=20, blank=True)

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
    property_udprn = models.CharField(
        max_length=10, blank=True, verbose_name="Property UDPRN from API"
    )

    property_ownership = models.CharField(
        max_length=10, choices=enums.PropertyOwnership.choices, blank=True
    )
    # UPRN is 12 digits, too big for a PositiveIntegerField
    uprn = models.PositiveBigIntegerField(null=True, blank=True)

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
    property_age_band = models.PositiveSmallIntegerField(
        choices=enums.PropertyAgeBand.choices, blank=True, null=True
    )

    property_age_band_orig = models.PositiveSmallIntegerField(
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
    flat_roof_modern = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="The property's flat roof was build or insulated after 1980",
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
    hwt_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has a hot water tank",
    )
    trvs_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Property has themostatic radiator valves",
    )
    trvs_present_orig = models.BooleanField(
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
        verbose_name="Property has a programmable thermostat control",
    )

    # TODO: planning constraints, preferences, income assessment


class ConsentGranted(models.Model):
    granted_for = models.ForeignKey(
        Answers, on_delete=models.CASCADE, blank=False, null=False
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    consent = models.CharField(
        max_length=10, choices=enums.Consent.choices, blank=False
    )

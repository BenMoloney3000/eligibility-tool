from django.db import models


class PropertyOwnership(models.TextChoices):
    OWNED = "OWNED", "Property is in private ownership"
    PRIVATE_TENANCY = "RENTAL", "Property is rented from a private landlord"
    SOCIAL_TENANCY = (
        "SOCIAL",
        "Property is rented from a social landlord or local authority",
    )


class RespondentRelationship(models.TextChoices):
    FRIEND = "FRIEND", "I am a friend of the occupant"
    PARENT = "PARENT", "I am a parent of the occupant"
    CHILD = "CHILD", "I am a child of the occupant"
    OTHER_FAMILY = "FAMILY", "I am another relative of the occupant"
    OTHER = "OTHER", "Other"


class PropertyDataSource(models.TextChoices):
    # If we found data for this property from a third party, what was it?
    EPC = "EPC", "EPC"
    HA = "HA", "Home Analytics"


class PropertyType(models.TextChoices):
    FLAT = "FLAT", "Flat"
    MAISONETTE = "MAISONETTE", "Maisonette"
    HOUSE = "HOUSE", "House"
    BUNGALOW = "BUNGALOW", "Bungalow"
    PARK_HOME = "PARK_HOME", "Park Home"


class PropertyForm(models.TextChoices):
    DETACHED = "DETACHED", "Detached"
    SEMI_DETACHED = "SEMI", "Semi-detached"
    MID_TERRACE = "MID_TERRACE", "Mid-terrace"
    END_TERRACE = "END_TERRACE", "End-terrace"


class PropertyAgeBand(models.IntegerChoices):
    # We can use an integer field to parse numerical values into bands
    BEFORE_1900 = 0, "Before 1900"
    FROM_1900 = 1900, "1900-1929"
    FROM_1930 = 1930, "1930-1949"
    FROM_1950 = 1950, "1950-1966"
    FROM_1967 = 1967, "1967-1975"
    FROM_1976 = 1976, "1976-1990"
    FROM_1991 = 1991, "1991-2002"
    SINCE_2003 = 2003, "Since 2003"


class WallType(models.TextChoices):
    SOLID = "SOLID", "Solid walls"
    CAVITY = "CAVITY", "Cavity walls"


class Consents(models.TextChoices):
    CALL_BACK = "CALLBACK", "To call/email you back to provide advice"
    RETAIN_DETAILS = (
        "RETAIN",
        (
            "To hold your details on file and contact you when we think there are schemes "
            "that are relevant for you"
        ),
    )
    ANONYMOUS_REPORTING = (
        "REPORTING",
        (
            "To use in anonymised reporting that relates to the energy efficiency "
            "of properties in the Plymouth City Council administrative area"
        ),
    )

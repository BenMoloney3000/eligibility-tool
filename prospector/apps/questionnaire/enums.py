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
    FLAT = "FLAT", "Flat or maisonette"
    HOUSE = "HOUSE", "House"
    BUNGALOW = "BUNGALOW", "Bungalow"
    PARK_HOME = "PARK_HOME", "Park Home"


class PropertyForm(models.TextChoices):
    DETACHED = "DETACHED", "Detached"
    SEMI_DETACHED = "SEMI_DETACHED", "Semi-detached"
    MID_TERRACE = "MID_TERRACE", "Mid-terrace"
    END_TERRACE = "END_TERRACE", "End-terrace"
    MAISONNETTE = "MAISONNETTE", "Maisonette"
    FLAT_SMALL = "FLAT_CONVERSION", "Flat (converted house or block of 5 or less flats)"
    FLAT_BLOCK = (
        "FLAT_BLOCK",
        "Flat (block of 5 or more flats or flat in mixed use building)",
    )


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


class NonGasFuel(models.TextChoices):
    OIL = "OIL", "Oil"
    LPG = "LPG", "LPG"
    COAL = "COAL", "Coal"
    WOOD = "WOOD", "Wood"
    ELECTRICITY = "ELECTRIC", "Electricity"
    DISTRICT = "DISTRICT", "Shared/district heating network"


class BoilerAgeBand(models.TextChoices):
    BEFORE_2004 = "BEFORE_2004", "Before 2004"
    FROM_2004 = "2004-2014", "Between 2004 and 2014 (inclusive)"
    FROM_2015 = "2015-2017", "Between 2015 and 2017 (inclusive)"
    FROM_2018 = "AFTER_2018", "Since 2018"


class Consent(models.TextChoices):
    CALL_BACK = "CALLBACK", "To call/email you back to provide advice"
    RETAIN_DETAILS = (
        "RETAIN",
        (
            "To hold your details on file and contact you when we think there are schemes "
            "that are relevant for you"
        ),
    )
    ASSESS_ELIGIBILITY = (
        "ASSESS",
        "To use the details you have provided to assess eligibility for current schemes",
    )
    ANONYMOUS_REPORTING = (
        "REPORTING",
        (
            "To use in anonymised reporting that relates to the energy efficiency "
            "of properties in the Plymouth City Council administrative area"
        ),
    )


class HeatingSystemControls(models.IntegerChoices):
    """These are taken from SAP table 4e.

    - see https://www.bre.co.uk/filelibrary/SAP/2012/SAP-2012_9-92.pdf
    """

    NO_HEATING_SYSTEM = 2699, "No heating system present"
    DHW_ONLY = 2100, "Not applicable (boiler or HP provides DHW only)"

    # GROUP 1: BOILER SYSTEMS WITH RADIATORS OR UNDERFLOOR HEATING (and micro-CHP)
    BOILER_NO_CONTROLS = 2101, "No time or thermostatic control of room temperature"
    BOILER_PROGRAMMER = 2102, "Programmer, no room thermostat"
    BOILER_ROOM_THERMOSTAT = 2103, "Room thermostat only"
    BOILER_PROGRAMMER_AND_ROOM = 2104, "Programmer and room thermostat"
    BOILER_PROGRAMMER_AND_ROOMS = 2105, "Programmer and at least two room thermostats"
    BOILER_PROGRAMMER_ROOM_TRVS = 2106, "Programmer, room thermostat and TRVs"
    BOILER_TRVS_BYPASS = 2111, "TRVs and bypass"
    BOILER_PROGRAMMER_TRVS_BYPASS = 2107, "Programmer, TRVs and bypass"
    BOILER_PROGRAMMER_TRVS_FLOW_SWITCH = 2108, "Programmer, TRVs and flow switch"
    BOILER_PROGRAMMER_TRVS_BEM = 2109, "Programmer, TRVs and boiler energy manager"
    BOILER_TIME_AND_TEMP_SERVICES = (
        2110,
        "Time and temperature zone control by suitable arrangement of plumbing and electrical services",
    )
    BOILER_TIME_AND_TEMP_DEVICE = (
        2112,
        "Time and temperature zone control by device in database",
    )

    # GROUP 2: HEAT PUMPS WITH RADIATORS OR UNDERFLOOR HEATING
    HP_NO_CONTROLS = 2201, "No time or thermostatic control of room temperature"
    HP_PROGRAMMER = 2202, "Programmer, no room thermostat"
    HP_ROOM_THERMOSTAT = 2203, "Room thermostat only"
    HP_PROGRAMMER_AND_ROOM = 2204, "Programmer and room thermostat"
    HP_PROGRAMMER_AND_ROOMS = 2205, "Programmer and at least two room thermostats"
    HP_PROGRAMMER_TRVS_BYPASS = 2206, "Programmer, TRVs and bypass"
    HP_TIME_AND_TEMP_SERVICES = (
        2207,
        "Time and temperature zone control by suitable arrangement of plumbing and electrical services",
    )
    HP_TIME_AND_TEMP_DEVICE = (
        2208,
        "Time and temperature zone control by device in database",
    )

    # GROUP 3: COMMUNITY HEATING SCHEMES
    DHS_FLAT_RATE_NO_CONTROL = (
        2301,
        "Flat rate charging, no thermostatic control of room temperature",
    )
    DHS_FLAT_RATE_PROGRAMMER = (
        2302,
        "Flat rate charging, programmer, no room thermostat",
    )
    DHS_FLAT_RATE_ROOM_ONLY = 2303, "Flat rate charging, room thermostat only"
    DHS_FLAT_RATE_PROGRAMMER_ROOM = (
        2304,
        "Flat rate charging, programmer and room thermostat",
    )
    DHS_FLAT_RATE_TRVS = 2307, "Flat rate charging, TRVs"
    DHS_FLAT_RATE_PROGRAMMER_TRVS = 2305, "Flat rate charging, programmer and TRVs"
    DHS_FLAT_RATE_PROGRAMMER_ROOMS = (
        2311,
        "Flat rate charging*, programmer and at least two room thermostats",
    )
    DHS_USE_CHARGE_ROOM = (
        2308,
        "Charging system linked to use of community heating, room thermostat only",
    )
    DHS_USE_CHARGE_PROGRAMMER_ROOM = (
        2309,
        "Charging system linked to use of community heating, programmer and room thermostat",
    )
    DHS_USE_CHARGE_TRVS = (
        2310,
        "Charging system linked to use of community heating, TRVs",
    )
    DHS_USE_CHARGE_PROGRAMMER_TRVS = (
        2306,
        "Charging system linked to use of community heating, programmer and TRVs",
    )
    DHS_USE_CHARGE_PROGRAMMER_ROOM2 = (
        2312,
        "Charging system linked to use of community heating, programmer and at least two room thermostats",
    )

    # GROUP 4: ELECTRIC STORAGE SYSTEMS
    STORAGE_MANUAL = 2401, "Manual charge control"
    STORAGE_AUTOMATIC = 2402, "Automatic charge control"
    STORAGE_CELECT = 2403, "Celect-type controls"
    STORAGE_HHRSH = 2404, "Controls for high heat retention storage heaters"

    # GROUP 5: WARM AIR SYSTEMS (including heat pumps with warm air distribution)
    AIR_NO_CONTROL = 2501, "No time or thermostatic control of room temperature"
    AIR_PROGRAMMER = 2502, "Programmer, no room thermostat"
    AIR_ROOM = 2503, "Room thermostat only"
    AIR_PROGRAMMER_ROOM = 2504, "Programmer and room thermostat"
    AIR_PROGRAMMER_ROOMS = 2505, "Programmer and at least two room thermostats"
    AIR_TIME_AND_TEMP_ZONED = 2506, "Time and temperature zone control"

    # GROUP 6: ROOM HEATER SYSTEMS
    ROOM_NO_CONTROL = 2601, "No thermostatic control of room temperature"
    ROOM_APPLIANCE = 2602, "Appliance thermostats"
    ROOM_PROGRAMMER_APPLIANCE = 2603, "Programmer and appliance thermostats"
    ROOM_ROOM = 2604, "Room thermostats only"
    ROOM_PROGRAMMER_ROOM = 2605, "Programmer and room thermostats"

    # GROUP 7: OTHER SYSTEMS
    OTHER_NO_CONTROL = 2701, "No time or thermostatic control of room temperature"
    OTHER_PROGRAMMER = 2702, "Programmer, no room thermostat"
    OTHER_ROOM = 2703, "Room thermostat only"
    OTHER_PROGRAMMER_ROOM = 2704, "Programmer and room thermostat"
    OTHER_TEMP_ZONED = 2705, "Temperature zone control"
    OTHER_TIME_AND_TEMP_ZONED = 2706, "Time and temperature zone control"


class ToleratedDisruption(models.TextChoices):
    UP_TO_ONE_DAY = (
        "UP_TO_ONE_DAY",
        "Jobs that take up to three hours inside home, up to one day outside home",
    )
    ONE_TO_FOUR_DAYS = (
        "ONE_TO_FOUR_DAYS",
        (
            "One or two days of work inside home, or three to four days taking place "
            "on exterior to property (involving scaffolding etc.)"
        ),
    )
    THREE_TO_TEN_DAYS = (
        "THREE_TO_TEN_DAYS",
        "Up to five days of work inside home, up to ten days outside the home",
    )
    TWO_WEEKS_TO_A_MONTH = (
        "TWO_WEEKS_TO_A_MONTH",
        "Up to two weeks of work inside home, up to one month outside the home",
    )


class PossibleMeasures(models.TextChoices):
    CAVITY_WALL_INSULATION = "CAVITY_WALL_INSULATION", "Cavity wall insulation"
    SOLID_WALL_INSULATION = "SOLID_WALL_INSULATION", "Solid wall insulation"
    UNDERFLOOR_INSULATION = (
        "UNDERFLOOR_INSULATION",
        "Underfloor insulation for suspended floors",
    )
    RIR_INSULATION = "RIR_INSULATION", "Room-in-roof insulation"
    FLAT_ROOF_INSULATION = "FLAT_ROOF_INSULATION", "Flat roof insulation"
    BOILER_UPGRADE = "BOILER_UPGRADE", "Boiler upgrade"
    STORAGE_HEATER_UPGRADE = (
        "STORAGE_HEATER_UPGRADE",
        "Replacement or upgrade or night storage heaters",
    )
    CENTRAL_HEATING_INSTALL = (
        "CENTRAL_HEATING_INSTALL",
        "Installation of a central heating system",
    )
    PARTY_WALL_INSULATION = "PARTY_WALL_INSULATION", "Party wall insulation"
    LOFT_INSULATION = "LOFT_INSULATION", "Additional insulation in loft space"

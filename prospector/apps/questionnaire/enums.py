from enum import auto

from django.db import models


class PropertyOwnership(models.TextChoices):
    OWNED = "OWNED", "The property is in private ownership"
    PRIVATE_TENANCY = "RENTAL", "The property is rented from a private landlord"
    SOCIAL_TENANCY = (
        "SOCIAL",
        (
            "The property is rented from a social landlord (eg. a housing "
            "association) or local authority"
        ),
    )


class RespondentRole(models.TextChoices):
    OWNER_OCCUPIER = (
        "OWNER",
        "I am the owner and live in the property",
    )
    TENANT = "TENANT", "I am a tenant"
    LANDLORD = "LANDLORD", "I am the landlord of the property and rent it out"
    OTHER = "OTHER", "I am filling this out on behalf of the tenant or owner"


class PropertyDataSource(models.TextChoices):
    # If we found data for this property from a third party, what was it?
    # Not currently used - Home Analytics was planned at project start but will
    # not be used, but this field will still be needed if we use Parity data
    # in future.
    EPC = "EPC", "EPC"
    HA = "HA", "Home Analytics"
    PDB = "PDB", "Parity Database"


# class PropertyTypeOld(models.TextChoices):
#     FLAT = "FLAT", "Flat or maisonette"
#     HOUSE = "HOUSE", "House"
#     BUNGALOW = "BUNGALOW", "Bungalow"
#     PARK_HOME = "PARK_HOME", "Park Home"


class PropertyType(models.TextChoices):
    FLAT = "Flat", "Flat"
    HOUSE = "House", "House"
    BUNGALOW = "Bungalow", "Bungalow"
    PARK_HOME = "ParkHome", "Park home"
    MAISONNETTE = "Maisonette", "Maisonette"


# class PropertyForm(models.TextChoices):
#     DETACHED = "DETACHED", "Detached"
#     SEMI_DETACHED = "SEMI_DETACHED", "Semi-detached"
#     MID_TERRACE = "MID_TERRACE", "Mid-terrace"
#     END_TERRACE = "END_TERRACE", "End-terrace"
#     MAISONNETTE = "MAISONNETTE", "Maisonette"
#     FLAT_SMALL = "FLAT_CONVERSION", "Flat (converted house or block of 5 or less flats)"
#     FLAT_BLOCK = (
#         "FLAT_BLOCK",
#         "Flat (block of 5 or more flats or flat in mixed use building)",
#     )


# Below defines attributes coresponding with Attachment field in ParityData model
class PropertyAttachment(models.TextChoices):
    DETACHED = "Detached", "Detached"
    SEMI_DETACHED = "SemiDetached", "Semi detached"
    MID_TERRACE = "MidTerrace", "Mid terrace"
    END_TERRACE = "EndTerrace", "End terrace"
    ENCLOSED_END_TERRACE = "EnclosedEndTerrace", "Enclosed end terrace"
    ENCLOSED_MID_TERRACE = "EnclosedMidTerrace", "Enclosed mid terrace"


# class PropertyAgeBand(models.TextChoices):
#     # We can use an integer field to parse numerical values into bands
#     BEFORE_1900 = 0, "Before 1900"
#     FROM_1900 = 1900, "1900-1929"
#     FROM_1930 = 1930, "1930-1949"
#     FROM_1950 = 1950, "1950-1966"
#     FROM_1967 = 1967, "1967-1975"
#     FROM_1976 = 1976, "1976-1990"
#     FROM_1991 = 1991, "1991-2002"
#     SINCE_2003 = 2003, "Since 2003"
#     UNKNOWN = "UNKNOWN", "I don't know"


class PropertyConstructionYears(models.TextChoices):
    BEFORE_1900 = 0, "Before 1900"
    FROM_1900 = 1900, "1900-1929"
    FROM_1930 = 1930, "1930-1949"
    FROM_1950 = 1950, "1950-1966"
    FROM_1967 = 1967, "1967-1975"
    FROM_1976 = 1976, "1976-1982"
    FROM_1983 = 1983, "1983-1990"
    FROM_1991 = 1991, "1991-1995"
    FROM_1996 = 1996, "1996-2002"
    FROM_2003 = 2003, "2003-2006"
    FROM_2007 = 2007, "2007-2011"
    FROM_2012 = 2012, "2012 onwards"


# class WallType(models.TextChoices):
#     SOLID = "SOLID", "Solid walls"
#     CAVITY = "CAVITY", "Cavity walls"


class WallConstruction(models.TextChoices):  # To replace WallType with Parity dataset
    CAVITY = "CAVITY", "Cavity"
    COB = "COB", "Cob"
    GRANITE = "GRANITE", "Granite"
    PARK_HOME = "PARK_HOME", "Park Home"
    SANDSTONE = "SANDSTONE", "Sandstone"
    SOLID_BRICK = "SOLID_BRICK", "Solid brick"
    SYSTEM = "SYSTEM", "System"
    TIMBER_FRAME = "TIMBER_FRAME", "Timber frame"


class WallInsulation(models.TextChoices):
    AS_BUILT = "AsBuilt", "As Built"
    EXTERNAL = "External", "External"
    FC = "FilledCavity", "Filled Cavity"
    FCE = "FilledCavityPlusExternal", "Filled Cavity Plus External"
    FCI = "FilledCavityPlusInternal", "Filled Cavity Plus Internal"
    INTERNAL = "Internal", "Internal"


class RoofConstruction(models.TextChoices):
    ADB = "AnotherDwellingAbove", "Another Dwelling Above"
    FLAT = "Flat", "Flat"
    PNLA = "PitchedNormalLoftAccess", "Pitched Normal Loft Access"
    PNNLA = "PitchedNormalNoLoftAccess", "Pitched Normal No Loft Access"
    PT = "PitchedThatched", "Pitched Thatched"
    PWSC = "PitchedWithSlopingCeiling", "Pitched With Sloping Ceiling"


class RoofInsulation(models.TextChoices):
    ADB = "AnotherDwellingAbove", "Another Dwelling Above"
    AS_BUILD = "AsBuilt", "As Build"
    MM_100 = "mm100", "100 mm"
    MM_12 = "mm12", "12 mm"
    MM_150 = "mm150", "150 mm"
    MM_200 = "mm200", "200 mm"
    MM_25 = "mm25", "25 mm"
    MM_250 = "mm250", "250 mm"
    MM_270 = "mm270", "270 mm"
    MM_300 = "mm300", "300 mm"
    MM_350 = "mm350", "350 mm"
    MM_400 = "mm400", "400 mm"
    MM_50 = "mm50", "50 mm"
    MM_75 = "mm75", "75 mm"
    NO_INSULATION = "None", "None"
    UNKNOWN = "Unknown", "Unknown"


class FloorConstruction(models.TextChoices):
    SOLID = "Solid", "Solid"
    SNT = "SuspendedNotTimber", "Suspended Not Timber"
    ST = "SuspendedTimber", "Suspended Timber"
    UNKNOWN = "Unknown", "Unknown"


class FloorInsulation(models.TextChoices):
    AS_BUILT = "AsBuilt", "As Built"
    RETRO_FITTED = "RetroFitted", "Retro Fitted"
    UNKNOWN = "Unknown", "Unknown"


class Glazing(models.TextChoices):
    DOUBLE_2002_PLUS = "Double2002orLater", "Double 2002 or later"
    DOUBLE_BEFORE_2002 = "DoubleBefore2002", "Double before 2002"
    DOUBLE_UNKNOWN = "DoubleButAgeUnknown", "Double but age unknown"
    NOT_DEFINED = "NotDefined", "Not Defined"
    SECONDARY = "Secondary", "Secondary"
    SINGLE = "Single", "Single"
    TRIPLE = "Triple", "Triple"


class Heating(models.TextChoices):
    BOILERS = "Boilers", "Boilers"
    COMMUNITY = "Community", "Community"
    EUF = "Electric underfloor", "Electric Under Floor"
    HP_WARM = "Heat pumps (warm air)", "Heat Pumps (Warm Air)"
    HP_WET = "Heat pumps (wet)", "Heat Pumps (Wet)"
    OTHER = "Other systems", "Other Systems"
    RH = "Room heaters", "Room Heaters"
    SH = "Storage heaters", "Storage Heaters"
    AIR = "Warm Air (not heat pump)", "Warm Air (Not Heat Pump)"


class MainFuel(models.TextChoices):
    ANTHRACITE = "Anthracite", "Anthracite"
    BWP = "BulkWoodPellets", "Bulk Wood Pellets"
    DFMW = "DualFuelMineralWood", "Dual Fuel Mineral Wood"
    EC = "ElectricityCommunity", "Electricity Community"
    ENC = "ElectricityNotCommunity", "Electricity Not Community"
    GBLPG = "GasBottledLPG", "Gas Bottled LPG"
    HCNC = "HouseCoalNotCommunity", "House Coal Not Community"
    LPGC = "LPGCommunity", "LPG Community"
    LPGNC = "LPGNotCommunity", "LPG Not Community"
    LPGSC = "LPGSpecialCondition", "LPG Special Condition"
    MGC = "MainsGasCommunity", "Mains Gas Community"
    MGNC = "MainsGasNotCommunity", "Mains Gas Not Community"
    OC = "OilCommunity", "Oil Community"
    ONC = "OilNotCommunity", "Oil Not Community"
    SC = "SmokelessCoal", "Smokeless Coal"
    WC = "WoodChips", "Wood Chips"
    WL = "WoodLogs", "Wood Logs"


class EfficiencyBand(models.TextChoices):
    A = "a", "A"
    B = "b", "B"
    C = "c", "C"
    D = "d", "D"
    E = "e", "E"
    F = "f", "F"
    G = "g", "G"


class ControlsAdequacy(models.TextChoices):
    OPTIMAL = "Optimal", "Optimal"
    SUB_OPTIMAL = "SubOptimal", "Sub Optimal"
    TOP_SPEC = "TopSpec", "Top Spec"


class InsulationConfidence(models.TextChoices):
    DEFINITELY = "DEFINITELY", "Yes definitely"
    PROBABLY = "PROBABLY", "Yes I think so"
    PROBABLY_NOT = "PROBABLY_NOT", "I think not"
    DEFINITELY_NOT = "DEFINITELY_NOT", "I know it isn't"
    UNKNOWN = "UNKNOWN", "I don't know"


class NonGasFuel(models.TextChoices):
    OIL = "OIL", "Oil"
    LPG = "LPG", "LPG (Liquified Petroleum Gas)"
    COAL = "COAL", "Coal"
    WOOD = "WOOD", "Wood"
    ELECTRICITY = "ELECTRIC", "Electricity"
    DISTRICT = "DISTRICT", "Via a shared or district heating network"


class BoilerAgeBand(models.TextChoices):
    BEFORE_2004 = "BEFORE_2004", "Before 2004"
    FROM_2004 = "2004-2014", "Between 2004 and 2014 (including those years)"
    FROM_2015 = "2015-2017", "Between 2015 and 2017 (including those years)"
    FROM_2018 = "AFTER_2018", "Since 2018"


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
        (
            "Jobs that take up to three hours inside the property and/or up to "
            "one day outside the property"
        ),
    )
    ONE_TO_FOUR_DAYS = (
        "ONE_TO_FOUR_DAYS",
        (
            "One or two days of work inside the property and/or three to four "
            "days outside the property (for example involving scaffolding etc.)"
        ),
    )
    THREE_TO_TEN_DAYS = (
        "THREE_TO_TEN_DAYS",
        (
            "Up to five days of work inside the property and/or up to ten days "
            "outside the property"
        ),
    )
    TWO_WEEKS_TO_A_MONTH = (
        "TWO_WEEKS_TO_A_MONTH",
        (
            "Up to two weeks of work inside the property and/or up to one month "
            "outside the property"
        ),
    )
    UNKNOWN = "UNKNOWN", "I don't know."


class ContributionCapacity(models.TextChoices):
    NONE = "NONE", "No"
    UP_TO_500 = "UP_TO_500", "Yes - up to £500"
    UP_TO_5K = "UP_TO_5K", "Yes - up to £5,000"
    UP_TO_10K = "UP_TO_10K", "Yes - up to £10,000"
    OVER_10K = "OVER_10K", "Yes - more than £10,000"
    UNKNOWN = "UNKNOWN", "I don't know"


class StateOfRepair(models.TextChoices):
    EXCELLENT = (
        "EXCELLENT",
        (
            "Excellent – recently renovated and the walls, roofs, windows, "
            "doors and ventilation (for example fans) are in good condition."
        ),
    )
    GOOD = (
        "GOOD",
        (
            "Good – there are no issues with the house and I have ventilation "
            "in the kitchen and bathrooms."
        ),
    )
    AVERAGE = (
        "AVERAGE",
        (
            "Average – there are no issues with the house but I don’t know if I "
            "have enough ventilation and I don’t know what condition the external "
            "elements (such as roofs, walls and windows) are in."
        ),
    )
    POOR = (
        "POOR",
        (
            "Poor – There are known issues with the property such as damp or "
            "leaks and/or there is no formal ventilation."
        ),
    )
    UNKNOWN = "UNKNOWN", "I don't know the state of repair of the property."


class OneToFourOrMore(models.IntegerChoices):
    ONE = 1, "1"
    TWO = 2, "2"
    THREE = 3, "3"
    FOUR = 4, "4 or more"


class UpToFourOrMore(models.IntegerChoices):
    NONE = 0, "None"
    ONE = 1, "1"
    TWO = 2, "2"
    THREE = 3, "3"
    FOUR = 4, "4 or more"


class IncomeIsUnderThreshold(models.TextChoices):
    YES = "YES", "Yes, it's under that figure"
    NO = "NO", "No, it's over that figure"
    UNKNOWN = "UNKNOWN", "I don't know"


class PossibleMeasures(models.TextChoices):
    CAVITY_WALL_INSULATION = "CAVITY_WALL_INSULATION", "Cavity wall insulation"
    SOLID_WALL_INSULATION = "SOLID_WALL_INSULATION", "Solid wall insulation"
    UNDERFLOOR_INSULATION = (
        "UNDERFLOOR_INSULATION",
        "Underfloor insulation for suspended floors",
    )
    RIR_INSULATION = "RIR_INSULATION", "Room-in-roof insulation"
    FLAT_ROOF_INSULATION = "FLAT_ROOF_INSULATION", "Flat roof insulation"
    BOILER_UPGRADE = "BOILER_UPGRADE", "A low carbon heating upgrade"
    STORAGE_HEATER_UPGRADE = (
        "STORAGE_HEATER_UPGRADE",
        "Replacement or upgrade or night storage heaters",
    )
    CENTRAL_HEATING_INSTALL = (
        "CENTRAL_HEATING_INSTALL",
        "Installation of a central heating system",
    )
    BROKEN_BOILER_UPGRADE = "BROKEN_BOILER_UPGRADE", "A low carbon heating upgrade"
    PARTY_WALL_INSULATION = "PARTY_WALL_INSULATION", "Party wall insulation"
    LOFT_INSULATION = "LOFT_INSULATION", "Additional insulation in loft space"
    HEAT_PUMP_INSTALL = "HEAT_PUMP_INSTALL", "Installation of a heat pump"


class EmploymentStatus(models.TextChoices):
    EMPLOYED = "EMPLOYED", "Employed"
    SELF_EMPLOYED = "SELF_EMPLOYED", "Self Employed"
    UNEMPLOYED = "UNEMPLOYED", "Unemployed"
    RETIRED = "RETIRED", "Retired"
    OTHER = "OTHER", "Other"


class PaymentFrequency(models.TextChoices):
    ANNUALLY = "ANNUALLY", "annually"
    MONTHLY = "MONTHLY", "monthly"


class BenefitPaymentFrequency(models.TextChoices):
    WEEKLY = "WEEKLY", "weekly"
    TWO_WEEKLY = "TWO_WEEKLY", "two weekly"
    FOUR_WEEKLY = "FOUR_WEEKLY", "four weekly"
    ANNUALLY = "ANNUALLY", "annually"
    MONTHLY = "MONTHLY", "monthly"


class BenefitType(models.TextChoices):
    UC = "UC", "Universal Credit"
    JSA = "JSA", "Job Seekers Allowance (JSA)"
    ESA = "ESA", "Employment and Support Allowance (ESA)"
    INCOME_SUPPORT = "INCOME_SUPPORT", "Income Support"
    CHILD_TAX_CREDIT = "CHILD_TAX_CREDIT", "Child Tax Credit"
    WORKING_TAX_CREDIT = "WORKING_TAX_CREDIT", "Working Tax Credit"
    CHILD_BENEFIT = "CHILD_BENEFIT", "Child Benefit"
    HOUSING_BENEFIT = "HOUSING_BENEFIT", "Housing Benefit"
    ATTENDANCE_ALLOWANCE = "ATTENDANCE_ALLOWANCE", "Attendance Allowance"
    CARERS_ALLOWANCE = "CARERS_ALLOWANCE", "Carers Allowance"
    DLA = "DLA", "Disability Living Allowance (DLA)"
    PIP = "PIP", "Personal Independence Payment (PIP)"
    PENSION_CREDIT = "PENSION_CREDIT", "Pension Credit"
    OTHER = "OTHER", "Other"


class ChildBenefitClaimantType(models.TextChoices):
    SINGLE = "SINGLE", "Single Claimant"
    JOINT = "JOINT", "Joint Claimant"


class RAYG(models.TextChoices):
    RED = auto()
    AMBER = auto()
    YELLOW = auto()
    GREEN = auto()


class FinancialEligibility(models.TextChoices):
    ALL = "ALL", "Financial circumstances eligible for all schemes"
    SOME = "SOME", "Financial circumstances eligible for some schemes"
    NONE = "NONE", "Financial circumstances eligible for no schemes"


class TRVsPresent(models.TextChoices):
    ALL = "ALL", "All radiators have TRVs"
    SOME = "SOME", "Some radiators have TRVs"
    NONE = "NONE", "No TRVs present"

from django.db import models


class ChildBenefitClaimantType(models.TextChoices):
    SINGLE = "SINGLE", "Single claimant"
    JOINT = "JOINT", "Member of a couple"


class ControlsAdequacy(models.TextChoices):
    OPTIMAL = "Optimal", "Optimal"
    SUB_OPTIMAL = "Sub Optimal", "Sub optimal"
    TOP_SPEC = "Top Spec", "Top spec"


class CouncilTaxBand(models.TextChoices):
    A = "A", "A"
    B = "B", "B"
    C = "C", "C"
    D = "D", "D"
    E = "E", "E"
    F = "F", "F"
    G = "G", "G"
    H = "H", "H"


class EfficiencyBand(models.TextChoices):
    A = "A", "A"
    B = "B", "B"
    C = "C", "C"
    D = "D", "D"
    E = "E", "E"
    F = "F", "F"
    G = "G", "G"


class FloorConstruction(models.TextChoices):
    SOLID = "Solid", "Solid"
    SNT = "SuspendedNotTimber", "Suspended - not timber"
    ST = "SuspendedTimber", "Suspended - timber"
    UNKNOWN = "Unknown", "Unknown"


class FloorInsulation(models.TextChoices):
    AS_BUILT = "AsBuilt", "As built"
    RETRO_FITTED = "RetroFitted", "Retrofitted"
    UNKNOWN = "Unknown", "Unknown"


class Glazing(models.TextChoices):
    DOUBLE_2002_PLUS = "Double 2002 or later", "Double 2002 or later"
    DOUBLE_BEFORE_2002 = "Double before 2002", "Double before 2002"
    DOUBLE_UNKNOWN = "Double but age unknown", "Double but age unknown"
    NOT_DEFINED = "NotDefined", "Not Defined"
    SECONDARY = "Secondary", "Secondary"
    SINGLE = "Single", "Single"
    TRIPLE = "Triple", "Triple"


class Heating(models.TextChoices):
    BOILERS = "Boilers", "Boilers"
    COMMUNITY = "Community", "Community"
    EUF = "Electric underfloor", "Electric underfloor"
    HP_WARM = "Heat pumps (warm air)", "Heat pumps (warm air)"
    HP_WET = "Heat pumps (wet)", "Heat pumps (wet)"
    OTHER = "Other systems", "Other systems"
    RH = "Room heaters", "Room heaters"
    SH = "Storage heaters", "Storage heaters"
    AIR = "Warm Air (not heat pump)", "Warm air (not heat pump)"


class HowDidYouHearAboutPEC(models.TextChoices):
    DOOR_KNOCKING = "Door knocking", "Door knocking"
    FACEBOOK = "Facebook", "Facebook"
    FLYER = "Flyer/poster", "Flyer or poster"
    INSTAGRAM = "Instagram", "Instagram"
    LETTER = "Letter in the post", "Letter in the post"
    LINKEDIN = "LinkedIn", "LinkedIn"
    PRINT_MEDIA = "Print media", "Newspaper or magazine"
    PRIOR_RELATIONSHIP = "Prior relationship with PEC", "Prior relationship with PEC"
    RADIO = "Radio", "Radio"
    SIGNPOST_CO = (
        "Signpost - Community organisation",
        "Referred by community organisation",
    )
    SIGNPOST_CHARITY = "Signpost - Charity", "Referred by charity"
    SIGNPOST_COUNCIL = "Signpost - Council", "Referred by council"
    SIGNPOST_LB = "Signpost - Local business", "Referred by local business"
    TWITTER = "Twitter", "X, formerly known as Twitter"
    WEB_SEARCH = "Web search", "Web search"
    BUSINESS_CARD_IN_SHOP = "Business card in shop", "Business card in shop"
    WORD_OF_MOUTH = "Word of mouth", "Word of mouth"
    NOT_SPECIFIED = "Not Yet Specified", "Other"
    LABEL = "Input label", "Please choose option"


class MainFuel(models.TextChoices):
    ANTHRACITE = "Anthracite", "Anthracite"
    BWP = "BulkWoodPellets", "Bulk wood pellets"
    DFMW = "DualFuelMineralWood", "Dual fuel mineral wood"
    EC = "ElectricityCommunity", "Electricity - community"
    ENC = "ElectricityNotCommunity", "Electricity - not community"
    GBLPG = "GasBottledLPG", "Bottled gas (LPG)"
    HCNC = "HouseCoalNotCommunity", "Coal - not community"
    LPGC = "LPGCommunity", "LPG - community"
    LPGNC = "LPGNotCommunity", "LPG - not community"
    LPGSC = "LPGSpecialCondition", "LPG - special condition"
    MGC = "MainsGasCommunity", "Mains gas - community"
    MGNC = "MainsGasNotCommunity", "Mains gas - not community"
    OC = "OilCommunity", "Oil - community"
    ONC = "OilNotCommunity", "Oil - not community"
    SC = "SmokelessCoal", "Smokeless coal"
    WC = "WoodChips", "Wood chips"
    WL = "WoodLogs", "Wood logs"


class OneToFiveOrMore(models.IntegerChoices):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class OneToTen(models.IntegerChoices):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10


class OneToTenOrNone(models.IntegerChoices):
    NONE = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10


class PossibleMeasures(models.TextChoices):
    CAVITY_WALL_INSULATION = "CAVITY_WALL_INSULATION", "Cavity wall insulation"
    SOLID_WALL_INSULATION = "SOLID_WALL_INSULATION", "Solid wall insulation"
    UNDERFLOOR_INSULATION = (
        "UNDERFLOOR_INSULATION",
        "Underfloor insulation for suspended floors",
    )
    RIR_INSULATION = "RIR_INSULATION", "Room-in-roof insulation"
    BOILER_UPGRADE = "BOILER_UPGRADE", "A low carbon heating upgrade"
    SOLAR_PV_INSTALLATION = (
        "SOLAR_PV_INSTALLATION",
        "Installation of a solar electricity panels",
    )
    LOFT_INSULATION = "LOFT_INSULATION", "Additional insulation in loft space"
    HEAT_PUMP_INSTALLATION = "HEAT_PUMP_INSTALLATION", "Installation of a heat pump"


class PropertyAttachment(models.TextChoices):
    DETACHED = "Detached", "Detached"
    SEMI_DETACHED = "SemiDetached", "Semi detached"
    MID_TERRACE = "MidTerrace", "Mid terrace"
    END_TERRACE = "EndTerrace", "End terrace"
    ENCLOSED_END_TERRACE = "EnclosedEndTerrace", "Enclosed end terrace"
    ENCLOSED_MID_TERRACE = "EnclosedMidTerrace", "Enclosed mid terrace"


class PropertyConstructionYears(models.TextChoices):
    BEFORE_1900 = "Before 1900", "Before 1900"
    FROM_1900 = "1900-1929", "1900-1929"
    FROM_1930 = "1930-1949", "1930-1949"
    FROM_1950 = "1950-1966", "1950-1966"
    FROM_1967 = "1967-1975", "1967-1975"
    FROM_1976 = "1976-1982", "1976-1982"
    FROM_1983 = "1983-1990", "1983-1990"
    FROM_1991 = "1991-1995", "1991-1995"
    FROM_1996 = "1996-2002", "1996-2002"
    FROM_2003 = "2003-2006", "2003-2006"
    FROM_2007 = "2007-2011", "2007-2011"
    FROM_2012 = "2012 onwards", "2012 onwards"


class PropertyType(models.TextChoices):
    FLAT = "Flat", "Flat"
    HOUSE = "House", "House"
    BUNGALOW = "Bungalow", "Bungalow"
    PARK_HOME = "ParkHome", "Park home"
    MAISONNETTE = "Maisonette", "Maisonette"


class RespondentRole(models.TextChoices):
    OWNER_OCCUPIER = (
        "OWNER",
        "I am the owner and live in the property",
    )
    TENANT = "TENANT", "I am a tenant"
    LANDLORD = "LANDLORD", "I am the landlord of the property and rent it out"
    OTHER = "OTHER", "I am filling this out on behalf of the tenant or owner"


class RoofConstruction(models.TextChoices):
    ADB = "AnotherDwellingAbove", "Another dwelling above"
    FLAT = "Flat", "Flat"
    PNLA = "PitchedNormalLoftAccess", "Pitched - loft access"
    PNNLA = "PitchedNormalNoLoftAccess", "Pitched - no loft access"
    PT = "PitchedThatched", "Pitched thatched"
    PWSC = "PitchedWithSlopingCeiling", "Pitched with sloping ceiling"


class RoofInsulation(models.TextChoices):
    ADB = "Another Dwelling Above", "Another dwelling above"
    AS_BUILD = "AsBuilt", "As built"
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


class Tenure(models.TextChoices):
    OWNER_OCCUPIED = "OwnerOccupied", "Owner-occupied"
    RENTED_PRIVATE = "RentedPrivate", "Rented - private"
    RENTED_SOCIAL = "RentedSocial", "Rented - social"
    UNKNOWN = "Unknown", "Unknown"


class WallConstruction(models.TextChoices):
    CAVITY = "Cavity", "Cavity"
    COB = "Cob", "Cob"
    GRANITE = "Granite", "Granite"
    PARK_HOME = "Park Home", "Park home"
    SANDSTONE = "Sandstone", "Sandstone"
    SOLID_BRICK = "Solid Brick", "Solid brick"
    SYSTEM = "System", "System"
    TIMBER_FRAME = "Timber Frame", "Timber frame"


class WallInsulation(models.TextChoices):
    AS_BUILT = "AsBuilt", "As built"
    EXTERNAL = "External", "External wall insulation"
    FC = "FilledCavity", "Filled cavity"
    FCE = "FilledCavityPlusExternal", "Filled cavity plus external wall insulation"
    FCI = "FilledCavityPlusInternal", "Filled cavity plus internal wall insulation"
    INTERNAL = "Internal", "Internal wall insulation"


# Deprecated but in use in ./migrations/0036_data_migration_trvs_present.py
# DO NOT REMOVE
class TRVsPresent(models.TextChoices):
    ALL = "ALL", "All radiators have TRVs"
    SOME = "SOME", "Some radiators have TRVs"
    NONE = "NONE", "No TRVs present"

import json
import logging
import urllib.parse
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import models

logger = logging.getLogger(__name__)


def get_crm_settings():
    unconfigured_settings = False
    if not getattr(settings, "CRM_API", False):
        logger.error("CRM_API Django settings not set.")
        unconfigured_settings = True

    for setting in ["CLIENT_ID", "CLIENT_SECRET", "TENANT"]:
        if not settings.CRM_API.get(setting):
            unconfigured_settings = True
            logger.error("CRM_API[%s] Django setting is not set." % (setting))

    if unconfigured_settings:
        raise ImproperlyConfigured("No CRM_API settings configured")

    return settings.CRM_API


def get_settings():
    crm_api = get_crm_settings()
    return {
        "client_id": crm_api["CLIENT_ID"],
        "client_secret": crm_api["CLIENT_SECRET"],
        "resource": crm_api["RESOURCE"],
        "token_url": (
            "https://login.microsoftonline.com/%s/oauth2/token" % (crm_api["TENANT"])
        ),
        "include_client_id": True,
    }


def get_client():
    settings = get_settings()
    return BackendApplicationClient(client_id=settings["client_id"])


def get_authorised_session(client):
    settings = get_settings()
    session = OAuth2Session(client=client)
    session.fetch_token(**settings)
    return session


def crm_request(session, query, params={}, json={}, request_method="GET"):
    crm_api = get_crm_settings()

    url = "%sapi/data/v9.1/%s" % (crm_api["RESOURCE"], query)
    encoded_params = urllib.parse.urlencode(
        params, quote_via=urllib.parse.quote, safe="$,"
    )
    headers = {
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "prefer": "return=representation",
    }

    return session.request(
        request_method,
        url,
        timeout=15,
        params=encoded_params,
        json=json,
        headers=headers,
    ).json()


def get_pcc_fields(client):
    query = "EntityDefinitions(LogicalName='pcc_retrofitintermediate')/Attributes"
    params = {
        "$select": ",".join(
            [
                "DisplayName",
                "LogicalName",
                "AttributeType",
                "SchemaName",
                "IsCustomAttribute",
                "IsValidODataAttribute",
                "EntityLogicalName",
                "AttributeOf",
                "AttributeType",
                "AttributeTypeName",
                "IsPrimaryId",
                "IsRequiredForForm",
            ]
        ),
        "$filter": "IsValidODataAttribute eq true and IsValidForCreate eq true",
    }
    return crm_request(client, query, params=params)


def get_pcc_picklist(client):
    query = "EntityDefinitions(LogicalName='pcc_retrofitintermediate')"
    params = {
        "$select": "LogicalName",
        "$expand": (
            "Attributes("
            "$select=LogicalName;"
            "$filter=AttributeType eq "
            "Microsoft.Dynamics.CRM.AttributeTypeCode'Picklist'"
            ")"
        ),
    }
    return crm_request(client, query, params=params)


def get_pcc_optionset(client):
    query = (
        "EntityDefinitions(LogicalName='pcc_retrofitintermediate')"
        "/Attributes/Microsoft.Dynamics.CRM.PicklistAttributeMetadata"
    )
    params = {
        "$select": "LogicalName",
        "$expand": "OptionSet,GlobalOptionSet",
    }
    return crm_request(client, query, params=params)


def load_crm_metadata(name):
    path = Path(__file__).parent / name
    with path.open() as f:
        return json.load(f)


def pcc_picklists():
    optionsets = load_crm_metadata("optionsets.json")

    def get_label(option):
        return option["Label"]["UserLocalizedLabel"]["Label"]

    picklists = {
        o["LogicalName"]: {get_label(p): p["Value"] for p in o["OptionSet"]["Options"]}
        for o in optionsets["value"]
    }

    return picklists


def pcc_entities():
    entity_definitions = load_crm_metadata("entity_definitions.json")
    picklist_definitions = pcc_picklists()

    def get_label(entity):
        return entity["DisplayName"]["UserLocalizedLabel"]["Label"]

    fields = {}
    for entity in entity_definitions["value"]:
        logical_name = entity["LogicalName"]

        picklist = {}
        if entity["AttributeType"] == "Picklist":
            picklist = {"picklist": picklist_definitions[logical_name]}

        fields[logical_name] = {
            "Label": get_label(entity),
            "AttributeType": entity["AttributeType"],
            "IsPrimaryId": entity["IsPrimaryId"],
            **picklist,
        }

    return fields


def pcc_entity_types():
    entity_definitions = load_crm_metadata("entity_definitions.json")
    types = []
    for entity in entity_definitions["value"]:
        types.append(entity["AttributeType"])
    return set(types)


def option_value(logical_name, choice_name):
    return pcc_entities()[logical_name]["picklist"][choice_name]


def option_value_mapping(
    logical_name, value, mapping, default=None, default_mapping=None
):
    crm_choice_name = mapping.get(value, default_mapping)
    if crm_choice_name is not None:
        return option_value(logical_name, crm_choice_name)
    return default


def map_crm(answers: models.Answers) -> dict:
    STATUSCODE_SUBMITTED = "798360000"
    STATECODE_ACTIVE = "0"

    def tco2current():
        if answers.t_co2_current is None:
            return None
        return float(answers.t_co2_current)

    crm_data = {
        # Metadata
        "statuscode": STATUSCODE_SUBMITTED,
        "statecode": STATECODE_ACTIVE,
        # CRM Links / Metadata
        "pcc_name": str(answers.uuid),
        # Domestic Property
        "pcc_street1": answers.property_address_1,
        "pcc_street2": answers.property_address_2,
        "pcc_street3": answers.property_address_3,
        "pcc_towncity": "PLYMOUTH",
        "pcc_county": None,  # Leave blank
        "pcc_postcode": answers.property_postcode,
        "pcc_udprn": answers.property_udprn,
        "pcc_likelihoodofprivatelyrented": (
            option_value_mapping(
                "pcc_likelihoodofprivatelyrented",
                answers.tenure,
                {
                    enums.Tenure.RENTED_PRIVATE: "High",
                },
                default_mapping="Low",
            )
        ),
        "pcc_inscopeformees": None,  # Leave blank
        "pcc_primaryheatingfuel": (
            option_value_mapping(
                "pcc_primaryheatingfuel",
                answers.main_fuel,
                {
                    enums.MainFuel.ANTHRACITE: "Anthracite",
                    enums.MainFuel.BWP: "Bulk wood pellets",
                    enums.MainFuel.DFMW: "Dual Fuel Mineral Wood",
                    enums.MainFuel.EC: "Electricity - community",
                    enums.MainFuel.ENC: "Electricity - not community",
                    enums.MainFuel.GBLPG: "Bottled gas (LPG)",
                    enums.MainFuel.HCNC: "Coal - not community",
                    enums.MainFuel.LPGC: "LPG - community",
                    enums.MainFuel.LPGNC: "LPG - not community",
                    enums.MainFuel.LPGSC: "LPG - special condition",
                    enums.MainFuel.MGC: "Mains gas - community",
                    enums.MainFuel.MGNC: "Mains gas - not community",
                    enums.MainFuel.OC: "Oil - community",
                    enums.MainFuel.ONC: "Oil - not community",
                    enums.MainFuel.SC: "Smokeless coal",
                    enums.MainFuel.WC: "Wood - chips",
                    enums.MainFuel.WL: "Wood - logs",
                },
            )
        ),
        "pcc_primaryheatingdeliverymethod": (
            option_value_mapping(
                "pcc_primaryheatingdeliverymethod",
                answers.heating,
                {
                    enums.Heating.BOILERS: "Boilers",
                    enums.Heating.COMMUNITY: "Community",
                    enums.Heating.EUF: "Electric underfloor",
                    enums.Heating.HP_WARM: "Heat pumps (warm air)",
                    enums.Heating.HP_WET: "Heat pumps (wet)",
                    enums.Heating.OTHER: "Other systems",
                    enums.Heating.RH: "Room heaters",
                    enums.Heating.SH: "Storage heaters",
                    enums.Heating.AIR: "Warm Air (not heat pump)",
                },
            )
        ),
        "pcc_secondaryheatingfuel": None,  # Leave blank
        "pcc_secondaryheatingdeliverymethod": None,  # Leave blank
        "pcc_boilertype": None,
        "pcc_heatingcontrols": None,
        "pcc_solarpanels": None,
        "pcc_solarthermal": None,  # Leave blank
        "pcc_propertytype": (
            option_value_mapping(
                "pcc_propertytype",
                answers.property_type,
                {
                    enums.PropertyType.FLAT: "Flat",
                    enums.PropertyType.HOUSE: "House",
                    enums.PropertyType.BUNGALOW: "Bungalow",
                    enums.PropertyType.PARK_HOME: "Park home",
                    enums.PropertyType.MAISONNETTE: "Maisonette",
                },
            )
        ),
        "pcc_bedrooms": None,  # Leave blank
        "pcc_propertyage": (
            option_value_mapping(
                "pcc_propertyage",
                answers.property_construction_years,
                {
                    enums.PropertyConstructionYears.BEFORE_1900: "Before 1900",
                    enums.PropertyConstructionYears.FROM_1900: "1900-1929",
                    enums.PropertyConstructionYears.FROM_1930: "1930-1949",
                    enums.PropertyConstructionYears.FROM_1950: "1950-1966",
                    enums.PropertyConstructionYears.FROM_1967: "1967-1975",
                    enums.PropertyConstructionYears.FROM_1976: "1976-1982",
                    enums.PropertyConstructionYears.FROM_1983: "1983-1990",
                    enums.PropertyConstructionYears.FROM_1991: "1991-1995",
                    enums.PropertyConstructionYears.FROM_1996: "1996-2002",
                    enums.PropertyConstructionYears.FROM_2003: "2003-2006",
                    enums.PropertyConstructionYears.FROM_2007: "2007-2011",
                    enums.PropertyConstructionYears.FROM_2012: "2012 Onwards",
                },
            )
        ),
        "pcc_listedproperty": None,  # Leave blank
        "pcc_rooftype": (
            option_value_mapping(
                "pcc_rooftype",
                answers.roof_construction,
                {
                    enums.RoofConstruction.ADB: "Another dwelling above",
                    enums.RoofConstruction.FLAT: "Flat",
                    enums.RoofConstruction.PNLA: "Pitched - loft access",
                    enums.RoofConstruction.PNNLA: "Pitched - no loft access",
                    enums.RoofConstruction.PT: "Thatched",
                    enums.RoofConstruction.PWSC: "Pitched with sloping ceiling",
                },
            )
        ),
        "pcc_roofinsulation": (
            option_value_mapping(
                "pcc_roofinsulation",
                answers.roof_insulation,
                {
                    enums.RoofInsulation.ADB: "Another dwelling above",
                    enums.RoofInsulation.AS_BUILD: "AsBuilt",
                    enums.RoofInsulation.MM_100: "mm 100",
                    enums.RoofInsulation.MM_12: "mm 12",
                    enums.RoofInsulation.MM_150: "mm 150",
                    enums.RoofInsulation.MM_200: "mm 200",
                    enums.RoofInsulation.MM_25: "mm 25",
                    enums.RoofInsulation.MM_250: "mm 250",
                    enums.RoofInsulation.MM_270: "mm 270",
                    enums.RoofInsulation.MM_300: "mm 300",
                    enums.RoofInsulation.MM_350: "mm 350",
                    enums.RoofInsulation.MM_400: "mm 400",
                    enums.RoofInsulation.MM_50: "mm 50",
                    enums.RoofInsulation.MM_75: "mm 75",
                    enums.RoofInsulation.NO_INSULATION: "None",
                    enums.RoofInsulation.UNKNOWN: "Unknown",
                },
            )
        ),
        "pcc_floortype": (
            option_value_mapping(
                "pcc_floortype",
                answers.floor_construction,
                {
                    enums.FloorConstruction.SOLID: "Solid",
                    enums.FloorConstruction.SNT: "Suspended - not timber",
                    enums.FloorConstruction.ST: "Suspended - timber",
                    enums.FloorConstruction.UNKNOWN: "Unknown",
                },
            )
        ),
        "pcc_floorinsulation": (
            option_value_mapping(
                "pcc_floorinsulation",
                answers.floor_insulation,
                {
                    enums.FloorInsulation.AS_BUILT: "As built",
                    enums.FloorInsulation.RETRO_FITTED: "Retrofitted",
                    enums.FloorInsulation.UNKNOWN: "Unknown",
                },
            )
        ),
        "pcc_walltype": (
            option_value_mapping(
                "pcc_walltype",
                answers.wall_construction,
                {
                    enums.WallConstruction.CAVITY: "Cavity",
                    enums.WallConstruction.COB: "Cob",
                    enums.WallConstruction.GRANITE: "Granite",
                    enums.WallConstruction.PARK_HOME: "Park home",
                    enums.WallConstruction.SANDSTONE: "Sandstone",
                    enums.WallConstruction.SOLID_BRICK: "Solid brick",
                    enums.WallConstruction.SYSTEM: "System",
                    enums.WallConstruction.TIMBER_FRAME: "Timber frame",
                },
            )
        ),
        "pcc_wallinsulation": (
            option_value_mapping(
                "pcc_wallinsulation",
                answers.walls_insulation,
                {
                    enums.WallInsulation.AS_BUILT: "As built",
                    enums.WallInsulation.EXTERNAL: "External wall insulation",
                    enums.WallInsulation.FC: "Filled cavity",
                    enums.WallInsulation.FCE: "Filled cavity plus external wall insulation",
                    enums.WallInsulation.FC: "Filled cavity plus internal wall insulation",
                    enums.WallInsulation.INTERNAL: "Internal wall insulation",
                },
            )
        ),
        "pcc_glazing": (
            option_value_mapping(
                "pcc_glazing",
                answers.glazing,
                {
                    enums.Glazing.DOUBLE_2002_PLUS: "Double - 2002 or later",
                    enums.Glazing.DOUBLE_BEFORE_2002: "Double before 2002",
                    enums.Glazing.DOUBLE_UNKNOWN: "Double but age unknown",
                    enums.Glazing.NOT_DEFINED: "NotDefined",
                    enums.Glazing.SECONDARY: "Secondary",
                    enums.Glazing.SINGLE: "Single",
                    enums.Glazing.TRIPLE: "Triple",
                },
            )
        ),
        "pcc_propertyprofilecomments": None,  # Leave blank
        "pcc_epctype": None,  # Leave blank after Phase 3 changes
        "pcc_dateofmostrecentepc": None,  # leave blank
        "pcc_gradeofmostrecentepc": None,  # leave blank
        "pcc_scoreofmostrecentepc": None,  # Leave blank after Phase 3 changes
        "pcc_hasapgrade": None,
        "pcc_hasapscore": None,
        "pcc_mouldgrowth": None,
        "pcc_condensation": None,
        "pcc_structuraldamp": None,
        "pcc_commentsondamp": None,
        "pcc_occupanteligibilityscore": None,  # Leave blank after Phase 3 changes
        "pcc_propertyeligibilityscore": None,  # Leave blank after Phase 3 changes
        # Contact
        "pcc_salutation": None,
        "pcc_firstname": answers.occupant_details["first_name"],
        "pcc_lastname": answers.occupant_details["last_name"],
        "pcc_homephone": answers.occupant_details["phone"],
        "pcc_mobile": answers.occupant_details["mobile"],
        "pcc_email": answers.occupant_details["email"],
        "pcc_address1street1": answers.respondent_address_1,
        "pcc_address1street2": answers.respondent_address_2,
        "pcc_address1street3": None,
        "pcc_address1city": answers.respondent_address_3,
        "pcc_address1county": None,
        "pcc_address1zippostalcode": answers.respondent_postcode,
        "pcc_udprncontact": answers.respondent_udprn,
        # Occupier
        "pcc_occupiedfrom": None,
        "pcc_occupiedto": None,
        "pcc_occupierrole": None,  # Leave blank after Phase 3 changes
        # Landlord
        "pcc_accountname": answers.company_name,
        "pcc_lladdress1street1": answers.landlord_details["address1"],
        "pcc_lladdress1street2": answers.landlord_details["address2"],
        "pcc_lladdress1street3": None,
        "pcc_lladdress1city": answers.landlord_details["city"],
        "pcc_lladdress1county": None,
        "pcc_lladdress1zippostalcode": answers.landlord_details["postcode"],
        "pcc_llmainphone": answers.landlord_details["phone"],
        "pcc_website": None,
        "pcc_howdidyouhearaboutpec2": (
            option_value_mapping(
                "pcc_howdidyouhearaboutpec2",
                answers.source_of_info_about_pec,
                {
                    enums.HowDidYouHearAboutPEC.DOOR_KNOCKING: "Door knocking",
                    enums.HowDidYouHearAboutPEC.FACEBOOK: "Facebook",
                    enums.HowDidYouHearAboutPEC.FLYER: "Flyer/poster",
                    enums.HowDidYouHearAboutPEC.INSTAGRAM: "Instagram",
                    enums.HowDidYouHearAboutPEC.LETTER: "Letter in the post",
                    enums.HowDidYouHearAboutPEC.LINKEDIN: "LinkedIn",
                    enums.HowDidYouHearAboutPEC.PRINT_MEDIA: "Print Media",
                    enums.HowDidYouHearAboutPEC.PRIOR_RELATIONSHIP: "Prior relationship with PEC",
                    enums.HowDidYouHearAboutPEC.RADIO: "Radio",
                    enums.HowDidYouHearAboutPEC.SIGNPOST_CO: "Signpost - Community organisation",
                    enums.HowDidYouHearAboutPEC.SIGNPOST_CHARITY: "Signpost – Charity",
                    enums.HowDidYouHearAboutPEC.SIGNPOST_COUNCIL: "Signpost – Council",
                    enums.HowDidYouHearAboutPEC.SIGNPOST_LB: "Signpost – Local business",
                    enums.HowDidYouHearAboutPEC.TWITTER: "Twitter",
                    enums.HowDidYouHearAboutPEC.WEB_SEARCH: "Web Search",
                    enums.HowDidYouHearAboutPEC.WORD_OF_MOUTH: "Word of mouth",
                    enums.HowDidYouHearAboutPEC.NOT_SPECIFIED: "Other",
                },
            )
        ),
        "cr51a_childbenefitclaimantsingleorcouple": (
            option_value_mapping(
                "cr51a_childbenefitclaimantsingleorcouple",
                answers.child_benefit_claimant_type,
                {
                    enums.ChildBenefitClaimantType.SINGLE: "Single",
                    enums.ChildBenefitClaimantType.JOINT: "Couple",
                },
            )
        ),
        "cr51a_counciltaxbracket": None,  # Leave blank until council tax data issue will be sorted
        "cr51a_propertyattachment": (
            option_value_mapping(
                "cr51a_propertyattachment",
                answers.property_attachment,
                {
                    enums.PropertyAttachment.DETACHED: "Detached",
                    enums.PropertyAttachment.SEMI_DETACHED: "Semi detached",
                    enums.PropertyAttachment.MID_TERRACE: "Mid terrace",
                    enums.PropertyAttachment.END_TERRACE: "End terrace",
                    enums.PropertyAttachment.ENCLOSED_END_TERRACE: "Enclosed end terrace",
                    enums.PropertyAttachment.ENCLOSED_MID_TERRACE: "Enclosed mid terrace",
                },
            )
        ),
        "cr51a_boilerefficiency": (
            option_value_mapping(
                "cr51a_boilerefficiency",
                answers.boiler_efficiency,
                {
                    enums.EfficiencyBand.A: "A",
                    enums.EfficiencyBand.B: "B",
                    enums.EfficiencyBand.C: "C",
                    enums.EfficiencyBand.D: "D",
                    enums.EfficiencyBand.E: "E",
                    enums.EfficiencyBand.F: "F",
                    enums.EfficiencyBand.G: "G",
                },
            )
        ),
        "cr51a_lodgedepcband": (
            option_value_mapping(
                "cr51a_lodgedepcband",
                answers.lodged_epc_band,
                {
                    enums.EfficiencyBand.A: "A",
                    enums.EfficiencyBand.B: "B",
                    enums.EfficiencyBand.C: "C",
                    enums.EfficiencyBand.D: "D",
                    enums.EfficiencyBand.E: "E",
                    enums.EfficiencyBand.F: "F",
                    enums.EfficiencyBand.G: "G",
                },
            )
        ),
        "cr51a_sapband": (
            option_value_mapping(
                "cr51a_sapband",
                answers.sap_band,
                {
                    enums.EfficiencyBand.A: "A",
                    enums.EfficiencyBand.B: "B",
                    enums.EfficiencyBand.C: "C",
                    enums.EfficiencyBand.D: "D",
                    enums.EfficiencyBand.E: "E",
                    enums.EfficiencyBand.F: "F",
                    enums.EfficiencyBand.G: "G",
                },
            )
        ),
        "cr51a_65andover": answers.seniors,
        "cr51a_adults": answers.adults,
        "cr51a_childbenefitqualifyingchildren": answers.child_benefit_number,
        "cr51a_children": answers.children,
        "cr51a_childreneligibleforfreeschoolmeals": answers.free_school_meals_eligibility,
        "cr51a_counciltaxreductionentitlement": answers.council_tax_reduction,
        "cr51a_consented_callback": answers.consented_callback,
        "cr51a_consented_future_schemes": answers.consented_future_schemes,
        "cr51a_heatedrooms": answers.heated_rooms,
        "cr51a_heatingcontrolsadequacy": (
            option_value_mapping(
                "cr51a_heatingcontrolsadequacy",
                answers.controls_adequacy,
                {
                    enums.ControlsAdequacy.OPTIMAL: "Optimal",
                    enums.ControlsAdequacy.SUB_OPTIMAL: "Suboptimal",
                    enums.ControlsAdequacy.TOP_SPEC: "Top-spec",
                },
            )
        ),
        "cr51a_householdincome": answers.household_income,
        "cr51a_householdincome_base": None,
        "cr51a_householdsavings": None,
        "cr51a_householdsavings_base": None,
        "cr51a_housingcosts": answers.housing_costs,
        "cr51a_housingcosts_base": None,
        "cr51a_imd_decile": answers.multiple_deprivation_index,
        "cr51a_imdincomedecile": answers.income_decile,
        "cr51a_incomeafterhousingcosts": None,
        "cr51a_incomeafterhousingcosts_base": None,
        "cr51a_lodgedepcscore": answers.lodged_epc_score,
        "cr51a_lowersuperoutputareacode": answers.lower_super_output_area_code,
        "cr51a_othervulnerabilitytothecold": answers.vulnerable_comments,
        "cr51a_paritysapscore": answers.sap_score,
        "cr51a_potentialmeasures": None,
        "cr51a_potentialschemeeligibility": None,
        "cr51a_realisticfuelbill": answers.realistic_fuel_bill,
        "cr51a_receiveschildbenefit": answers.child_benefit,
        "cr51a_receivesmeanstestedbenefits": answers.means_tested_benefits,
        "cr51a_respondent_comments": answers.respondent_comments,
        "cr51a_respondent_relationship_to_property": (
            option_value_mapping(
                "cr51a_respondent_relationship_to_property",
                answers.respondent_role,
                {
                    enums.RespondentRole.OWNER_OCCUPIER: "Owner-Occupier",
                    enums.RespondentRole.TENANT: "Tenant",
                    enums.RespondentRole.LANDLORD: "Landlord",
                    enums.RespondentRole.OTHER: "Other",
                },
            )
        ),
        "cr51a_respondentemailadress": answers.email,
        "cr51a_respondentfirstname": answers.first_name,
        "cr51a_respondentlastname": answers.last_name,
        "cr51a_respondentmobile": answers.contact_mobile,
        "cr51a_respondentphonenumber": answers.contact_phone,
        "cr51a_respondentrelationshiptooccupier": answers.respondent_role_other,
        "cr51a_situation": answers.advice_needed_details,
        "cr51a_shortid": answers.short_uid,
        "cr51a_tco2current": tco2current(),
        "cr51a_tenure": (
            option_value_mapping(
                "cr51a_tenure",
                answers.tenure,
                {
                    enums.Tenure.RENTED_SOCIAL: "Social Rented",
                    enums.Tenure.RENTED_PRIVATE: "Private Rented",
                    enums.Tenure.OWNER_OCCUPIED: "Owner Occupied",
                    enums.Tenure.UNKNOWN: "Not Yet Specified",
                },
                default_mapping="Not Yet Specified",
            )
        ),
        "cr51a_uprn": answers.uprn,
        "cr51a_vulnerabilitytothecold": answers.vulnerabilities_general,
        "cr51a_vulnerabilitytothecold_cardiovascular": answers.vulnerable_cariovascular,
        "cr51a_vulnerabilitytothecold_respiratory": answers.vulnerable_respiratory,
        "cr51a_vulnerabilitytothecold_mentalhealth": answers.vulnerable_mental_health,
        "cr51a_vulnerabilitytothecold_disabledltdmob": answers.vulnerable_disability,
        "cr51a_vulnerabilitytothecold_65plus": answers.vulnerable_age,
        "cr51a_vulnerabilitytothecold_youngchildren": answers.vulnerable_children,
        "cr51a_vulnerabilitytothecold_pregnancy": answers.vulnerable_pregnancy,
        "cr51a_vulnerabilitytothecold_immunosuppression": answers.vulnerable_immunosuppression,
        "cr51a_nmt4properties": answers.nmt4properties,
        "cr51a_advice_needed_warm": answers.advice_needed_warm,
        "cr51a_advice_needed_bills": answers.advice_needed_bills,
        "cr51a_advice_needed_supplier": answers.advice_needed_supplier,
        "cr51a_advice_needed_from_team": answers.advice_needed_from_team,
        "cr51a_past_means_tested_benefits": answers.past_means_tested_benefits,
        # Potential schemes eligibility fields:
        "cr51a_bus": answers.is_bus_eligible,
        "cr51a_connectedforwarmth": answers.is_connected_for_warmth_eligible,
        "cr51a_eco4": answers.is_eco4_eligible,
        "cr51a_eco4flex": answers.is_eco4_flex_eligible,
        "cr51a_gbis": answers.is_gbis_eligible,
        "cr51a_hug2": answers.is_hug2_eligible,
        "cr51a_whlg": answers.is_whlg_eligible,
        # Potential measures' fields:
        "cr51a_batterystorage": answers.is_solar_pv_installation_recommended,
        "cr51a_cavity_wall_insulation": answers.is_cavity_wall_insulation_recommended,
        "cr51a_heat_pump": answers.is_heatpump_installation_recommended,
        "cr51a_loft_insulation": answers.is_loft_insulation_recommended,
        "cr51a_low_carbon_heating_upgrade": answers.is_boiler_upgrade_recommended,
        "cr51a_rir_insulation": answers.is_rir_insulation_recommended,
        "cr51a_smartheatingcontrols": answers.is_heating_controls_installation_recommended,
        "cr51a_solarpv": answers.is_solar_pv_installation_recommended,
        "cr51a_solid_wall_insulation": answers.is_solid_wall_insulation_recommended,
        "cr51a_underfloor_insulation": answers.is_underfloor_insulation_recommended,
    }
    return crm_data


def create_pcc_record(client, crm_data: dict) -> Optional[dict]:
    """CRM record spec from.

    https://docs.google.com/spreadsheets/d/1qhLWOEHnvFS3oKO-VDtP2lB8y85CGG0W/edit#gid=1103082051
    """
    query = "pcc_retrofitintermediates"
    return crm_request(client, query, json=crm_data, request_method="POST")


def answers_to_submit():
    return models.Answers.objects.filter(
        completed_at__isnull=False,  # Completed records only at this time.
        crmresult__isnull=True,  # No re-submissions.
    )

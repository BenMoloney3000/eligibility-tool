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


def infer_pcc_primaryheatingfuel(
    on_mains_gas: Optional[bool] = None,
    storage_heaters_present: Optional[bool] = None,
    other_heating_fuel: enums.NonGasFuel = "",  # non-nullable, but blank=True
) -> int:
    """Map between answers and pcc_primaryheatingfuel.

    Unmapped answers field values:
        'other_heating_fuel': DISTRICT  # see pcc_heatingdeliverymethod

    pcc_primaryheatingfuel:
        No Heating System Present
    """
    if on_mains_gas:
        return "Mains Gas"
    elif other_heating_fuel == enums.NonGasFuel.ELECTRICITY:
        if storage_heaters_present:
            return "Electricity - off peak"
        else:
            return "Electricity - standard"
    else:
        return {
            enums.NonGasFuel.WOOD: "Biomass",
            enums.NonGasFuel.COAL: "Coal",
            enums.NonGasFuel.LPG: "LPG",
            enums.NonGasFuel.OIL: "Oil",
        }.get(other_heating_fuel, "Unknown")


def map_crm(answers: models.Answers) -> dict:
    STATUSCODE_SUBMITTED = "798360000"
    STATECODE_ACTIVE = "0"

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
        "pcc_towncity": answers.property_address_3,
        "pcc_county": None,  # Leave blank
        "pcc_postcode": answers.property_postcode,
        "pcc_udprn": answers.property_udprn,
        "pcc_likelihoodofprivatelyrented": option_value_mapping(
            "pcc_likelihoodofprivatelyrented",
            answers.property_ownership,
            {
                enums.PropertyOwnership.PRIVATE_TENANCY: "High",
            },
            default_mapping="Low",
        ),
        "pcc_inscopeformees": None,  # Leave blank
        "pcc_primaryheatingfuel": option_value(
            "pcc_primaryheatingfuel",
            infer_pcc_primaryheatingfuel(
                on_mains_gas=answers.on_mains_gas,
                storage_heaters_present=answers.storage_heaters_present,
                other_heating_fuel=answers.other_heating_fuel,
            ),
        ),
        "pcc_primaryheatingdeliverymethod": None,
        "pcc_secondaryheatingfuel": None,
        "pcc_secondaryheatingdeliverymethod": None,
        "pcc_boilertype": None,
        "pcc_heatingcontrols": None,
        "pcc_solarpanels": None,
        "pcc_solarthermal": None,
        "pcc_propertytype": None,
        "pcc_bedrooms": None,
        "pcc_propertyage": None,
        "pcc_listedproperty": None,
        "pcc_rooftype": None,
        "pcc_roofinsulation": None,
        "pcc_floortype": None,
        "pcc_floorinsulation": None,
        "pcc_walltype": None,
        "pcc_wallinsulation": None,
        "pcc_glazing": None,
        "pcc_propertyprofilecomments": None,
        "pcc_epctype": None,
        "pcc_dateofmostrecentepc": None,
        "pcc_gradeofmostrecentepc": None,
        "pcc_scoreofmostrecentepc": None,
        "pcc_hasapgrade": None,
        "pcc_hasapscore": None,
        "pcc_mouldgrowth": None,
        "pcc_condensation": None,
        "pcc_structuraldamp": None,
        "pcc_commentsondamp": None,
        "pcc_occupanteligibilityscore": option_value_mapping(
            "pcc_occupanteligibilityscore",
            answers.income_rating,
            {
                enums.RAYG.RED: "Red",
                enums.RAYG.AMBER: "Amber",
                enums.RAYG.YELLOW: "Yellow",
                enums.RAYG.GREEN: "Green",
            },
        ),
        "pcc_propertyeligibilityscore": option_value_mapping(
            "pcc_occupanteligibilityscore",
            answers.property_rating,
            {
                enums.RAYG.RED: "Red",
                enums.RAYG.AMBER: "Amber",
                enums.RAYG.GREEN: "Green",
            },
        ),
        # Contact
        "pcc_salutation": None,
        "pcc_firstname": answers.first_name,
        "pcc_lastname": answers.last_name,
        "pcc_homephone": answers.contact_phone,
        "pcc_mobile": answers.contact_mobile,
        "pcc_email": answers.email,
        "pcc_address1street1": answers.respondent_address_1,
        "pcc_address1street2": answers.respondent_address_2,
        "pcc_address1street3": answers.respondent_address_3,
        "pcc_address1city": None,
        "pcc_address1county": None,
        "pcc_address1zippostalcode": answers.respondent_postcode,
        "pcc_udprncontact": answers.respondent_udprn,
        # Occupier
        "pcc_occupiedfrom": None,
        "pcc_occupiedto": None,
        "pcc_occupierrole": None,
        # Landlord
        "pcc_accountname": None,
        "pcc_lladdress1street1": None,
        "pcc_lladdress1street2": None,
        "pcc_lladdress1street3": None,
        "pcc_lladdress1city": None,
        "pcc_lladdress1county": None,
        "pcc_lladdress1zippostalcode": None,
        "pcc_llmainphone": None,
        "pcc_website": None,
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

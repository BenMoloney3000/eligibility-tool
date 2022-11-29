import json
import logging
import urllib.parse
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from prospector.apis.crm import mapping
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
        "pcc_primaryheatingfuel": mapping.infer_pcc_primaryheatingfuel(
            on_mains_gas=answers.on_mains_gas,
            storage_heaters_present=answers.storage_heaters_present,
            other_heating_fuel=answers.other_heating_fuel,
        )[1],
        "pcc_primaryheatingdeliverymethod": (
            mapping.infer_pcc_primaryheatingdeliverymethod(
                gas_boiler_present=answers.gas_boiler_present,
                heat_pump_present=answers.heat_pump_present,
                storage_heaters_present=answers.storage_heaters_present,
                hhrshs_present=answers.hhrshs_present,
                electric_radiators_present=answers.electric_radiators_present,
            )[1]
        ),
        "pcc_secondaryheatingfuel": None,  # Leave blank
        "pcc_secondaryheatingdeliverymethod": None,  # Leave blank
        "pcc_boilertype": mapping.infer_pcc_boilertype(
            gas_boiler_present=answers.gas_boiler_present,
            gas_boiler_age=answers.gas_boiler_age,
        )[1],
        "pcc_heatingcontrols": mapping.infer_pcc_heatingcontrols(
            gas_boiler_present=answers.gas_boiler_present,
            smart_thermostat=answers.smart_thermostat,
            room_thermostat=answers.room_thermostat,
            programmable_thermostat=answers.programmable_thermostat,
            heat_pump_present=answers.heat_pump_present,
            ch_timer=answers.ch_timer,
        )[1],
        "pcc_solarpanels": option_value_mapping(
            "pcc_solarpanels",
            answers.has_solar_pv,
            {
                True: "RoofArray",
                False: "Unknown",
            },
            default_mapping="Unknown",
        ),
        "pcc_solarthermal": None,  # Leave blank
        "pcc_propertytype": (
            mapping.infer_pcc_propertytype(
                property_type=answers.property_type,
                property_form=answers.property_form,
            )[1]
         ),
        "pcc_bedrooms": None,  # Leave blank
        "pcc_propertyage": (
            option_value_mapping(
                "pcc_propertyage",
                answers.property_age_band,
                {
                    enums.PropertyAgeBand.BEFORE_1900: "Pre 1900",
                    enums.PropertyAgeBand.FROM_1900: "1900 to 1929",
                    enums.PropertyAgeBand.FROM_1930: "1930 to 1949",
                    enums.PropertyAgeBand.FROM_1950: "1950 to 1966",
                    enums.PropertyAgeBand.FROM_1967: "1967 to 1975",
                    enums.PropertyAgeBand.FROM_1976: "1976 to 1990",
                    enums.PropertyAgeBand.FROM_1991: "1991 to 2002",
                    enums.PropertyAgeBand.SINCE_2003: "Since 2003",
                    enums.PropertyAgeBand.UNKNOWN: "Unknown",
                },
                default_mapping="Unknown",
            )
        ),
        "pcc_listedproperty": None,  # Leave blank
        "pcc_rooftype": (
            mapping.infer_pcc_rooftype(
                unheated_loft=answers.unheated_loft,
                room_in_roof=answers.room_in_roof,
                flat_roof=answers.flat_roof,
            )[1]
         ),
        "pcc_roofinsulation": None,  # Leave blank
        "pcc_floortype": (
            option_value_mapping(
                "pcc_floortype",
                answers.suspended_floor,
                {
                    True: "Yes",
                    False: "Solid"
                },
                default_mapping="Unknown",
            )
        ),
        "pcc_floorinsulation": (
            option_value_mapping(
                "pcc_floorinsulation",
                answers.suspended_floor_insulated,
                {
                    True: "Insulated",
                    False: "Uninsulated"
                },
                default_mapping="Unknown",
            )
        ),
        "pcc_walltype": (
            mapping.infer_pcc_walltype(
                wall_type=answers.wall_type,
                walls_insulated=answers.walls_insulated,
            )[1]
        ),
        "pcc_wallinsulation": (
            option_value_mapping(
                "pcc_wallinsulation",
                answers.walls_insulated,
                {
                    True: "Insulated",
                    False: "Uninsulated"
                },
                default_mapping="Unknown",
            )
        ),
        "pcc_glazing": None,  # Leave blank
        "pcc_propertyprofilecomments": None,  # Leave blank
        "pcc_epctype": (
            option_value_mapping(
                "pcc_epctype",
                answers.selected_epc,
                {
                    True: "Acutal",
                    False: "Unknown",
                },
                default_mapping="Unknown",
            )
        ),
        "pcc_dateofmostrecentepc": None,  # leave blank
        "pcc_gradeofmostrecentepc": None,  # leave blank
        "pcc_scoreofmostrecentepc": (
            answers.sap_rating
        ),
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
                enums.RAYG.RED: "\U0001f7e5 Red",
                enums.RAYG.AMBER: "\U0001f7e7 Amber",
                enums.RAYG.YELLOW: "\U0001f7e8 Yellow",
                enums.RAYG.GREEN: "\U0001f7e9 Green",
            },
        ),
        "pcc_propertyeligibilityscore": option_value_mapping(
            "pcc_occupanteligibilityscore",
            answers.property_rating,
            {
                enums.RAYG.RED: "\U0001f7e5 Red",
                enums.RAYG.AMBER: "\U0001f7e7 Amber",
                enums.RAYG.YELLOW: "\U0001f7e8 Yellow",
                enums.RAYG.GREEN: "\U0001f7e9 Green",
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
        "pcc_address1city": answers.respondent_address_3,
        "pcc_address1county": None,
        "pcc_address1zippostalcode": answers.respondent_postcode,
        "pcc_udprncontact": answers.respondent_udprn,
        # Occupier
        "pcc_occupiedfrom": None,
        "pcc_occupiedto": None,
        "pcc_occupierrole": (
            mapping.infer_pcc_occupierrole(
                respondent_role=answers.respondent_role,
            )[1]
        ),
        # Landlord
        "pcc_accountname": (
            "{} {}".format(first_name, last_name)
            if answers.respondent_role == enums.RespondentRole.LANDLORD
            else None
        ),
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

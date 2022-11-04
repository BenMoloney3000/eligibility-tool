import os
import json
import csv
import logging

from dataclasses import dataclass
from typing import Optional

import requests

from django.conf import settings
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError

from prospector.apps.questionnaire import models


logger = logging.getLogger(__name__)
BASE_URL = "https://plymouthenergycommunity.crm4.dynamics.com/"


@dataclass
class AddressData:
    line_1: str
    line_2: str
    line_3: str
    post_town: str
    district: str
    postcode: str
    udprn: int
    uprn: str


def _process_results(results):
    return [
        AddressData(
            row["Address"]["Lines"][0],  # line_1
            row["Address"]["Lines"][1],  # line_2
            row["Address"]["Lines"][2],  # line_3
            row["Address"]["Lines"][4],  # post_town
            row["RawAddress"]["Location"]["District"],  # district
            row["Address"]["Lines"][5],  # postcode
            int(row["RawAddress"]["UniqueReference"] or 0),  # UDPRN, shoudn't ever be 0
            "",  # UPRN
        )
        for row in results
    ]


def get_bearer_token():
    if not getattr(settings, "CRM_API", False):
        logger.error("CRM_API Django settings not set.")

    crm_api = settings.CRM_API

    with requests.Session() as s:
        url = "https://login.microsoftonline.com/%s/oauth2/token" % (
            crm_api['TENANT']
        )
        s.mount(url, HTTPAdapter(max_retries=3))
        response = s.post(
            url,
            json={
                'grant_type': 'client_credentials',
                'resource': crm_api['RESOURCE'],
                'client_id': crm_api['CLIENT_ID'],
                'client_secret': crm_api['CLIENT_SECRET'],
            },
            timeout=15,
        )
        json_response = json.loads(response.text)
        return json_response['access_token']

def get_fields():
    field_spec_csv = os.path.join(os.path.dirname(__file__), 'crm_fields.csv')
    rows = []
    with open(field_spec_csv, mode='r') as infile:
        reader = csv.DictReader(infile)
        rows += [o for o in reader]

    create_rows = [
        (o['LogicalName'], o['AttributeType'])
        for o in rows if bool(o['IsValidForCreate'])
    ]

    # TODO:
    # Add handlers for each AttributeType
    # model field serialiser -> crm
    AttributeTypes = {
    }
    __import__('pdb').set_trace()

def serialise_crm(answers: models.Answers) -> str:
    logical_name = 'pcc_retrofitintermediate'
    entity = None
    return json.dumps(entity)

def create_entry(answers: models.Answers) -> Optional[list]:
    """ Create a CRM entry """

    answer_record = serialise_crm(answers)

    params = {
        "licence": settings.DATA8_LICENSE,
        "postcode": postcode,
        "options": {
            "ApplicationName": "Prospector",
            "IncludeUDPRN": True,
            "IncludeAdminArea": True,
            "NormalizeTownCase ": True,  # Doesn't seem to work!
        },
    }
    try:
        with requests.Session() as s:
            s.mount(url, HTTPAdapter(max_retries=3))

            results = s.post(
                url,
                json=params,
                timeout=15,
            )
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not reach Data8 server: {e}")
        return []
    except HTTPError as http_err:
        logging.error(f"Data8 server responded with an error: {http_err}")
        return []

    data = results.json()

    if not data["Status"].get("Success", False):
        if "not a valid postcode" in data["Status"]["ErrorMessage"]:
            return None
        else:
            logging.error(
                "Data8 request unsuccessful: " + data["Status"]["ErrorMessage"]
            )
            return []

    try:
        return _process_results(data["Results"])
    except json.JSONDecodeError:
        # Something went wrong technically. Log it for debugging
        logging.error(
            f"Data8 request unsuccessful: could not parse response for {postcode}"
        )
        return []

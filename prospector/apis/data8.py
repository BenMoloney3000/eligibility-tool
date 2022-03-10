"""Get data from the Data8 Postcodes API to pre-fill addresses."""
import json
import logging
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError

from prospector.dataformats import postcodes


logger = logging.getLogger(__name__)
BASE_URL = "https://webservices.data-8.co.uk/AddressCapture/GetFullAddress.json"


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


def get_for_postcode(raw_postcode: str) -> Optional[list]:
    """Return a list of addresses for the given postcode.

    Raises as ValueError exception if malformed or None if not a valid postcode.
    """

    postcode = postcodes.normalise(raw_postcode)
    if not postcodes.validate_household_postcode(postcode):
        return ValueError("This is not a UK household postcode")

    if not getattr(settings, "DATA8_API_KEY", False):
        # Probably a dev environment. Log an error and continue as if no data
        logger.error("Postcode API not set.")

        # Can't say it's not a valid postcode, or that it wasn't found, so we'll
        # do our best to put on a brave face and continue.
        return []

    url = BASE_URL + "?key=" + settings.DATA8_API_KEY
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

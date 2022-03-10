"""Get data from Ideal Postcodes API to pre-fill addresses and find UPRNs."""
import json
import logging
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter

from prospector.dataformats import postcodes


logger = logging.getLogger(__name__)
BASE_URL = "https://api.ideal-postcodes.co.uk/v1/"


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


def _process_results(rows):
    return [
        AddressData(
            row["line_1"],
            row["line_2"],
            row["line_3"],
            row["post_town"],
            row["district"],
            row["postcode"],
            int(row["udprn"] or 0),  # should never be 0
            row["uprn"],
        )
        for row in rows
    ]


def get_for_postcode(raw_postcode: str) -> Optional[list]:
    """Return a list of addresses for the given postcode.

    Raises as ValueError exception if malformed or None if postcode not found.
    """

    postcode = postcodes.normalise(raw_postcode)
    if not postcodes.validate_household_postcode(postcode):
        return ValueError("This is not a UK household postcode")

    if not settings.IDEAL_POSTCODES_API_KEY:
        # Probably a dev environment. Log an error and continue as if no data
        logger.error("Postcode API not set.")

        # Can't say it's not a valid postcode, or that it wasn't found, so we'll
        # do our best to put on a brave face and continue.
        return []

    # Ideal Postcodes wants the postcode submitted without spaces
    postcode.replace(" ", "")

    try:
        with requests.Session() as s:
            s.mount(BASE_URL, HTTPAdapter(max_retries=3))

            results = s.get(
                f"{BASE_URL}postcodes/{postcode}",
                params={"api_key": settings.IDEAL_POSTCODES_API_KEY},
                timeout=15,
            )
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not reach Ideal Postcodes server: {e}")
        return []

    if results.status_code == 400:
        raise ValueError("This postcode is malformed.")
    elif results.status_code == 404:
        # Postcode not found
        return None
    elif results.status_code == 402:
        # We ran out of API credits
        logger.error("No API credits for Ideal Postcodes")
        return []
    elif results.status_code != 200:
        # Some other unexpected server error
        logger.error(f"Server error {results.status_code} from Ideal Postcodes")
        return []

    data = results.json()

    try:
        return _process_results(data["result"])
    except json.JSONDecodeError:
        # Something went wrong technically
        return []

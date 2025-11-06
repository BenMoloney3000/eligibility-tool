"""Get data from the Postcoder API to pre-fill addresses (UPRN only)."""
import json
import logging
import urllib.parse
from dataclasses import dataclass
from os import path
from typing import List, Optional

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter

from prospector.dataformats import postcodes


logger = logging.getLogger(__name__)
BASE_URL = "https://ws.postcoder.com/pcw/"


@dataclass
class AddressData:
    line_1: str
    line_2: str
    line_3: str
    post_town: str
    district: str
    postcode: str
    uprn: str  # UPRN only
    id: str  # Fallback identifier


def _process_results(results: list) -> List[AddressData]:
    out: List[AddressData] = []

    for i, row in enumerate(results or []):
        out.append(
            AddressData(
                line_1=row.get('addressline1', ''),
                line_2=row.get('addressline2', ''),
                line_3=row.get('addressline3', ''),
                post_town=row.get('posttown', ''),
                district=row.get('dependentlocality', ''),
                postcode=row.get('postcode', ''),
                uprn=row.get('uniquedeliverypointreferencenumber', ''),
                id=f"addr-{row.get('addresskey', '')}",
            )
        )

    return out


def get_for_postcode(raw_postcode: str) -> Optional[List[AddressData]]:
    """Return addresses for the given postcode (UPRN only).

    Raises:
        ValueError: if the postcode is malformed / not a UK household postcode.

    Returns:
        list[AddressData]: on success,
        []: if the API can’t be reached or another non-fatal error occurred,
        None: if the postcode is validly-formed but not a real/serviced postcode.
    """
    postcode = postcodes.normalise(raw_postcode)
    if not postcodes.validate_household_postcode(postcode):
        raise ValueError("This is not a UK household postcode")

    if not getattr(settings, "POSTCODER_API_KEY", None):
        # Likely a dev environment. Log and behave as "no data" rather than erroring.
        logger.error("POSTCODER_API_KEY not set.")
        return []

    if settings.POSTCODER_API_KEY == 'DUMMY':
        # Read in an example response file (for PL1 5PD) to allow local testing without using API credits.
        with open(path.join(settings.SRC_DIR, 'testutils', 'example_postcoder_response.json')) as f:
            dummy_response = f.read()
        data = json.loads(dummy_response)

    else:
        url = f"{BASE_URL}{settings.POSTCODER_API_KEY}/address/uk/{urllib.parse.quote_plus(postcode)}?lines=3&addtags=udprn,addresskey"

        try:
            with requests.Session() as s:
                # Mount retries for the scheme/host, not the full URL
                s.mount("https://", HTTPAdapter(max_retries=3))
                resp = s.get(url, timeout=15)
                resp.raise_for_status()
                data = resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Could not reach Postcoder server: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Postcoder response was not valid JSON for {postcode}: {e}")
            return []

    try:
        addresses = _process_results(data)
    except Exception as e:
        # Guard against unexpected shape changes
        logger.error(f"Postcoder response parse error for {postcode}: {e}")
        return []

    return addresses

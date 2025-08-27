"""Get data from the Data8 Postcodes API to pre-fill addresses (UPRN only)."""
import json
import logging
from dataclasses import dataclass
from typing import List, Optional

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter

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
    uprn: str  # UPRN only


def _extract_additional_value(raw: dict, name: str) -> str:
    """Get a value from RawAddress.AdditionalData by Name."""
    for kv in (raw or {}).get("AdditionalData", []) or []:
        if kv.get("Name") == name and kv.get("Value"):
            return str(kv["Value"])
    return ""


def _process_results(results: list) -> List[AddressData]:
    out: List[AddressData] = []

    for row in results or []:
        addr = row.get("Address", {}) or {}
        lines = addr.get("Lines", []) or []
        raw = row.get("RawAddress", {}) or {}
        loc = raw.get("Location", {}) or {}

        def _get(i: int) -> str:
            return lines[i] if i < len(lines) else ""

        # UPRN is provided in RawAddress.AdditionalData as {"Name": "UPRN", "Value": "..."}
        uprn = _extract_additional_value(raw, "UPRN") or str(row.get("UPRN") or raw.get("UPRN") or "")

        out.append(
            AddressData(
                line_1=_get(0),
                line_2=_get(1),
                line_3=_get(2),
                post_town=_get(4),   # town commonly at index 4
                district=str(loc.get("District") or ""),  # in your payload, District lives under RawAddress.Location
                postcode=_get(6),    # postcode commonly at index 6
                uprn=uprn,
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

    if not getattr(settings, "DATA8_API_KEY", None):
        # Likely a dev environment. Log and behave as "no data" rather than erroring.
        logger.error("DATA8_API_KEY not set.")
        return []

    url = f"{BASE_URL}?key={settings.DATA8_API_KEY}"
    params = {
        "licence": settings.DATA8_LICENSE,  # Data8 uses British spelling
        "postcode": postcode,
        "options": {
            "ApplicationName": "Prospector",
            # Request **only** UPRN (do not request UDPRN alongside it)
            "IncludeUPRN": True,
            "IncludeAdminArea": True,
            # Normalisation helpers (exact casing matters)
            "NormalizeCase": True,
            "NormalizeTownCase": True,
        },
    }

    try:
        with requests.Session() as s:
            # Mount retries for the scheme/host, not the full URL
            s.mount("https://", HTTPAdapter(max_retries=3))
            resp = s.post(url, json=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not reach Data8 server: {e}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Data8 response was not valid JSON for {postcode}: {e}")
        return []

    status = (data or {}).get("Status", {})
    if not status.get("Success", False):
        msg = (status.get("ErrorMessage") or "").strip()
        # Data8 uses a variety of phrasings; be permissive in detection
        if "invalid postcode" in msg.lower() or "not a valid postcode" in msg.lower():
            return None
        logger.error(f"Data8 request unsuccessful: {msg}")
        return []

    try:
        addresses = _process_results(data.get("Results", []))
    except Exception as e:
        # Guard against unexpected shape changes
        logger.error(f"Data8 response parse error for {postcode}: {e}")
        return []

    # Helpful signal if the API shape changes or licence/options don’t return UPRN
    if params["options"].get("IncludeUPRN") and addresses and all(not a.uprn for a in addresses):
        logger.warning("Data8: IncludeUPRN=True but no UPRN values found in results for %s", postcode)

    return addresses

"""Get data from public EPC database for England & Wales."""
import datetime
import json
import logging
from typing import Optional

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from requests.adapters import HTTPAdapter

from .dataclass import EPCData
from prospector.dataformats import postcodes


def _process_results(rows):
    return [
        EPCData(
            row["lmk-key"],
            datetime.date.fromisoformat(row["inspection-date"]),
            row["address1"],
            row["address2"],
            row["address3"],
            row["uprn"],
            row["property-type"],
            row["built-form"],
            row["construction-age-band"],
            row["walls-description"],
            row["floor-description"],
            row["roof-description"],
            row["mainheat-description"],
            row["hotwater-description"],
            (
                int(row["main-heating-controls"])
                if (
                    row["main-heating-controls"].isdecimal()
                    and int(row["main-heating-controls"]) > 0
                )
                else None
            ),
            row["current-energy-efficiency"],
        )
        for row in rows
    ]


def get_for_postcode(postcode: str) -> Optional[list]:
    """Return a list of EPCs for the given postcode.

    None returned on failure, empty list if no EPCs found.
    """

    if not settings.EPC_API_KEY:
        raise ImproperlyConfigured("No EPC API key configured")

    try:
        with requests.Session() as s:
            s.mount("https://epc.opendatacommunities.org", HTTPAdapter(max_retries=3))

            results = s.get(
                "https://epc.opendatacommunities.org/api/v1/domestic/search",
                params={"postcode": postcodes.normalise(postcode)},
                headers={
                    "Authorization": f"Basic {settings.EPC_API_KEY}",
                    "Accept": "application/json",
                },
                timeout=15,
            )
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not reach EPC server: {e}")
        return None

    # If there are no EPCs we get an empty 200 response rather than no rows
    # (which is, IMHO, as dumb as duck custard. If it was going to do this
    # it could at least return a status code of 204 No Content).
    if len(results.content) == 0:
        return []

    try:
        return _process_results(results.json()["rows"])
    except json.JSONDecodeError:
        return None


def get_for_id(id: str):
    if not settings.EPC_API_KEY:
        raise ImproperlyConfigured("No EPC API key configured")

    try:
        with requests.Session() as s:
            s.mount("https://epc.opendatacommunities.org", HTTPAdapter(max_retries=3))

            results = s.get(
                f"https://epc.opendatacommunities.org/api/v1/domestic/certificate/{id}",
                headers={
                    "Authorization": f"Basic {settings.EPC_API_KEY}",
                    "Accept": "application/json",
                },
                timeout=15,
            )
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not reach EPC server: {e}")
        return None

    try:
        epcs = _process_results(results.json()["rows"])
    except json.JSONDecodeError:
        return None

    return epcs[0]

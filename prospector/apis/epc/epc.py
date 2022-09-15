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


# zeroth element is a dummy value, N/A should translate to None
RATING_STRINGS = ["DUMMY", "VERY POOR", "POOR", "AVERAGE", "GOOD", "VERY GOOD"]


def maybe_row(
    row,
    key,
    transform=lambda x: x,
    condition=lambda x: True,
    default=None
):
    value = row.get(key, default)

    try:
        if value and not condition(value):
            return None
    except Exception as e:
        logging.debug('EPC condition failure: ', key, value, e)
        return None

    try:
        value = transform(value)
    except Exception as e:
        logging.debug('EPC transform failure: ', key, value, e)

    return value


def _process_result(row):
    return EPCData(
        maybe_row(row, "lmk-key"),
        maybe_row(
            row,
            "inspection-date",
            transform=datetime.date.fromisoformat
        ),
        maybe_row(row, "address1"),
        maybe_row(row, "address2"),
        maybe_row(row, "address3"),
        maybe_row(row, "uprn"),
        maybe_row(row, "property-type"),
        maybe_row(row, "built-form"),
        maybe_row(row, "construction-age-band"),
        maybe_row(row, "walls-description"),
        maybe_row(
            row,
            "walls-energy-eff",
            transform=lambda x: RATING_STRINGS.index(x.upper()),
            condition=lambda x: x.upper() in RATING_STRINGS
        ),
        maybe_row(row, "floor-description"),
        maybe_row(
            row,
            "floor-energy-eff",
            transform=lambda x: RATING_STRINGS.index(x.upper()),
            condition=lambda x: x.upper() in RATING_STRINGS
        ),
        maybe_row(row, "roof-description"),
        maybe_row(
            row,
            "roof-energy-eff",
            transform=lambda x: RATING_STRINGS.index(x.upper()),
            condition=lambda x: x.upper() in RATING_STRINGS
        ),
        maybe_row(row, "mainheat-description"),
        maybe_row(row, "hotwater-description"),
        maybe_row(
            row,
            "main-heating-controls",
            transform=lambda x: int(x),
            condition=lambda x: all([
                    x.isdecimal(),
                    int(x) > 0
                ])
        ),
        maybe_row(row, "current-energy-efficiency"),
        maybe_row(
            row,
            "photo-supply",
            transform=lambda x: int(x),
            condition=lambda x: all([
                    row["photo-supply"].isdecimal(),
                ])
        ),
    )


def _process_results(rows):
    epcs = []

    for row in rows:
        try:
            epcs.append(_process_result(row))
        except Exception as e:
            logging.error("epc._process_result error", e, row)

    return epcs


def domestic_search(postcode: str) -> Optional[list]:
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
    return results


def get_for_postcode(postcode: str) -> Optional[list]:
    """Return a list of EPCs for the given postcode.

    None returned on failure, empty list if no EPCs found.
    """

    results = domestic_search(postcode)

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

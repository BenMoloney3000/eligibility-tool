"""Fake postcode API for testing."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AddressData:
    line_1: str
    line_2: str
    line_3: str
    post_town: str
    district: str
    postcode: str
    uprn: str


def get_for_postcode(raw_postcode: str) -> Optional[list]:
    addresses = [
        AddressData(
            "123 Test Avenue",
            "Test Suburb",
            "",
            "Plymouth",
            "",
            "PL1 2AB",
            "100000000000",
        )
    ]

    return addresses

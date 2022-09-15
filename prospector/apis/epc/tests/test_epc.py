from unittest import mock

import pytest

from ..epc import _process_results


@pytest.fixture
def fake_epc():
    return {
        "address1": "1 Nowhere",
        "address2": None,
        "address3": None,
        "uprn": "200000000000",
        "property-type": "House",
        "built-form": "End-Terrace",
        "construction-age-band": "England and Wales: 1991-1995",
        "walls-description": "Cavity wall, as built, insulated (assumed)",
        "walls-energy-eff": "Good",
        "floor-description": "Solid, limited insulation (assumed)",
        "floor-energy-eff": "NO DATA!",
        "roof-description": "Pitched, 100 mm loft insulation",
        "roof-energy-eff": "Average",
        "mainheat-description": "Boiler and radiators, mains gas",
        "hotwater-description": "From main system",
        "main-heating-controls": "2106",
        "current-energy-efficiency": "63",
        "photo-supply": None,
    }


def test_parse_epc(fake_epc):
    results = _process_results([fake_epc])
    assert len(results) == 1
    epc = results[0]
    assert epc.address_1 == "1 Nowhere"
    assert epc.address_2 is None
    assert epc.address_3 is None
    assert epc.uprn == "200000000000"
    assert epc.property_type == "House"
    assert epc.built_form == "End-Terrace"
    assert epc.construction_age_band == "England and Wales: 1991-1995"
    assert epc.walls_description == "Cavity wall, as built, insulated (assumed)"
    assert epc.walls_rating == 4  # 'Good'
    assert epc.floor_description == "Solid, limited insulation (assumed)"
    assert epc.floor_rating == None  # 'NO DATA!'
    assert epc.roof_description == "Pitched, 100 mm loft insulation"
    assert epc.roof_rating == 3  # 'Average'
    assert epc.mainheat_description == "Boiler and radiators, mains gas"
    assert epc.hotwater_description == "From main system"
    assert epc.main_heating_controls == 2106
    assert epc.current_energy_rating == "63"
    assert epc.photo_supply is None


def test_parse_epc_missing_field(fake_epc):
    fake_epc.pop("property-type")
    results = _process_results([fake_epc])
    assert len(results) == 1
    epc = results[0]
    assert epc.property_type is None


def test_parse_epc_malformed_rating(fake_epc):
    fake_epc["walls-energy-eff"] = "Bad Data"
    results = _process_results([fake_epc])
    assert len(results) == 1
    epc = results[0]
    assert epc.walls_rating is None


def test_parse_epc_non_decimal_heating_controls(fake_epc):
    fake_epc["main-heating-controls"] = "Bad Data"
    results = _process_results([fake_epc])
    assert len(results) == 1
    epc = results[0]
    assert epc.main_heating_controls is None

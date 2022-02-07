import datetime

from . import factories
from prospector.apis import epc
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import services

FAKE_EPC = epc.dataclass.EPCData(
    "19747490192737",
    datetime.date(2020, 10, 10),
    "20 Testington Pastures",
    "Eggborough",
    "Royal Leamington Spa",
    "1234",
    "Bungalow",
    "Semi-Detached",
    "England and Wales: 1976-1982",
    "Cavity wall, filled cavity",
    "To unheated space, limited insulation (assumed)",
    "Flat, no insulation (assumed)",
    "Boiler and radiators, electric",
    "From main system",
    2302,  # DHS_FLAT_RATE_PROGRAMMER
)


def test_that_gets_processed():
    """Test that the fake EPC gets processed.

    A bit artificial to get the coverage where it needs to be, and better than
    nothing!
    """

    answers = services.prepopulate_from_epc(factories.AnswersFactory.build(), FAKE_EPC)

    assert answers.property_type_orig == enums.PropertyType.BUNGALOW
    assert answers.property_form_orig == enums.PropertyForm.SEMI_DETACHED
    assert answers.property_age_band_orig == enums.PropertyAgeBand.FROM_1976
    assert answers.wall_type_orig == enums.WallType.CAVITY
    assert answers.walls_insulated_orig is True
    assert answers.suspended_floor_orig is None
    assert answers.unheated_loft_orig is False
    assert answers.room_in_roof_orig is False
    assert answers.rir_insulated_orig is False
    assert answers.roof_space_insulated_orig is None  # No roof space
    assert answers.flat_roof_orig is True
    assert answers.gas_boiler_present_orig is False
    assert answers.trvs_present_orig is False
    assert answers.room_thermostat_orig is False
    assert answers.ch_timer_orig is True
    assert answers.programmable_thermostat_orig is None

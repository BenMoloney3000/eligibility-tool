from prospector.dataformats.postcodes import normalise
from prospector.dataformats.postcodes import validate_household_postcode


def test_normalise_common_formats():
    assert normalise("SK4 4BX") == "SK4 4BX"
    assert normalise("SK44BX") == "SK4 4BX"
    assert normalise("C__C9;;€€#;W ;0F'''F") == "CC9W 0FF"
    assert normalise("m13 0pq") == "M13 0PQ"


def test_reject_common_postcode_mistakes():
    assert not validate_household_postcode("Y010 4BG")
    assert not validate_household_postcode("YO10 ABG")
    assert not validate_household_postcode("YO10 A8G")
    assert not validate_household_postcode("YO10 AB6")


def test_pass_unusual_correct_postcode():
    assert validate_household_postcode("SW1A 2AA")

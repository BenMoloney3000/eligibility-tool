import pytest

from prospector.dataformats.phone_numbers import format
from prospector.dataformats.phone_numbers import normalise
from prospector.dataformats.phone_numbers import ParseError


def test_normalise_common_formats():
    assert normalise("+4479684     99121") == "+447968499121"
    assert normalise("0161 783 6911") == "+441617836911"
    assert normalise("(0161)  783 9 8 2 2") == "+441617839822"
    assert normalise("+441617836911") == "+441617836911"


def test_normalise_international_passthrough():
    assert normalise("+49929 198 3922") == "+49929 198 3922"


def test_international_dialling_code():
    assert normalise("003232941665") == "+3232941665"


@pytest.mark.parametrize("num", ["+++", "0161 + 783 + 6911"])
def test_plus_errors(num):
    with pytest.raises(ParseError) as exc:
        normalise(num)

    assert str(exc.value) == "'+' may only be at the start of a phone number"


def test_only_numbers():
    with pytest.raises(ParseError) as exc:
        normalise("FREDDO")

    assert str(exc.value) == "'F' not allowed in a phone number"


def test_error_start_with_plus_or_zero():
    with pytest.raises(ParseError) as exc:
        normalise("161 783 6911")

    assert str(exc.value) == "Number should start with either a '0' or a '+'"


def test_format():
    assert format("07968499121") == "07968 499121"
    assert format("01617836911") == "0161 783 6911"

    assert format("+49 929 6911 444") == "+49 929 6911 444"

    assert format("++++") == "++++"

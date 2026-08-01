import pytest

from prospector.dataformats.names import normalise


@pytest.mark.parametrize(
    "name,expected",
    [
        ("jane smith", "Jane Smith"),
        ("JANE SMITH", "Jane Smith"),
        ("jane", "Jane"),
        ("JANE", "Jane"),
    ],
)
def test_single_case_names_are_recased(name, expected):
    assert normalise(name) == expected


@pytest.mark.parametrize(
    "name",
    [
        "Jane Smith",
        "Jane McDonald",
        "Jane van Dijk",
        "Jane ffrench",
        "Jane MacLeod",
    ],
)
def test_mixed_case_names_are_left_alone(name):
    assert normalise(name) == name


@pytest.mark.parametrize(
    "name,expected",
    [
        ("smith-jones", "Smith-Jones"),
        ("SMITH-JONES", "Smith-Jones"),
        ("o'brien", "O'Brien"),
        ("d'arcy", "D'Arcy"),
        ("mcdonald", "McDonald"),
        ("mccoy", "McCoy"),
        ("mcgee", "McGee"),
    ],
)
def test_compound_surnames(name, expected):
    assert normalise(name) == expected


@pytest.mark.parametrize("name", ["macey", "mackie", "machin"])
def test_mac_is_not_treated_as_a_prefix(name):
    # Guessing here does more harm than good, so we just capitalise.
    assert normalise(name) == name.capitalize()


@pytest.mark.parametrize(
    "name,expected",
    [
        ("piet van der berg", "Piet van der Berg"),
        ("MARIA DE LA CRUZ", "Maria de la Cruz"),
        # A particle at the start of the field still gets capitalised.
        ("van der berg", "Van der Berg"),
    ],
)
def test_particles_stay_lower_case_mid_name(name, expected):
    assert normalise(name) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("  jane   smith  ", "Jane Smith"),
        ("Jane   Smith", "Jane Smith"),
        ("jane\tsmith", "Jane Smith"),
    ],
)
def test_whitespace_is_tidied(name, expected):
    assert normalise(name) == expected


@pytest.mark.parametrize("name", [None, "", "   "])
def test_empty_values_pass_through(name):
    assert normalise(name) in (name, "")

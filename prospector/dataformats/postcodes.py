import re


def normalise_postcode(code: str) -> str:
    """Make some text into something resembling a postcode."""
    regex = re.compile("[A-Z0-9]")
    stripped = "".join(c for c in code.upper() if re.match(regex, c))
    return stripped[:-3] + " " + stripped[-3:]


assert normalise_postcode("SK4 4BX") == "SK4 4BX"
assert normalise_postcode("C__C9;;€€#;W ;0F'''F") == "CC9W 0FF"
assert normalise_postcode("m13 0pq") == "M13 0PQ"


def validate_household_postcode(code: str) -> bool:
    # Validates the *structure* of the UK postcode provided, ignoring some
    # edge case non-geographic postcodes. Based on the 'fixed' version of the
    # 'official' UK postcode regex.
    # See https://stackoverflow.com/questions/164979/regex-for-matching-uk-postcodes

    regex = re.compile("^[A-Z]{1,2}\\d[A-Z\\d]? ?\\d[A-Z]{2}$", re.IGNORECASE)
    return bool(re.match(regex, code))

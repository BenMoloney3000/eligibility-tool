# This file under the Apache License 2.0
# Number formats and formatting code taken from phonenumbers Python library, which is
# a port of:
# Original Java code is Copyright (C) 2009-2015 The Libphonenumber Authors.
import re
from collections import namedtuple


class ParseError(Exception):
    pass


_IGNORE_CHARS = [" ", "\n", "\t", "(", ")", "-"]


def normalise(num: str) -> str:
    """
    Normalise a phone number as best we can.

    This function will try to parse out a phone number, and return a normalised
    version.  If it can't produce a normalised version it will throw a ParseError.
    The normalised version will always start with "+" and include a country code.

    If it's a non-UK number, spacing is preserved intact.

    It makes some assumptions; for example, if no international prefix is provided
    (00 or +) then it's a UK number.
    """
    parsed = ""
    seen_data = False
    seen_plus = False

    for idx, digit in enumerate(num):
        if digit.isdigit():
            if digit != "0" and not seen_data and not seen_plus:
                raise ParseError("Number should start with either a '0' or a '+'")

            parsed = parsed + digit
            seen_data = True

        elif digit == "+":
            if not seen_data and not seen_plus:
                seen_plus = True
            else:
                raise ParseError("'+' may only be at the start of a phone number")

        elif digit == " ":
            # We save spaces in case we don't understand the country code.
            # In this case we want to return the number with spacing intact.
            parsed = parsed + digit

        elif digit in _IGNORE_CHARS:
            pass

        else:
            raise ParseError(f"'{digit}' not allowed in a phone number")

    # International & national dialling codes
    if parsed.startswith("00"):
        parsed = parsed[2:]
    elif parsed.startswith("0"):
        parsed = "44" + parsed[1:]

    if parsed.startswith("44"):
        # We strip spaces from UK numbers to make comparison better.
        # You can put them back with format().
        return "+" + parsed.replace(" ", "")
    else:
        return "+" + parsed


_NumberFormat = namedtuple("NumberFormat", "pattern, format, leading_digits_pattern")

_FORMATS = [
    _NumberFormat(
        pattern="(\\d{3})(\\d{4})", format="\\1 \\2", leading_digits_pattern="8001111"
    ),
    _NumberFormat(
        pattern="(\\d{3})(\\d{2})(\\d{2})",
        format="\\1 \\2 \\3",
        leading_digits_pattern="845464",
    ),
    _NumberFormat(
        pattern="(\\d{3})(\\d{6})", format="\\1 \\2", leading_digits_pattern="800"
    ),
    _NumberFormat(
        pattern="(\\d{5})(\\d{4,5})",
        format="\\1 \\2",
        leading_digits_pattern="1(?:3873|5(?:242|39[4-6])|(?:697|768)[347]|9467)",
    ),
    _NumberFormat(
        pattern="(\\d{4})(\\d{5,6})",
        format="\\1 \\2",
        leading_digits_pattern="1(?:[2-69][02-9]|[78])",
    ),
    _NumberFormat(
        pattern="(\\d{2})(\\d{4})(\\d{4})",
        format="\\1 \\2 \\3",
        leading_digits_pattern="[25]|7(?:0|6(?:[03-9]|2[356]))",
    ),
    _NumberFormat(
        pattern="(\\d{4})(\\d{6})", format="\\1 \\2", leading_digits_pattern="7"
    ),
    _NumberFormat(
        pattern="(\\d{3})(\\d{3})(\\d{4})",
        format="\\1 \\2 \\3",
        leading_digits_pattern="[1389]",
    ),
]


# Stolen ruthlessly from the python-phonenumbers GitHub project:
# https://github.com/daviddrysdale/python-phonenumbers/blob/76d17e1278bebb5746026d0e7c3fe6159ee689d0/python/phonenumbers/phonenumberutil.py
def fullmatch(pattern, string, flags=0):
    """
    Try to find an appropriate formatting pattern for the `string`.

    Try to apply the pattern at the start of the string, returning a match
    object if the whole string matches, or None if no match was found.
    """
    # Build a version of the pattern with a non-capturing group around it.
    # This is needed to get m.end() to correctly report the size of the
    # matched expression (as per the final doctest above).
    grouped_pattern = re.compile("^(?:%s)$" % pattern.pattern, pattern.flags)
    m = grouped_pattern.match(string)
    if m and m.end() < len(string):
        # Incomplete match (which should never happen because of the $ at the
        # end of the regexp), treat as failure.
        m = None  # pragma no cover
    return m


def _choose_formatting_pattern_for_number(available_formats, national_number):
    for num_format in available_formats:
        ld_pattern = re.compile(num_format.leading_digits_pattern)
        ld_match = ld_pattern.match(national_number)
        if ld_match:
            format_pattern = re.compile(num_format.pattern)
            if fullmatch(format_pattern, national_number):
                return num_format
    return None


def format(num: str) -> str:
    """
    Attempt to format a phone number.

    This will accept any random input and try to parse it as a phone number.  If that
    fails, it returns the original input.  If it doesn't fail, it formats it according
    to Google's rules, which seem to give an OK result most of the time.
    """
    try:
        normalised = normalise(num)
    except ParseError:
        return num

    if normalised.startswith("+44"):
        val = normalised[3:]

        f = _choose_formatting_pattern_for_number(_FORMATS, val)
        if f:
            return "0" + re.sub(f.pattern, f.format, val)
        else:
            return num

    return normalised

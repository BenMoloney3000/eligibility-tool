"""
Tidy up the capitalisation of personal names.

People type their names however they like -- "jane smith", "JANE SMITH" -- and
whatever we send is what the CRM displays.  `normalise()` fixes the obvious
cases and deliberately leaves anything else alone.
"""
from typing import Optional

# Particles that stay lower case when they appear part-way through a name,
# as in "van der Berg" or "de la Cruz".
_PARTICLES = {
    "af",
    "al",
    "bin",
    "binte",
    "da",
    "de",
    "del",
    "della",
    "den",
    "der",
    "des",
    "di",
    "do",
    "dos",
    "du",
    "el",
    "ibn",
    "la",
    "le",
    "ten",
    "ter",
    "van",
    "von",
    "y",
    "zu",
}


def _capitalise(part: str) -> str:
    # Unlike str.capitalize() this leaves the rest of the part as it is.
    if not part:
        return part

    return part[0].upper() + part[1:]


def _capitalise_word(word: str) -> str:
    # Both halves of a double-barrelled name: "smith-jones" -> "Smith-Jones".
    word = "-".join(_capitalise(part) for part in word.split("-"))

    # "o'brien" -> "O'Brien", but not "smith's" -- only a very short prefix is
    # likely to be a name particle.
    prefix, apostrophe, rest = word.partition("'")
    if apostrophe and len(prefix) <= 2:
        word = prefix + "'" + _capitalise(rest)

    # "mcdonald" -> "McDonald".  Mac is left alone; there are too many names it
    # would get wrong ("Macey", "Mackie", "Machin").
    if len(word) > 4 and word.startswith("Mc"):
        word = "Mc" + _capitalise(word[2:])

    return word


def normalise(name: Optional[str]) -> Optional[str]:
    """
    Return `name` with sensible capitalisation.

    Whitespace is always tidied up.  The capitalisation is only changed if the
    name arrived entirely in upper or lower case -- if there's a mix then the
    user has capitalised it deliberately ("McDonald", "van Dijk", "ffrench")
    and we would do more harm than good by second-guessing them.

    Empty values and None are passed straight through.
    """
    if not name:
        return name

    name = " ".join(name.split())

    if not (name.isupper() or name.islower()):
        return name

    return " ".join(
        word if index and word in _PARTICLES else _capitalise_word(word)
        for index, word in enumerate(name.lower().split(" "))
    )

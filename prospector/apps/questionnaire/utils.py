import csv
import logging
import random
import os

from django.core.management.base import CommandError

logger = logging.getLogger(__name__)

MAX_64_BIT_INT = 9223372036854775807
MIN_64_BIT_INT = -9223372036854775808

def generate_id():
    """
    Generate string to be utilised as the short UUID-like value.

    Composed from 5 uppercase letters and 5 numbers.
    """

    id_string = ""
    chars = "ABCDEFGHIJKLMNPQRSTUVWXYZ123456789"
    for i in range(10):
        if i < 5:
            index = random.randint(0, 24)
            id_string += chars[index]
        else:
            index = random.randint(25, len(chars) - 1)
            id_string += chars[index]

    return "".join(random.sample(id_string, len(id_string)))


def get_whlg_eligible_postcodes():
    path = "external_data/WHLG-eligible-postcodes.csv"

    if not os.path.exists(path):
        print("⚠️ Skipping postcode loading: file not found")
        return []

    postcodes = []
    with open(path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                postcodes.append(row[0])
            except Exception:
                raise CommandError("Operation aborted due to data error.")
    return postcodes


def is_valid_64_bit_integer(data):
    try:
        number = int(data)
    except ValueError:
        return False

    if number > MAX_64_BIT_INT or number < MIN_64_BIT_INT:
        return False

    return True

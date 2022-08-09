import dataclasses
import hashlib

from django.conf import settings
from django.core.cache import caches

from . import models
from prospector.apis import data8
from prospector.apis import fake_postcodes
from prospector.apis import ideal_postcodes


# Running "manage.py compilescss" will import this file, so here we
# conditionally configure postcodes cache when we are building the docker
# image:
if settings.ENV != "offline":
    POSTCODE_CACHE = caches["postcodes"]
else:
    POSTCODE_CACHE = {}


def data_was_changed(answers: models.Answers) -> bool:
    """Determine if any third-party sourced property data was overruled."""

    # No EPC -> nothing to change
    if answers.selected_epc is None:
        return False

    # Dynamically find all the prepopulatable fields:
    for field in models.Answers._meta.get_fields():
        if field.name[-5:] == "_orig":
            # Data has been corrected if data derived value was presented
            # and the user entered a value which does not agree with it
            data_derived_value = getattr(answers, field.name)
            user_entered_value = getattr(answers, field.name[:-5])

            if (
                data_derived_value not in ["", None]
                and user_entered_value not in ["", None]
                and data_derived_value != user_entered_value
            ):
                return True

    return False


def make_key(key, key_prefix, version):
    # Store hashed post codes to silence the warning "CacheKeyWarning: Cache
    # key contains characters that will cause errors if used with memcached"
    m = hashlib.md5()
    m.update(key)
    return "%s:%s:%s" % (key_prefix, version, m.hexdigest())


def get_postcode(postcode):
    """Check cached postcodes before hitting the API.

    Uses normalised postcodes.
    """
    if POSTCODE_CACHE.get(postcode, None):
        return _process_cached_results(POSTCODE_CACHE.get(postcode))

    postcoders = {
        "DATA8": data8,
        "IDEAL_POSTCODES": ideal_postcodes,
        "FAKE": fake_postcodes,
    }
    postcoder = postcoders.get(settings.POSTCODER, ideal_postcodes)

    addresses = postcoder.get_for_postcode(postcode)

    if addresses:
        POSTCODE_CACHE.set(
            postcode, [dataclasses.asdict(address) for address in addresses]
        )
    return addresses


def _process_cached_results(results):
    return [
        data8.AddressData(
            row["line_1"],
            row["line_2"],
            row["line_3"],
            row["post_town"],
            row["district"],
            row["postcode"],
            int(row["udprn"]),
            row["uprn"],
        )
        for row in results
    ]

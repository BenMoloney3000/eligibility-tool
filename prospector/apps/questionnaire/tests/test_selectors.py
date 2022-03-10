from unittest import mock

from django.test import override_settings
from django.test import TestCase

from prospector.apis import data8
from prospector.apps.questionnaire import selectors


DUMMY_RESULTS = [
    data8.AddressData(
        "Bridge 5 Mill",
        "22a Beswick Street",
        "Ancoats",
        "MANCHESTER",
        "Manchester District",
        "M4 7HR",
        52418170,
        "",
    )
]


# There may be something built in in Django/Python but I don't know it.
class DummyCache:
    postcodes = {}

    def set(self, key, val):
        self.postcodes[key] = val

    def get(self, key, default=None):
        return self.postcodes.get(key, default)

    def wipe(self):
        self.postcodes = {}


DUMMY_CACHE = DummyCache()


class TestPostcodeCacher(TestCase):
    @override_settings(POSTCODER="DATA8")
    @mock.patch("prospector.apis.data8.get_for_postcode")
    def test_data8_postcodes_get_cached(self, get_for_postcode):
        get_for_postcode.return_value = DUMMY_RESULTS

        DUMMY_CACHE.wipe()

        with mock.patch(
            "prospector.apps.questionnaire.selectors.POSTCODE_CACHE", new=DUMMY_CACHE
        ):
            op = selectors.get_postcode("M4 7HR")

            assert get_for_postcode.call_count == 1
            assert op == DUMMY_RESULTS

            # The API call wasn't triggered the second time
            op = selectors.get_postcode("M4 7HR")
            assert get_for_postcode.call_count == 1
            assert op == DUMMY_RESULTS

    @override_settings(POSTCODER="IDEAL_POSTCODES")
    @mock.patch("prospector.apis.ideal_postcodes.get_for_postcode")
    def test_ideal_postcode_postcodes_get_cached(self, get_for_postcode):
        get_for_postcode.return_value = DUMMY_RESULTS

        DUMMY_CACHE.wipe()

        with mock.patch(
            "prospector.apps.questionnaire.selectors.POSTCODE_CACHE", new=DUMMY_CACHE
        ):
            op = selectors.get_postcode("M4 7HR")

            assert get_for_postcode.call_count == 1
            assert op == DUMMY_RESULTS

            # The API call wasn't triggered the second time
            op = selectors.get_postcode("M4 7HR")
            assert get_for_postcode.call_count == 1
            assert op == DUMMY_RESULTS

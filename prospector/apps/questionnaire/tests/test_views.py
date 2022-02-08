import datetime
from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import override_settings
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from . import factories
from prospector.apis.epc import dataclass as epc_dataclass
from prospector.apps.questionnaire import views
from prospector.testutils import add_middleware_to_request
from prospector.trail.mixin import snake_case


def _html(response):
    response.render()
    return response.content.decode("utf-8")


FAKE_EPC = epc_dataclass.EPCData(
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
    2302,
)


@override_settings(DEBUG=True)
class TrailTest(TestCase):
    trail = ["Start"]
    answers = None
    view = views.Start
    url_name = "questionnaire:start"

    def _submit_form(self, postdata, url_name: str = None):
        request = RequestFactory().post(reverse(self.url_name), data=postdata)
        add_middleware_to_request(request, SessionMiddleware)

        if not url_name:
            url_name = self.url_name

        if self.answers:
            request.session[views.SESSION_ANSWERS_ID] = self.answers.id
            request.session[views.SESSION_TRAIL_ID] = self.trail

        return self.view.as_view()(request)

    def _get_page(self, url_name: str = None):

        if not url_name:
            url_name = self.url_name

        request = RequestFactory().get(reverse(self.url_name))

        add_middleware_to_request(request, SessionMiddleware)

        if self.answers:
            request.session[views.SESSION_ANSWERS_ID] = self.answers.id
            request.session[views.SESSION_TRAIL_ID] = self.trail

        return self.view.as_view()(request)


class TestQuestionsRender(TrailTest):
    @classmethod
    def setUpTestData(cls):
        cls.answers = factories.AnswersFactory()

    def _get_trail_view(self, view_class):
        # The same trail jumping code for all tests
        self.trail = ["Start", view_class]
        self.view = getattr(views, view_class)
        url_name = snake_case(view_class, separator="-")

        return self._get_page(f"questionnaire:{url_name}")

    def test_start_renders(self):
        response = self._get_page()
        assert response.status_code == 200

    def test_respondent_name_renders(self):
        assert self._get_trail_view("RespondentName").status_code == 200

    def test_respondent_role_renders(self):
        assert self._get_trail_view("RespondentRole").status_code == 200

    def test_respondent_relationship_renders(self):
        assert self._get_trail_view("RespondentRelationship").status_code == 200

    def test_need_permission_renders(self):
        assert self._get_trail_view("NeedPermission").status_code == 200

        # As this view should delete the answers we'll set some more.
        # (TODO NB this should be tested elsewhere)
        self.answers = factories.AnswersFactory()

    def test_respondent_postcode_renders(self):
        assert self._get_trail_view("Postcode").status_code == 200

    @mock.patch("prospector.apis.ideal_postcodes.get_for_postcode")
    def test_respondent_address_renders(self, get_for_postcode):
        get_for_postcode.return_value = []

        assert self._get_trail_view("RespondentAddress").status_code == 200

    def test_respondent_email_renders(self):
        assert self._get_trail_view("Email").status_code == 200

    def test_contact_phone_renders(self):
        assert self._get_trail_view("ContactPhone").status_code == 200

    def test_occupant_name_renders(self):
        assert self._get_trail_view("OccupantName").status_code == 200

    def test_property_postcode_renders(self):
        assert self._get_trail_view("PropertyPostcode").status_code == 200

    @mock.patch("prospector.apis.ideal_postcodes.get_for_postcode")
    def test_property_address_renders(self, get_for_postcode):
        get_for_postcode.return_value = []

        assert self._get_trail_view("PropertyAddress").status_code == 200

    def test_property_ownership_renders(self):
        assert self._get_trail_view("PropertyOwnership").status_code == 200

    def test_consents_renders(self):
        assert self._get_trail_view("Consents").status_code == 200

    @mock.patch("prospector.apis.epc.get_for_postcode")
    def test_select_epc_renders(self, get_for_postcode):
        get_for_postcode.return_value = [FAKE_EPC]
        self.answers.uprn = FAKE_EPC.uprn

        assert self._get_trail_view("SelectEPC").status_code == 200

    def test_property_type_renders(self):
        assert self._get_trail_view("PropertyType").status_code == 200

    def test_property_age_band_renders(self):
        assert self._get_trail_view("PropertyAgeBand").status_code == 200

    def test_wall_type_renders(self):
        assert self._get_trail_view("WallType").status_code == 200

    def test_walls_insulated_renders(self):
        assert self._get_trail_view("WallsInsulated").status_code == 200

    def test_floor_type_renders(self):
        assert self._get_trail_view("SuspendedFloor").status_code == 200

    def test_unheated_loft_renders(self):
        assert self._get_trail_view("UnheatedLoft").status_code == 200

    def test_room_in_roof_renders(self):
        assert self._get_trail_view("RoomInRoof").status_code == 200

    def test_rir_insulated_renders(self):
        assert self._get_trail_view("RoomInRoof").status_code == 200

    def test_roof_space_insulated_renders(self):
        assert self._get_trail_view("RoofSpaceInsulated").status_code == 200

    def test_flat_roof_renders(self):
        assert self._get_trail_view("FlatRoof").status_code == 200

    def test_flat_roof_age_renders(self):
        assert self._get_trail_view("FlatRoofModern").status_code == 200

    def test_gas_boiler_present_renders(self):
        assert self._get_trail_view("GasBoilerPresent").status_code == 200


# TODO tests to write
# confirm that reaching needs_permission deletes the Answers
# confirm that relationship_other is required if selecting other
# confirm that ContactPhone redirects according to is_occupant

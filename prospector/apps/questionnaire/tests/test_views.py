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

    def test_start_renders(self):
        response = self._get_page()
        assert response.status_code == 200

    def test_respondent_name_renders(self):
        self.trail = ["Start", "RespondentName"]
        self.view = views.RespondentName

        response = self._get_page("questionnaire:respondent-name")
        assert response.status_code == 200

    def test_respondent_role_renders(self):
        self.trail = ["Start", "RespondentRole"]
        self.view = views.RespondentRole

        response = self._get_page("questionnaire:respondent-role")
        assert response.status_code == 200

    def test_respondent_relationship_renders(self):
        self.trail = ["Start", "RespondentRelationship"]
        self.view = views.RespondentRelationship

        response = self._get_page("questionnaire:respondent-relationship")
        assert response.status_code == 200

    def test_need_permission_renders(self):
        self.trail = ["Start", "NeedPermission"]
        self.view = views.NeedPermission

        response = self._get_page("questionnaire:need-permission")
        assert response.status_code == 200

        # As this view should delete the answers we'll set some more.
        # (NB this should be tested elsewhere)
        self.answers = factories.AnswersFactory()

    def test_respondent_postcode_renders(self):
        self.trail = ["Start", "Postcode"]
        self.view = views.Postcode

        response = self._get_page("questionnaire:postcode")
        assert response.status_code == 200

    @mock.patch("prospector.apis.ideal_postcodes.get_for_postcode")
    def test_respondent_address_renders(self, get_for_postcode):
        get_for_postcode.return_value = []

        self.trail = ["Start", "RespondentAddress"]
        self.view = views.RespondentAddress

        response = self._get_page("questionnaire:your-address")
        assert response.status_code == 200

    def test_respondent_email_renders(self):
        self.trail = ["Start", "Email"]
        self.view = views.Email

        response = self._get_page("questionnaire:email")
        assert response.status_code == 200

    def test_contact_phone_renders(self):
        self.trail = ["Start", "ContactPhone"]
        self.view = views.ContactPhone

        response = self._get_page("questionnaire:contact-phone")
        assert response.status_code == 200

    def test_occupant_name_renders(self):
        self.trail = ["Start", "OccupantName"]
        self.view = views.OccupantName

        response = self._get_page("questionnaire:occupant-name")
        assert response.status_code == 200

    def test_property_postcode_renders(self):
        self.trail = ["Start", "PropertyPostcode"]
        self.view = views.PropertyPostcode

        response = self._get_page("questionnaire:property-postcode")
        assert response.status_code == 200

    @mock.patch("prospector.apis.ideal_postcodes.get_for_postcode")
    def test_property_address_renders(self, get_for_postcode):
        get_for_postcode.return_value = []

        self.trail = ["Start", "PropertyAddress"]
        self.view = views.PropertyAddress

        response = self._get_page("questionnaire:property-address")
        assert response.status_code == 200

    def test_property_ownership_renders(self):
        self.trail = ["Start", "PropertyOwnership"]
        self.view = views.PropertyOwnership

        response = self._get_page("questionnaire:property-ownership")
        assert response.status_code == 200

    def test_consents_renders(self):
        self.trail = ["Start", "Consents"]
        self.view = views.Consents

        response = self._get_page("questionnaire:consents")
        assert response.status_code == 200

    @mock.patch("prospector.apis.epc.get_for_postcode")
    def test_select_epc_renders(self, get_for_postcode):
        get_for_postcode.return_value = [FAKE_EPC]

        self.trail = ["Start", "SelectEPC"]
        self.view = views.SelectEPC
        self.answers.uprn = FAKE_EPC.uprn

        response = self._get_page("questionnaire:select-e-p-c")
        assert response.status_code == 200


# TODO tests to write
# confirm that reaching needs_permission deletes the Answers
# confirm that relationship_other is required if selecting other
# confirm that ContactPhone redirects according to is_occupant

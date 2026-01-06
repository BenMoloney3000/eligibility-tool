from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import override_settings
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import factories
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire.views import trail as views
from prospector.testutils import add_middleware_to_request
from prospector.trail.mixin import snake_case


def _html(response):
    response.render()
    return response.content.decode("utf-8")


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

    def _get_trail_view(self, view_class: str):
        # The same trail jumping code for all tests
        if view_class != "Start":
            self.trail = ["Start", view_class]
        self.view = getattr(views, view_class)
        url_name = snake_case(view_class, separator="-")

        return self._get_page(f"questionnaire:{url_name}")

    def _post_trail_data(self, view_class, postdata):
        # The same trail jumping code for all tests
        self.trail = ["Start", view_class]
        self.view = getattr(views, view_class)
        url_name = snake_case(view_class, separator="-")

        return self._submit_form(postdata, f"questionnaire:{url_name}")


class TestQuestionsRender(TrailTest):
    @classmethod
    def setUpTestData(cls):
        cls.answers = factories.AnswersFactory()

    def test_start_renders(self):
        response = self._get_trail_view("Start")
        assert response.status_code == 200

    def test_consents_renders(self):
        assert self._get_trail_view("Consents").status_code == 200

    def test_respondent_name_renders(self):
        assert self._get_trail_view("RespondentName").status_code == 200

    def test_respondent_email_renders(self):
        assert self._get_trail_view("Email").status_code == 200

    def test_contact_phone_renders(self):
        assert self._get_trail_view("ContactPhone").status_code == 200

    def test_respondent_role_renders(self):
        assert self._get_trail_view("RespondentRole").status_code == 200

    def test_respondent_has_permission_renders(self):
        assert self._get_trail_view("RespondentHasPermission").status_code == 200

    def test_company_name_renders(self):
        assert self._get_trail_view("CompanyName").status_code == 200

    def test_respondent_postcode_renders(self):
        assert self._get_trail_view("RespondentPostcode").status_code == 200

    @mock.patch("prospector.apps.questionnaire.selectors.get_postcode")
    def test_respondent_address_renders(self, get_postcode):
        get_postcode.return_value = []

        assert self._get_trail_view("RespondentAddress").status_code == 200

    def test_property_postcode_renders(self):
        assert self._get_trail_view("PropertyPostcode").status_code == 200

    @mock.patch("prospector.apis.data8.get_for_postcode")
    def test_property_address_renders(self, get_for_postcode):
        get_for_postcode.return_value = []

        assert self._get_trail_view("PropertyAddress").status_code == 200

    def test_address_unknown_renders(self):
        assert self._get_trail_view("AddressUnknown").status_code == 200

    def test_thabnk_you_renders(self):
        assert self._get_trail_view("ThankYou").status_code == 200

    def test_tenure_renders(self):
        assert self._get_trail_view("Tenure").status_code == 200

    def test_property_measures_renders(self):
        assert self._get_trail_view("PropertyMeasuresSummary").status_code == 200

    def test_occupant_name_renders(self):
        assert self._get_trail_view("OccupantName").status_code == 200

    def test_occupants_renders(self):
        assert self._get_trail_view("Occupants").status_code == 200

    def test_means_tested_benefits_renders(self):
        assert self._get_trail_view("MeansTestedBenefits").status_code == 200

    def test_vulnerabilities_general_renders(self):
        assert self._get_trail_view("VulnerabilitiesGeneral").status_code == 200

    def test_vulnerabilities_renders(self):
        assert self._get_trail_view("Vulnerabilities").status_code == 200

    def test_household_income_renders(self):
        assert self._get_trail_view("HouseholdIncome").status_code == 200

    def test_housing_costs_renders(self):
        assert self._get_trail_view("HousingCosts").status_code == 200

    def test_energy_advices_renders(self):
        assert self._get_trail_view("EnergyAdvices").status_code == 200

    def test_answers_summary_renders(self):
        assert self._get_trail_view("AnswersSummary").status_code == 200

    def test_recommended_measures_renders(self):
        assert self._get_trail_view("RecommendedMeasures").status_code == 200


class TestDataPosts(TrailTest):
    """Test page submission logic in views.py."""

    @classmethod
    def setUpTestData(cls):
        cls.answers = factories.AnswersFactory()

    def test_generic_single_question_saves(self):
        # Test an example of a generic SingleQuestion view

        submitted_value = enums.Tenure.RENTED_PRIVATE

        response = self._post_trail_data("Tenure", {"field": submitted_value.value})

        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert self.answers.tenure == submitted_value


class SpecialCases(TrailTest):
    def setUp(self):
        self.answers = factories.AnswersFactory()

    def test_cant_edit_completed_questionnaire(self):
        self.answers.completed_at = timezone.now()
        self.answers.save()
        response = self._get_trail_view("ContactPhone")

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:start")

    # TODO test postcode caching - should be in test_services tho'


class TestPropertyPostcode(TrailTest):
    """Test that the redirects work correctly for the repeating questions."""

    @classmethod
    def setUpTestData(cls):
        cls.answers = factories.AnswersFactory()

    @mock.patch("prospector.apis.data8.get_for_postcode")
    def test_validate_normalised_postcode_area(self, get_for_postcode):
        get_for_postcode.return_value = []
        response = self._post_trail_data(
            "PropertyPostcode",
            {
                "field": "pl6 5ah",
            },
        )
        assert response.status_code == 302

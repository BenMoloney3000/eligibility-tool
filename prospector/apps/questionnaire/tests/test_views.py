from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import override_settings
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from . import factories
from prospector.apps.questionnaire import views
from prospector.testutils import add_middleware_to_request


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


# TODO tests to write
# confirm that reaching needs_permission deletes the Answers
# confirm that relationship_other is required if selecting other
# confirm that ContactPhone redirects according to is_occupant

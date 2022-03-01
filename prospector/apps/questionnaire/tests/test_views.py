from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import override_settings
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from . import factories
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import models
from prospector.apps.questionnaire import views
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

    def _get_trail_view(self, view_class):
        # The same trail jumping code for all tests
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
        response = self._get_page()
        assert response.status_code == 200

    def test_respondent_name_renders(self):
        assert self._get_trail_view("RespondentName").status_code == 200

    def test_respondent_role_renders(self):
        assert self._get_trail_view("RespondentRole").status_code == 200

    def test_respondent_has_permission_renders(self):
        assert self._get_trail_view("RespondentHasPermission").status_code == 200

    def test_need_permission_renders(self):
        assert self._get_trail_view("NeedPermission").status_code == 200

        # As this view should delete the answers we'll set some more.
        self.answers = factories.AnswersFactory()

    def test_respondent_postcode_renders(self):
        assert self._get_trail_view("RespondentPostcode").status_code == 200

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
        get_for_postcode.return_value = [factories.FAKE_EPC]
        self.answers.uprn = factories.FAKE_EPC.uprn

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

    def test_floor_insulated_renders(self):
        assert self._get_trail_view("SuspendedFloorInsulated").status_code == 200

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

    def test_flat_roof_insulated_renders(self):
        assert self._get_trail_view("FlatRoofInsulated").status_code == 200

    def test_gas_boiler_present_renders(self):
        assert self._get_trail_view("GasBoilerPresent").status_code == 200

    def test_hwt_present_renders(self):
        assert self._get_trail_view("HwtPresent").status_code == 200

    def test_on_mains_gas_renders(self):
        assert self._get_trail_view("OnMainsGas").status_code == 200

    def test_other_heating_renders(self):
        assert self._get_trail_view("OtherHeatingPresent").status_code == 200

    def test_heat_pump_present_renders(self):
        assert self._get_trail_view("HeatPumpPresent").status_code == 200

    def test_other_heating_fuel_renders(self):
        assert self._get_trail_view("OtherHeatingFuel").status_code == 200

    def test_gas_boiler_age_renders(self):
        assert self._get_trail_view("GasBoilerAge").status_code == 200

    def test_gas_boiler_broken_renders(self):
        assert self._get_trail_view("GasBoilerBroken").status_code == 200

    def test_heating_controls_renders(self):
        assert self._get_trail_view("HeatingControls").status_code == 200

    def test_storage_heaters_renders(self):
        assert self._get_trail_view("StorageHeatersPresent").status_code == 200

    def test_hhrshs_present_renders(self):
        assert self._get_trail_view("HhrshsPresent").status_code == 200

    def test_electric_radiators_present_renders(self):
        assert self._get_trail_view("ElectricRadiatorsPresent").status_code == 200

    def test_in_conservation_area_renders(self):
        assert self._get_trail_view("InConservationArea").status_code == 200

    def test_accuracy_warning_renders(self):
        assert self._get_trail_view("AccuracyWarning").status_code == 200

    def test_recommended_measures_renders(self):
        assert self._get_trail_view("RecommendedMeasures").status_code == 200

    def test_tolerated_disruption_renders(self):
        assert self._get_trail_view("ToleratedDisruption").status_code == 200

    def test_moitivations_renders(self):
        assert self._get_trail_view("Motivations").status_code == 200

    def test_property_eligibility_renders(self):
        assert self._get_trail_view("PropertyEligibility").status_code == 200


class TestDataPosts(TrailTest):
    """Test page submission logic in views.py."""

    @classmethod
    def setUpTestData(cls):
        cls.answers = factories.AnswersFactory()

    def test_generic_single_question_saves(self):
        # Test an example of a generic SingleQuestion view

        submitted_value = enums.PropertyOwnership.PRIVATE_TENANCY

        response = self._post_trail_data(
            "PropertyOwnership", {"field": submitted_value.value}
        )

        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert self.answers.property_ownership == submitted_value

    def test_generic_prepopped_question_saves_confirm(self):
        # Test an example of a generic SinglePrepoppedQuestion confirming data

        self.answers.property_age_band_orig = enums.PropertyAgeBand.FROM_1930
        self.answers.save()

        submitted_value_to_be_ignored = enums.PropertyAgeBand.FROM_1976

        response = self._post_trail_data(
            "PropertyAgeBand",
            {
                "field": submitted_value_to_be_ignored.value,
                "data_correct": "True",
            },
        )

        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert self.answers.property_age_band == self.answers.property_age_band_orig

    def test_generic_prepopped_question_saves_overwrite(self):
        # Test an example of a generic SinglePrepoppedQuestion overwriting data

        self.answers.property_age_band_orig = enums.PropertyAgeBand.FROM_1930
        self.answers.save()

        submitted_corrected_value = enums.PropertyAgeBand.FROM_1976

        response = self._post_trail_data(
            "PropertyAgeBand",
            {
                "field": submitted_corrected_value.value,
                "data_correct": "False",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert self.answers.property_age_band == submitted_corrected_value


class SpecialCases(TrailTest):
    def setUp(self):
        self.answers = factories.AnswersFactory()

    def test_needs_permission_deletes(self):
        # Test the selective redirect to needs_permission and consequent deletion of the answers

        response = self._get_trail_view("NeedPermission")

        assert response.status_code == 200
        with self.assertRaises(models.Answers.DoesNotExist):
            self.answers.refresh_from_db()

    # TODO test postcode caching

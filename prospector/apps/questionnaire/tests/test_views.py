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

    def test_inferred_data_renders(self):
        assert self._get_trail_view("InferredData").status_code == 200

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

    def test_occupants_renders(self):
        assert self._get_trail_view("Occupants").status_code == 200

    def test_household_income_renders(self):
        assert self._get_trail_view("HouseholdIncome").status_code == 200

    def test_household_take_home_income_renders(self):
        assert self._get_trail_view("HouseholdTakeHomeIncome").status_code == 200

    def test_disability_benefits_renders(self):
        assert self._get_trail_view("DisabilityBenefits").status_code == 200

    def test_child_benefit_renders(self):
        assert self._get_trail_view("ChildBenefit").status_code == 200

    def test_income_lt_child_benefit_threshold_renders(self):
        # Need to set the threshold!
        self.answers.adults = 2
        self.answers.children = 2
        self.answers.child_benefit = True
        self.answers.save()
        assert self._get_trail_view("IncomeLtChildBenefitThreshold").status_code == 200

    def test_vulnerabilities_renders(self):
        assert self._get_trail_view("Vulnerabilities").status_code == 200

    def test_recommended_measures_renders(self):
        assert self._get_trail_view("RecommendedMeasures").status_code == 200

    def test_tolerated_disruption_renders(self):
        assert self._get_trail_view("ToleratedDisruption").status_code == 200

    def test_state_of_repair_renders(self):
        assert self._get_trail_view("StateOfRepair").status_code == 200

    def test_motivations_renders(self):
        assert self._get_trail_view("Motivations").status_code == 200

    def test_contribution_capacity_renders(self):
        assert self._get_trail_view("ContributionCapacity").status_code == 200

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


class TestInferredData(TrailTest):
    """Test the various redirections & saves that may happen from this page."""

    _no_correction_postdata = {
        "will_correct_type": "False",
        "will_correct_walls": "False",
        "will_correct_roof": "False",
        "will_correct_floor": "False",
        "will_correct_heating": "False",
    }

    def test_no_correction_missing_property_type(self):
        # Should not save any data and send the user to PropertyType
        self.answers = factories.AnswersFactory()
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:property-type")
        assert self.answers.property_age_band is None
        assert self.answers.property_type == ""
        assert self.answers.property_form == ""

    def test_no_correction_missing_property_form(self):
        # Should not save any data and send the user to PropertyType
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:property-type")
        assert self.answers.property_age_band is None
        assert self.answers.property_type == ""
        assert self.answers.property_form == ""

    def test_no_correction_missing_property_age(self):
        # Should not save any data and send the user to PropertyType
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:property-type")
        assert self.answers.property_type == ""
        assert self.answers.property_form == ""

    def test_no_correction_missing_wall_type(self):
        # Should save property type data and send the user to WallType
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:wall-type")
        assert self.answers.property_type == enums.PropertyType.BUNGALOW.value
        assert self.answers.property_form == enums.PropertyForm.SEMI_DETACHED.value
        assert self.answers.property_age_band == enums.PropertyAgeBand.FROM_1950.value

    def test_no_correction_missing_wall_insulation(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:wall-type")
        assert self.answers.wall_type == ""

    def test_no_correction_missing_floor_type(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:suspended-floor")
        assert self.answers.wall_type == enums.WallType.CAVITY.value
        assert self.answers.walls_insulated is True

    def test_no_correction_missing_required_floor_insulation(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:suspended-floor")
        assert self.answers.suspended_floor is None

    def test_no_correction_missing_non_required_floor_insulation(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=False,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:unheated-loft")
        assert self.answers.suspended_floor is False

    def test_no_correction_missing_unheated_loft(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=True,
            suspended_floor_insulated_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:unheated-loft")
        assert self.answers.suspended_floor is True
        assert self.answers.suspended_floor_insulated is True

    def test_no_correction_missing_room_in_roof(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=True,
            suspended_floor_insulated_orig=True,
            unheated_loft_orig=False,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:unheated-loft")
        assert self.answers.unheated_loft is None

    def test_no_correction_missing_rir_insulated(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=True,
            suspended_floor_insulated_orig=True,
            unheated_loft_orig=False,
            room_in_roof_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:unheated-loft")
        assert self.answers.unheated_loft is None
        assert self.answers.room_in_roof is None

    def test_no_correction_missing_flat_roof(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=True,
            suspended_floor_insulated_orig=True,
            unheated_loft_orig=False,
            room_in_roof_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:unheated-loft")
        assert self.answers.unheated_loft is None
        assert self.answers.room_in_roof is None

    def test_no_correction_missing_flat_roof_insulated(self):
        # It will always be missing in this circumstance.
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=True,
            suspended_floor_insulated_orig=True,
            unheated_loft_orig=False,
            room_in_roof_orig=True,
            flat_roof_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:unheated-loft")
        assert self.answers.unheated_loft is None
        assert self.answers.room_in_roof is None
        assert self.answers.flat_roof is None

    def test_no_correction_missing_loft_insulation(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=False,
            unheated_loft_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:unheated-loft")
        assert self.answers.unheated_loft is None

    def test_no_correction_missing_gas_boiler(self):
        # Complete the whole of the roof section
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=False,
            unheated_loft_orig=True,
            roof_space_insulated_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:gas-boiler-present")
        assert self.answers.unheated_loft is True
        assert self.answers.roof_space_insulated is True

    def test_no_correction_missing_other_heating(self):
        # Complete the whole of the roof section
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=False,
            unheated_loft_orig=True,
            roof_space_insulated_orig=True,
            gas_boiler_present_orig=False,
            on_mains_gas_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:gas-boiler-present")
        assert self.answers.gas_boiler_present is None

    def test_no_correction_missing_storage_heaters(self):
        # Tests that controls get ignored
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=False,
            unheated_loft_orig=True,
            roof_space_insulated_orig=True,
            gas_boiler_present_orig=False,
            on_mains_gas_orig=True,
            other_heating_present_orig=False,
            room_thermostat_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:gas-boiler-present")
        assert self.answers.gas_boiler_present is None
        assert self.answers.other_heating_present is None
        assert self.answers.room_thermostat is None

    def test_no_corrections_to_complete_set_of_inferences(self):
        # Tests that controls get ignored
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=False,
            unheated_loft_orig=True,
            roof_space_insulated_orig=True,
            gas_boiler_present_orig=False,
            on_mains_gas_orig=True,
            other_heating_present_orig=False,
            storage_heaters_present_orig=False,
            electric_radiators_present_orig=True,
        )
        response = self._post_trail_data("InferredData", self._no_correction_postdata)
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:in-conservation-area")
        assert self.answers.gas_boiler_present is False
        assert self.answers.other_heating_present is False
        assert self.answers.storage_heaters_present is False

    """
    # Now test the scenarios where the user *does* want to correct stuff
    """

    def test_correct_complete_property_type(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
        )
        response = self._post_trail_data(
            "InferredData",
            {
                "will_correct_type": "True",
                "will_correct_walls": "True",
                "will_correct_floor": "True",
                "will_correct_roof": "True",
                "will_correct_heating": "True",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:property-type")
        assert self.answers.property_type == ""
        assert self.answers.property_form == ""
        assert self.answers.property_age_band is None

    def test_correct_complete_walls(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
        )
        response = self._post_trail_data(
            "InferredData",
            {
                "will_correct_type": "False",
                "will_correct_walls": "True",
                "will_correct_floor": "True",
                "will_correct_roof": "True",
                "will_correct_heating": "True",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:wall-type")
        assert self.answers.property_type == enums.PropertyType.BUNGALOW.value
        assert self.answers.property_form == enums.PropertyForm.SEMI_DETACHED.value
        assert self.answers.property_age_band == enums.PropertyAgeBand.FROM_1950.value
        assert self.answers.wall_type == ""
        assert self.answers.walls_insulated is None

    def test_correct_complete_floors(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=True,
            suspended_floor_insulated_orig=True,
        )
        response = self._post_trail_data(
            "InferredData",
            {
                "will_correct_type": "False",
                "will_correct_walls": "False",
                "will_correct_floor": "True",
                "will_correct_roof": "True",
                "will_correct_heating": "True",
            },
        )

        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:suspended-floor")
        assert self.answers.wall_type == enums.WallType.CAVITY.value
        assert self.answers.walls_insulated is True

    def test_correct_complete_roof(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=False,
            unheated_loft_orig=True,
            roof_space_insulated_orig=True,
        )
        response = self._post_trail_data(
            "InferredData",
            {
                "will_correct_type": "False",
                "will_correct_walls": "False",
                "will_correct_floor": "False",
                "will_correct_roof": "True",
                "will_correct_heating": "True",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:unheated-loft")
        assert self.answers.wall_type == enums.WallType.CAVITY.value
        assert self.answers.walls_insulated is True

    def test_correct_complete_heating(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=False,
            unheated_loft_orig=True,
            roof_space_insulated_orig=True,
            gas_boiler_present_orig=False,
            other_heating_present_orig=False,
            storage_heaters_present_orig=False,
        )
        response = self._post_trail_data(
            "InferredData",
            {
                "will_correct_type": "False",
                "will_correct_walls": "False",
                "will_correct_floor": "False",
                "will_correct_roof": "False",
                "will_correct_heating": "True",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:gas-boiler-present")
        assert self.answers.unheated_loft is True
        assert self.answers.roof_space_insulated is True


class TestSkipForwards(TrailTest):
    """Test that the respondent's wishes to skip bits are respected."""

    def setUp(self):
        self.answers = factories.AnswersFactory(
            property_type_orig=enums.PropertyType.BUNGALOW,
            property_form_orig=enums.PropertyForm.SEMI_DETACHED,
            property_age_band_orig=enums.PropertyAgeBand.FROM_1950,
            wall_type_orig=enums.WallType.CAVITY,
            walls_insulated_orig=True,
            suspended_floor_orig=False,
            suspended_floor_insulated_orig=False,
            unheated_loft_orig=True,
            rir_insulated_orig=False,
            flat_roof_orig=False,
            roof_space_insulated_orig=True,
            gas_boiler_present_orig=False,
            on_mains_gas_orig=True,
            other_heating_present_orig=False,
            storage_heaters_present_orig=False,
            electric_radiators_present_orig=True,
        )

    def test_skip_walls_from_age_band(self):
        # Skip from PropertyAgeBand to SuspendedFloor
        self.answers.will_correct_walls = False
        self.answers.will_correct_floor = True
        self.answers.save()

        response = self._post_trail_data(
            "PropertyAgeBand",
            {
                "data_correct": "True",
                "field": str(enums.PropertyAgeBand.FROM_1950.value),
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:suspended-floor")
        assert self.answers.property_age_band == enums.PropertyAgeBand.FROM_1950.value

    def test_skip_floors_from_walls_insulated(self):
        # Skip from WallsInsulated to UnheatedLoft
        self.answers.will_correct_floor = False
        self.answers.will_correct_roof = True
        self.answers.save()

        response = self._post_trail_data(
            "WallsInsulated",
            {
                "data_correct": "True",
                "field": "True",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:unheated-loft")
        assert self.answers.walls_insulated is True

    def test_skip_roof_from_suspended_floor(self):
        # Skip from SuspendedFloor to GasBoilerPresent
        self.answers.will_correct_roof = False
        self.answers.will_correct_heating = True
        self.answers.save()

        response = self._post_trail_data(
            "SuspendedFloor",
            {
                "data_correct": "True",
                "field": "False",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:gas-boiler-present")
        assert self.answers.suspended_floor is False

    def test_skip_roof_from_suspended_floor_insulated(self):
        # Skip from SuspendedFloorInsulated to GasBoilerPresent
        self.answers.will_correct_roof = False
        self.answers.will_correct_heating = True
        self.answers.save()

        response = self._post_trail_data(
            "SuspendedFloorInsulated",
            {
                "data_correct": "True",
                "field": "False",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:gas-boiler-present")
        assert self.answers.suspended_floor_insulated is False

    def test_skip_heating_from_rir_insulated(self):
        # Skip from RirInsulated to ConservationArea
        self.answers.will_correct_heating = False
        self.answers.save()

        response = self._post_trail_data(
            "RirInsulated",
            {
                "data_correct": "True",
                "field": "False",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:in-conservation-area")
        assert self.answers.rir_insulated is False

    def test_skip_heating_from_flat_roof(self):
        # Skip from FlatRoof to ConservationArea
        self.answers.will_correct_heating = False
        self.answers.save()

        response = self._post_trail_data(
            "FlatRoof",
            {
                "data_correct": "True",
                "field": "False",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:in-conservation-area")
        assert self.answers.flat_roof is False

    def test_skip_heating_from_flat_roof_insulated(self):
        # Skip from FlatRoof to ConservationArea
        self.answers.will_correct_heating = False
        self.answers.save()

        response = self._post_trail_data(
            "FlatRoofInsulated", {"field": enums.InsulationConfidence.PROBABLY.value}
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:in-conservation-area")
        assert (
            self.answers.flat_roof_insulated
            == enums.InsulationConfidence.PROBABLY.value
        )

    def test_skip_heating_from_roof_space_insulated(self):
        # Skip from RoofSpaceInsulated to ConservationArea
        self.answers.will_correct_heating = False
        self.answers.save()

        response = self._post_trail_data(
            "RoofSpaceInsulated",
            {
                "data_correct": "True",
                "field": "True",
            },
        )
        self.answers.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("questionnaire:in-conservation-area")
        assert self.answers.roof_space_insulated is True

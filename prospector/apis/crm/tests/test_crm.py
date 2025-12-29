import json
import os
from datetime import datetime

import pytest
import requests
from django.utils.timezone import make_aware
from factory.django import DjangoModelFactory

from prospector.apis.crm import crm
from prospector.apps.crm import tasks
from prospector.apps.crm.models import CrmResult
from prospector.apps.crm.models import CrmState
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import services


@pytest.fixture
def mock_crm_response(mock_crm_api_settings):
    # settings = mock_crm_api_settings
    default_mock_response_data = {
        "@odata.context": (
            "https://plymouthenergycommunity.crm4.dynamics.com/api/data/v9.1/"
            "$metadata#pcc_retrofitintermediates/$entity"
        ),
        "@odata.etag": 'W/"66377597"',
        "_createdby_value": "c1f33749-6212-ed11-b83d-000d3a3a2991",
        "_createdonbehalfby_value": None,
        "_modifiedby_value": "c1f33749-6212-ed11-b83d-000d3a3a2991",
        "_modifiedonbehalfby_value": None,
        "_ownerid_value": "c1f33749-6212-ed11-b83d-000d3a3a2991",
        "_owningbusinessunit_value": "95994ab8-738d-e311-9fb9-6c3be5be2f78",
        "_owningteam_value": None,
        "_owninguser_value": "c1f33749-6212-ed11-b83d-000d3a3a2991",
        "_pcc_contactlookup_value": None,
        "_pcc_domesticpropertylookup_value": None,
        "_pcc_landlordlookup_value": None,
        "_pcc_retrofitprojectlookup_value": None,
        "_stageid_value": None,
        "cr51a_childbenefitclaimantsingleorcouple": 106870000,
        "cr51a_counciltaxbracket": None,
        "cr51a_propertyattachment": 106870000,
        "cr51a_boilerefficiency": 106870000,
        "cr51a_lodgedepcband": 106870000,
        "cr51a_sapband": 106870000,
        "cr51a_65andover": 0,
        "cr51a_adults": 2,
        "cr51a_childbenefitqualifyingchildren": 1,
        "cr51a_children": 1,
        "cr51a_childreneligibleforfreeschoolmeals": False,
        "cr51a_counciltaxreductionentitlement": False,
        "cr51a_consented_callback": False,
        "cr51a_consented_future_schemes": False,
        "cr51a_heatedrooms": 2,
        "cr51a_heatingcontrolsadequacy": 106870000,
        "cr51a_householdincome": 40000,
        "cr51a_householdincome_base": 40000,
        "cr51a_householdsavings": None,
        "cr51a_householdsavings_base": None,
        "cr51a_housingcosts": 2000,
        "cr51a_housingcosts_base": 2000,
        "cr51a_imd_decile": 8,
        "cr51a_incomeafterhousingcosts": 38000,
        "cr51a_incomeafterhousingcosts_base": 38000,
        "cr51a_lodgedepcscore": 52,
        "cr51a_lowersuperoutputareacode": None,
        "cr51a_othervulnerabilitytothecold": None,
        "cr51a_paritysapscore": 54,
        "cr51a_potentialmeasures": None,
        "cr51a_potentialschemeeligibility": None,
        "cr51a_realisticfuelbill": "£857",
        "cr51a_receiveschildbenefit": True,
        "cr51a_receivesmeanstestedbenefits": False,
        "cr51a_respondent_comments": "Test comment",
        "cr51a_respondent_relationship_to_property": 106870000,
        "cr51a_respondentemailadress": "example@example.com",
        "cr51a_respondentfirstname": "Test",
        "cr51a_respondentlastname": "Entry",
        "cr51a_respondentmobile": "+441234777888",
        "cr51a_respondentphonenumber": "+441234777888",
        "cr51a_respondentrelationshiptooccupier": None,
        "cr51a_shortid": "13971R3AAH",
        "cr51a_tco2current": 5.5,
        "cr51a_tenure": 798360001,
        "cr51a_uprn": "100040423808",
        "cr51a_vulnerabilitytothecold": False,
        "cr51a_vulnerabilitytothecold_cardiovascular": None,
        "cr51a_vulnerabilitytothecold_respiratory": None,
        "cr51a_vulnerabilitytothecold_mentalhealth": None,
        "cr51a_vulnerabilitytothecold_disabledltdmob": None,
        "cr51a_vulnerabilitytothecold_65plus": None,
        "cr51a_vulnerabilitytothecold_youngchildren": None,
        "cr51a_vulnerabilitytothecold_pregnancy": None,
        "cr51a_vulnerabilitytothecold_immunosuppression": None,
        "cr51a_nmt4properties": None,
        "cr51a_advice_needed_warm": False,
        "cr51a_advice_needed_bills": False,
        "cr51a_advice_needed_supplier": False,
        "cr51a_advice_needed_from_team": False,
        "cr51a_past_means_tested_benefits": False,
        "cr51a_bus": False,
        "cr51a_cavity_wall_insulation": False,
        "cr51a_heat_pump": False,
        "cr51a_loft_insulation": False,
        "cr51a_low_carbon_heating_upgrade": True,
        "cr51a_rir_insulation": False,
        "cr51a_solarpv": False,
        "cr51a_solid_wall_insulation": False,
        "cr51a_underfloor_insulation": False,
        "createdon": "2022-11-20T23:23:54Z",
        "importsequencenumber": None,
        "modifiedon": "2022-11-20T23:23:54Z",
        "overriddencreatedon": None,
        "pcc_accountname": None,
        "pcc_address1city": None,
        "pcc_address1county": None,
        "pcc_address1street1": None,
        "pcc_address1street2": None,
        "pcc_address1street3": None,
        "pcc_address1zippostalcode": None,
        "pcc_bedrooms": None,
        "pcc_boilertype": None,
        "pcc_commentsondamp": None,
        "pcc_condensation": None,
        "pcc_county": None,
        "pcc_dateofmostrecentepc": None,
        "pcc_email": "example@example.com",
        "pcc_epctype": None,
        "pcc_ffversion": None,
        "pcc_firstname": "Test",
        "pcc_floorinsulation": None,
        "pcc_floortype": None,
        "pcc_glazing": 106870006,
        "pcc_gradeofmostrecentepc": None,
        "pcc_hasapgrade": None,
        "pcc_hasapscore": None,
        "pcc_heatingcontrols": None,
        "pcc_homephone": "+441234555666",
        "pcc_howdidyouhearaboutpec2": 798360015,
        "pcc_inscopeformees": None,
        "pcc_lastname": "Entry",
        "pcc_likelihoodofprivatelyrented": 798360003,
        "pcc_listedproperty": None,
        "pcc_lladdress1city": None,
        "pcc_lladdress1county": None,
        "pcc_lladdress1street1": None,
        "pcc_lladdress1street2": None,
        "pcc_lladdress1street3": None,
        "pcc_lladdress1zippostalcode": None,
        "pcc_llmainphone": None,
        "pcc_mobile": "+441234777888",
        "pcc_mouldgrowth": None,
        "pcc_name": "3eecd150-0ca7-48b1-9f5d-da4351f3cdf1",
        "pcc_occupanteligibilityscore": 798360000,
        "pcc_occupiedfrom": None,
        "pcc_occupiedto": None,
        "pcc_occupierrole": None,
        "pcc_postcode": "PL1 1AE",
        "pcc_primaryheatingdeliverymethod": None,
        "pcc_primaryheatingfuel": 798360004,
        "pcc_propertyage": None,
        "pcc_propertyeligibilityscore": 798360000,
        "pcc_propertyprofilecomments": None,
        "pcc_propertytype": None,
        "pcc_retrofitintermediateid": "9be2f162-2a69-ed11-9561-000d3abd864b",
        "pcc_roofinsulation": None,
        "pcc_rooftype": None,
        "pcc_salutation": None,
        "pcc_scoreofmostrecentepc": None,
        "pcc_secondaryheatingdeliverymethod": None,
        "pcc_secondaryheatingfuel": None,
        "pcc_solarpanels": None,
        "pcc_solarthermal": None,
        "pcc_street1": "Test Address Line 1",
        "pcc_street2": "Test Address Line 2",
        "pcc_street3": "Test Address Line 3",
        "pcc_structuraldamp": None,
        "pcc_towncity": "Test Address Line 3",
        "pcc_udprn": None,
        "pcc_udprncontact": None,
        "pcc_updateoptions": 798360003,
        "pcc_wallinsulation": None,
        "pcc_walltype": None,
        "pcc_website": None,
        "processid": None,
        "statecode": 0,
        "statuscode": 798360000,
        "timezoneruleversionnumber": None,
        "traversedpath": None,
        "utcconversiontimezonecode": None,
        "versionnumber": 66377597,
    }

    def get_mock_crm_response(query, mock_response_data={}, mock_request_method="GET"):
        # mock_uri = "%sapi/data/v9.1/%s" % (settings.CRM_API["RESOURCE"], query)
        return {**default_mock_response_data, **mock_response_data}

    return get_mock_crm_response


@pytest.fixture()
def mock_crm_api_settings(settings):
    settings.CRM_API = {
        "TENANT": "00000000-0000-0000-0000-000000000000",
        "RESOURCE": "https://test.crm4.dynamics.com/",
        "CLIENT_ID": "ffffffff-ffff-ffff-ffff-ffffffffffff",
        "CLIENT_SECRET": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    }
    return settings


@pytest.fixture()
def mock_session_token(mock_crm_api_settings, requests_mock):
    settings = mock_crm_api_settings

    mock_oauth_uri = "https://login.microsoftonline.com/%s/oauth2/token" % (
        settings.CRM_API["TENANT"],
    )

    dummy_token = {"access_token": "xxxxxx"}
    json_resp = json.dumps(dummy_token)
    mocker = requests_mock.register_uri("POST", mock_oauth_uri, text=json_resp)
    return (mocker, dummy_token)


@pytest.fixture()
def mock_crm_request(mock_crm_api_settings, requests_mock):
    settings = mock_crm_api_settings

    def get_mock_crm_request(
        query, mock_response_data={}, mock_request_method="GET", mock_request_exc=None
    ):
        mock_uri = "%sapi/data/v9.1/%s" % (settings.CRM_API["RESOURCE"], query)
        mock_response = json.dumps(mock_response_data)
        return requests_mock.register_uri(
            mock_request_method, mock_uri, text=mock_response, exc=mock_request_exc
        )

    return get_mock_crm_request


@pytest.fixture()
def mock_crm_request_exc(mock_crm_api_settings, requests_mock):
    settings = mock_crm_api_settings

    def get_mock_crm_request(query, mock_request_method="GET", mock_request_exc=None):
        mock_uri = "%sapi/data/v9.1/%s" % (settings.CRM_API["RESOURCE"], query)
        return requests_mock.register_uri(
            mock_request_method, mock_uri, exc=mock_request_exc
        )

    return get_mock_crm_request


@pytest.mark.django_db
def test_crm_create(mock_session_token, mock_crm_request, mock_crm_response, answers):
    dummy_answers = answers()

    # mock request
    query = "pcc_retrofitintermediates"
    response = mock_crm_response(query)
    mocker = mock_crm_request(
        query, mock_request_method="post", mock_response_data=response
    )

    assert dummy_answers.crmresult_set.count() == 0
    tasks.crm_create(dummy_answers.uuid)
    assert mocker.call_count == 1
    assert dummy_answers.crmresult_set.count() == 1

    crmresult = dummy_answers.crmresult_set.get()
    assert crmresult.result["pcc_name"] == response["pcc_name"]
    assert crmresult.state == CrmState.SUCCESS


@pytest.mark.django_db
def test_crm_create_with_timeout(mock_session_token, mock_crm_request_exc, answers):
    dummy_answers = answers()

    # mock request
    query = "pcc_retrofitintermediates"
    mocker = mock_crm_request_exc(
        query,
        mock_request_method="post",
        mock_request_exc=requests.exceptions.ConnectTimeout,
    )

    assert dummy_answers.crmresult_set.count() == 0
    with pytest.raises(requests.exceptions.ConnectTimeout):
        tasks.crm_create(dummy_answers.uuid)
        assert mocker.call_count == 1
        assert dummy_answers.crmresult_set.count() == 1

    crmresult = dummy_answers.crmresult_set.get()
    assert crmresult.state == CrmState.FAILURE


@pytest.fixture()
def pcc_entity_definitions(request):
    fixture_dir = os.path.dirname(request.module.__file__)
    pcc_entity_definitions = os.path.join(fixture_dir, "../entity_definitions.json")
    with open(pcc_entity_definitions) as f:
        return json.load(f)


def test_get_bearer_token(
    mock_crm_api_settings,
    mock_session_token,
):
    _, dummy_token = mock_session_token
    client = crm.get_client()
    session = crm.get_authorised_session(client)
    assert session.token == dummy_token


@pytest.mark.django_db
def test_map_crm(answers):
    dummy_answers = answers(
        # Force property_rating to be Red
        sap_score=65.1
    )
    crm_data = crm.map_crm(dummy_answers)
    assert crm_data["pcc_name"] == str(dummy_answers.uuid)
    assert crm_data["pcc_propertyeligibilityscore"] is None  # Red
    assert crm_data["pcc_occupanteligibilityscore"] is None  # Green


@pytest.mark.django_db
def test_map_crm_does_not_populate_udprn(answers):
    """Ensure UDPRN fields are always left empty in CRM payload."""
    dummy_answers = answers(
        property_udprn="1234567890",
        respondent_udprn="0987654321",
        uprn="100040423808",
    )
    crm_data = crm.map_crm(dummy_answers)
    assert crm_data["pcc_udprn"] is None
    assert crm_data["pcc_udprncontact"] is None
    assert crm_data["cr51a_uprn"] == "100040423808"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "property_ownership,expected",
    [
        (enums.Tenure.RENTED_PRIVATE, 798360001),  # High
    ]
    + [(o, 798360003) for o in enums.Tenure if o.name != "RENTED_PRIVATE"],  # Low
)
def test_map_pcc_likelihoodofprivatelyrented(answers, property_ownership, expected):
    dummy_answers = answers(tenure=property_ownership)
    crm_data = crm.map_crm(dummy_answers)
    assert crm_data["pcc_likelihoodofprivatelyrented"] == expected


@pytest.mark.django_db
def test_create_pcc_record(mock_session_token, mock_crm_request, answers):
    dummy_answers = answers()

    # Mock request
    query = "pcc_retrofitintermediates"
    mocker = mock_crm_request(query, mock_request_method="POST")

    client = crm.get_client()
    session = crm.get_authorised_session(client)
    dummy_crm_data = crm.map_crm(dummy_answers)
    crm.create_pcc_record(session, dummy_crm_data)

    # Requests method was called with the json data matching dummy_crm_data
    assert mocker.call_count == 1
    assert mocker.request_history[0].json() == dummy_crm_data


@pytest.fixture()
def crmresult():
    class CrmResultFactory(DjangoModelFactory):
        class Meta:
            model = CrmResult

    def get_crmresult(**factory_kwargs):
        return CrmResultFactory(**factory_kwargs)

    return get_crmresult


@pytest.mark.django_db
@pytest.mark.freeze_time("2022-05-10")
def test_answers_to_submit_returns_completed_records(answers, crmresult):
    def _answers(completed=False):
        answers_fixture = answers(
            completed_at=None if not completed else make_aware(datetime.now())
        )
        return answers_fixture

    expected_to_submit = [
        o
        for o in [_answers(completed=(i % 2 == 0)) for i in range(0, 10)]
        if o.completed_at is not None
    ]

    to_submit = crm.answers_to_submit()
    assert set(to_submit) == set(expected_to_submit)


@pytest.mark.django_db
@pytest.mark.freeze_time("2022-05-10")
def test_answers_to_submit_no_resubmit_with_crmresult(answers, crmresult):
    """Resubmit is not currently supported.

    Records that have been submitted (and have a crmresult) shouldn't be
    batched for submission.
    """

    def _answers_with_crmresult(create_crmresult=False):
        answers_fixture = answers(completed_at=make_aware(datetime.now()))
        if create_crmresult:
            crmresult(answers=answers_fixture)
        return answers_fixture

    dummy_answers_batch = [
        _answers_with_crmresult(create_crmresult=(i % 2 == 0)) for i in range(0, 10)
    ]

    # For now we don't support retrys, so only expect unsubmitted anwsers
    # records.
    unsubmitted_answers = crm.answers_to_submit()
    assert set(unsubmitted_answers) == set(dummy_answers_batch[1::2])


@pytest.mark.django_db
def test_close_questionnaire_calls_async_crm_create(mocker, answers):
    dummy_answers = answers()

    mock_task = mocker.patch("prospector.apps.crm.tasks.crm_create.delay")
    services.close_questionnaire(dummy_answers)
    assert mock_task.call_count == 1

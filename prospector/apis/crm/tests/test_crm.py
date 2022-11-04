import pytest
import json

from requests_mock import Adapter, ANY

from ..crm import (
    get_bearer_token,
    create_entry,
    get_fields
)


@pytest.fixture()
def mock_crm_api_settings(settings):
    settings.CRM_API = {
        "TENANT": "00000000-0000-0000-0000-000000000000",
        "RESOURCE": "https://test.crm4.dynamics.com/",
        "CLIENT_ID": "ffffffff-ffff-ffff-ffff-ffffffffffff",
        "CLIENT_SECRET": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }


def test_get_bearer_token(mock_crm_api_settings, requests_mock):
    json_resp = json.dumps({'access_token': 'xxxxxx'})
    requests_mock.register_uri(ANY, ANY, text=json_resp)
    requests_mock.post('mock://example.com/')
    assert get_bearer_token() == "xxxxxx"


def test_get_fields():
    fields = get_fields()
    __import__('pdb').set_trace()


def test_create_entry(mock_crm_api_settings, requests_mock):
    # create_entry(answers)
    pass

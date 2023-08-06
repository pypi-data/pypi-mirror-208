import pytest

from gantry.api_client import APIClient
from gantry.applications.client import ApplicationClient

HOST = "https://test-api"


@pytest.fixture
def test_api_client():
    return APIClient(origin=HOST)


@pytest.fixture
def test_client(test_api_client):
    return ApplicationClient(api_client=test_api_client)

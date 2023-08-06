import mock
import pytest
import responses
from responses import matchers

from gantry import api_client
from gantry.exceptions import GantryRequestException
from gantry.version import __version__

HOST = "http://test-api"
FAKE_API_KEY = "ABCD1234"


@mock.patch("gantry.api_client.platform")
def test_request_ua(mock_platform):
    mock_platform.python_implementation.return_value = "foo"
    mock_platform.python_version.return_value = "bar"
    mock_platform.system.return_value = "baz"
    mock_platform.machine.return_value = "qux"

    api_client_obj = api_client.APIClient(HOST, FAKE_API_KEY)

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/health",
            headers={"Content-Type": "application/json"},
            json={
                "response": "ok",
                "data": "foobar",
            },
            match=[
                matchers.header_matcher(
                    {
                        "User-Agent": f"gantry/{__version__} foo/bar baz qux",
                        "X-Gantry-Api-Key": FAKE_API_KEY,
                        "Other": "header",
                    }
                )
            ],
        )

        assert api_client_obj.request("GET", "/health", headers={"Other": "header"}) == {
            "response": "ok",
            "data": "foobar",
        }


def test_request_rate_limit(caplog):
    api_client_obj = api_client.APIClient(HOST, FAKE_API_KEY)
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/health",
            headers={"Content-Type": "application/json"},
            status=429,
            json={
                "response": "ok",
                "error": "something",
            },
        )

        assert api_client_obj.request("GET", "/health") == {
            "response": "ok",
            "error": "something",
        }

        with pytest.raises(GantryRequestException) as excinfo:
            api_client_obj.request("GET", "/health", raise_for_status=True)
        assert "Logger has hit the rate limit" in str(excinfo.value)


@pytest.mark.parametrize("status_code", list(range(400, 600)))
def test_request_raise_for_status(status_code):
    api_client_obj = api_client.APIClient(HOST, FAKE_API_KEY)
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/some_resource",
            headers={"Content-Type": "application/json"},
            status=status_code,
            json={
                "response": "ok",
            },
        )

        with pytest.raises(GantryRequestException):
            api_client_obj.request("GET", "/some_resource", raise_for_status=True)


@pytest.mark.parametrize(
    ("status_code", "text", "expected_error"),
    [
        (404, "[error-details123]", r"A resource was not found.+\[error\-details123\]"),
        (429, "", r"Logger has hit the rate limit."),
        (401, "", r"Authentication error. Ensure that you supplied a working API key"),
        (403, "", r"Access denied. Check with your organization admin or Gantry support"),
        (409, "[error-details123]", r"Malformed data error.+\[error\-details123\]"),
        (500, "", r"Internal Gantry error. Contact Gantry support for help."),
    ],
)
def test_request_error_messages(status_code, text, expected_error):
    api_client_obj = api_client.APIClient(HOST, FAKE_API_KEY)
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/some_resource",
            headers={"Content-Type": "application/json"},
            status=status_code,
            json={"response": text},
        )

        with pytest.raises(GantryRequestException, match=expected_error):
            api_client_obj.request("GET", "/some_resource", raise_for_status=True)

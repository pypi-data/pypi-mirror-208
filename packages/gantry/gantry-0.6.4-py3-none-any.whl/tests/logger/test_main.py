import os

import mock
import pytest

import gantry
from gantry.exceptions import ClientNotInitialized
from gantry.logger import main


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("ping", {}),
        ("ready", {}),
        ("log_record", {"application": "foobar", "version": "1.2.3"}),
        ("log_records", {"application": "foobar", "version": "1.2.3"}),
    ],
)
@pytest.mark.parametrize("module", [main, gantry])
def test_uninit_client_main(module, method, params):
    """Test all public methods from gantry module or gantry.main module
    fail if client is not initialized
    """
    with mock.patch("gantry.logger.main._CLIENT", None):
        with pytest.raises(ClientNotInitialized):
            getattr(module, method)(**params)


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("ping", {}),
        ("ready", {}),
        (
            "log_records",
            {
                "application": "foobar",
                "version": "1.2.3",
                "inputs": [1, 2, 3],
                "outputs": [4, 5, 6],
                "feedback_keys": ["A"],
                "feedback_ids": [10],
                "feedbacks": [4, 5, 6],
                "ignore_inputs": ["A"],
                "timestamps": "today",
                "sort_on_timestamp": True,
                "sample_rate": 1.0,
                "as_batch": False,
                "tags": {},
                "join_keys": ["foo", "bar"],
                "row_tags": [{}, {}, {}],
                "global_tags": {},
            },
        ),
        (
            "log_record",
            {
                "application": "foobar",
                "version": "1.2.3",
                "inputs": [1, 2, 3],
                "outputs": [4, 5, 6],
                "feedback_keys": ["A"],
                "feedback_id": [10],
                "feedback": [4, 5, 6],
                "ignore_inputs": ["A"],
                "timestamp": "today",
                "sample_rate": 1.0,
                "tags": {},
                "join_key": "foo",
            },
        ),
    ],
)
@pytest.mark.parametrize("module", [main, gantry])
def test_logger_methods(module, method, params):
    """Test all public methods from gantry module or gantry.main module
    resolve in the global _CLIENT methods
    """
    m = mock.Mock()
    with mock.patch("gantry.logger.main._CLIENT", m):
        getattr(m, method).return_value = "return_value"
        assert getattr(module, method)(**params) == "return_value"
        getattr(m, method).assert_called_once_with(**params)


@pytest.mark.parametrize(
    ["kwargs", "expected"],
    [
        (
            {"api_key": "12345"},
            ("12345", None, None, None),
        ),
        (
            {
                "api_key": "12345",
                "logging_level": "ERROR",
                "environment": "test",
                "send_in_background": False,
            },
            ("12345", "ERROR", "test", False),
        ),
    ],
)
@pytest.mark.parametrize("ping_ret", [True, False])
@mock.patch("gantry.logger.main.Gantry")
@mock.patch("gantry.logger.main._resolve_params")
def test_logger_init(mock_resolve_params, mock_gantry, ping_ret, kwargs, expected):
    """Test the initialzation flow"""
    mock_resolve_params.return_value = (
        "54321",
        "https://barbaz",
        "CRITICAL",
        "foobaz",
        False,
        False,
    )
    m = mock.Mock()
    m.ping = mock.Mock(return_value=ping_ret)
    mock_gantry.return_value = m

    main._init(**kwargs)

    assert main._CLIENT == m

    args, kwargs = mock_gantry.call_args
    store = args[0]
    assert store._api_client._host == "https://barbaz"
    assert store._api_client._api_key == "54321"
    assert store._bypass_firehose is False
    assert store.send_in_background is False

    assert args[1] == "foobaz"
    assert args[2] == "CRITICAL"

    mock_resolve_params.assert_called_once_with(*expected)
    m.ping.assert_called_once()
    if ping_ret:
        m.ready.assert_called_once()


@pytest.mark.parametrize(
    ["environ", "kwargs", "expected"],
    [
        (
            {},
            {
                "api_key": "12345",
                "logging_level": "ERROR",
                "environment": "test",
                "send_in_background": False,
            },
            ("12345", "https://app.gantry.io", "ERROR", "test", False, False),
        ),
        (
            {
                "GANTRY_API_KEY": "123456789",
                "GANTRY_LOGS_LOCATION": "https://barfoo",
                "GANTRY_LOGGING_LEVEL": "WARNING",
                "GANTRY_ENVIRONMENT": "another",
                "GANTRY_BYPASS_FIREHOSE": "true",
                "GANTRY_SEND_IN_BACKGROUND": "true",
            },
            {
                "api_key": "12345",
                "logging_level": "ERROR",
                "environment": "test",
                "send_in_background": False,
            },
            ("12345", "https://barfoo", "ERROR", "test", True, False),
        ),
        (
            {
                "GANTRY_API_KEY": "123456789",
                "GANTRY_LOGGING_LEVEL": "WARNING",
                "GANTRY_ENVIRONMENT": "another",
                "GANTRY_SEND_IN_BACKGROUND": "true",
            },
            {
                "logging_level": "ERROR",
                "environment": "test",
            },
            ("123456789", "https://app.gantry.io", "ERROR", "test", False, True),
        ),
        (
            {
                "GANTRY_API_KEY": "123456789",
            },
            {},
            ("123456789", "https://app.gantry.io", "INFO", "dev", False, True),
        ),
        (
            {
                "GANTRY_API_KEY": "123456789",
                "AWS_LAMBDA_FUNCTION_NAME": "foobar",
            },
            {},
            ("123456789", "https://app.gantry.io", "INFO", "dev", False, False),
        ),
    ],
)
def test_resolve_params(environ, kwargs, expected):
    """Test that passed parameters take precedence over env vars"""
    with mock.patch.dict(os.environ, environ):
        assert expected == main._resolve_params(**kwargs)


@pytest.mark.parametrize(
    ["environ", "kwargs"],
    [
        (
            {},
            {
                "logs_location": "https://foobar",
                "logging_level": "ERROR",
                "environment": "test",
                "bypass_firehose": False,
                "send_in_background": False,
            },
        ),
        (
            {
                "GANTRY_API_KEY": "123456789",
                "GANTRY_LOGS_LOCATION": "https://barfoo",
                "GANTRY_LOGGING_LEVEL": "WARNING",
                "GANTRY_ENVIRONMENT": "another",
                "GANTRY_BYPASS_FIREHOSE": "true",
                "GANTRY_SEND_IN_BACKGROUND": "true",
            },
            {
                "api_key": "12345",
                "logs_location": "tcp://foobar",
                "logging_level": "ERROR",
                "environment": "test",
                "bypass_firehose": False,
                "send_in_background": False,
            },
        ),
        (
            {
                "GANTRY_API_KEY": "123456789",
                "GANTRY_LOGS_LOCATION": "https://barfoo",
            },
            {
                "logs_location": "https://foobar",
                "logging_level": "another",
            },
        ),
    ],
)
def test_resolve_params_invalid(environ, kwargs):
    """Check invalid initialization parameters even env vars"""
    with mock.patch.dict(os.environ, environ):
        with pytest.raises((ValueError, TypeError)):
            main._resolve_params(**kwargs)

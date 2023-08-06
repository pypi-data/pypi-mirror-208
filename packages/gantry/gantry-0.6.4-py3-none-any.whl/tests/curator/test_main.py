import mock
import pytest

from gantry.automations.curators import Curator, UniformCurator, globals, main
from gantry.exceptions import ClientNotInitialized


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("get_all_curators", {}),
        ("get_curator", {"name": "test-curator"}),
        ("list_curators", {}),
    ],
)
def test_uninit_client_main(method, params):
    """Test all public methods from curator module
    fail if client is not initialized
    """
    with mock.patch("gantry.automations.curators.globals._CURATOR_CLIENT", None):
        with pytest.raises(ClientNotInitialized):
            getattr(main, method)(**params)


@pytest.mark.parametrize(
    ["curator_type", "params"],
    [
        (Curator, {"name": "test_curator", "application_name": "test-app"}),
        (UniformCurator, {"name": "test_curator", "application_name": "test-app", "limit": 10}),
    ],
)
def test_unint_curator(curator_type, params):
    """Test that curator initialization fails if client is not initialized"""
    with mock.patch("gantry.automations.curators.globals._API_CLIENT", None):
        with pytest.raises(ClientNotInitialized):
            curator_type(**params)


@pytest.mark.parametrize("backend", ["", "/some/file", "tcp://other/protocol"])
def test_global_init_error(backend):
    with mock.patch.dict("os.environ", {"GANTRY_LOGS_LOCATION": backend}):
        with pytest.raises(ValueError):
            main._init()


def test_no_api_key_provided():
    with mock.patch.dict("os.environ", {"GANTRY_API_KEY": ""}):
        with pytest.raises(ValueError):
            main._init(api_key=None)


def test_init():
    """Test init"""
    passed_api_key = "some_key"
    with mock.patch.dict(
        "os.environ",
        {
            "GANTRY_API_KEY": passed_api_key,
            "GANTRY_LOGS_LOCATION": "https://foo/bar",
        },
    ):
        main._init()
        assert globals._CURATOR_CLIENT._api_client._host == "https://foo/bar"
        assert globals._CURATOR_CLIENT._api_client._api_key == passed_api_key
        assert globals._API_CLIENT._host == "https://foo/bar"
        assert globals._API_CLIENT._api_key == passed_api_key


def test_init_default():
    """Test init client with default values"""
    main._init(api_key="ABCD1234")
    assert globals._CURATOR_CLIENT._api_client._host == "https://app.gantry.io"
    assert globals._CURATOR_CLIENT._api_client._api_key == "ABCD1234"
    assert globals._API_CLIENT._host == "https://app.gantry.io"
    assert globals._API_CLIENT._api_key == "ABCD1234"


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("get_all_curators", {}),
        ("get_curator", {"name": "test-curator"}),
        ("list_curators", {}),
    ],
)
def test_curator_methods(method, params):
    """Test all public methods from gantry module or gantry.main module
    resolve in the global _CURATOR_CLIENT methods
    """
    m = mock.Mock()
    with mock.patch("gantry.automations.curators.globals._CURATOR_CLIENT", m):
        getattr(main, method)(**params)
        getattr(m, method).assert_called_once_with(**params)

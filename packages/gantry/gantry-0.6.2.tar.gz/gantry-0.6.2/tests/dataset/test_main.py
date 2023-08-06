import mock
import pytest

from gantry.dataset import main
from gantry.exceptions import ClientNotInitialized


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("create_dataset", {"name": "dataset_name"}),
        ("get_dataset", {"name": "dataset_name"}),
        ("list_dataset_versions", {"name": "dataset_name"}),
        ("list_datasets", {}),
        ("delete_dataset", {"name": "dataset_name"}),
    ],
)
def test_uninit_client_main(method, params):
    """Test all public methods from dataset module
    fail if client is not initialized
    """
    with mock.patch("gantry.dataset.main._DATASET", None):
        with pytest.raises(ClientNotInitialized):
            getattr(main, method)(**params)


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
            "GANTRY_DATASET_WORKING_DIR": "working_dir",
        },
    ):
        main._init()
        assert main._DATASET._api_client._host == "https://foo/bar"
        assert main._DATASET._api_client._api_key == passed_api_key
        assert main._DATASET.working_directory == "working_dir"


def test_init_default():
    """Test init client with default values"""
    main._init(api_key="ABCD1234")
    assert main._DATASET._api_client._host == "https://app.gantry.io"
    assert main._DATASET._api_client._api_key == "ABCD1234"


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("create_dataset", {"name": "dataset_name"}),
        ("get_dataset", {"name": "dataset_name"}),
        ("list_dataset_versions", {"name": "dataset_name"}),
        ("list_datasets", {}),
        ("delete_dataset", {"name": "dataset_name"}),
        ("set_working_directory", {"working_dir": "path"}),
    ],
)
def test_dataset_methods(method, params):
    """Test all public methods from gantry module or gantry.main module
    resolve in the global _DATASET methods
    """
    m = mock.Mock()
    with mock.patch("gantry.dataset.main._DATASET", m):
        getattr(main, method)(**params)
        getattr(m, method).assert_called_once_with(**params)

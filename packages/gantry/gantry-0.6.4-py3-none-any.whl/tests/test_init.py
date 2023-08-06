import mock

from gantry import init


@mock.patch("gantry.logger_init")
@mock.patch("gantry.query_init")
@mock.patch("gantry.alerts_init")
@mock.patch("gantry.curators_init")
@mock.patch("gantry.dataset_init")
def test_init(
    mock_dataset_init, mock_curators_init, mock_alerts_init, mock_query_init, mock_logger_init
):
    init("foobar", "INFO", "dev", False)

    mock_dataset_init.assert_called_once_with("foobar")
    mock_curators_init.assert_called_once_with("foobar")
    mock_alerts_init.assert_called_once_with("foobar")
    mock_query_init.assert_called_once_with("foobar")
    mock_logger_init.assert_called_once_with("foobar", "INFO", "dev", False)

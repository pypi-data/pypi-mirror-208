import mock
import pytest
from click.testing import CliRunner

from gantry.cli.projection import _get_custom_projection_configs, get_logs, update


def test_get_custom_projection_configs():
    empty_projection_dir = "tests/cli/custom-projections/empty_projection_dir/"
    with pytest.raises(ValueError):
        _get_custom_projection_configs(empty_projection_dir)

    valid_projection_dir = "tests/cli/custom-projections/valid_projection_dir/"
    projection = _get_custom_projection_configs(valid_projection_dir)
    assert projection is not None


@mock.patch(
    "gantry.cli.projection._validate_custom_projection_configs",
    return_value=(False, ["error 1", "error 2"]),
)
@mock.patch("gantry.logger.main.get_client")
def test_update_fail_validate_configs(mock_api_client, mock_validate_configs):
    runner = CliRunner()
    cli_args = ["--projection-dir", "tests/cli/custom-projections/invalid_projection_dir/"]
    result = runner.invoke(update, cli_args, env={"GANTRY_API_KEY": "test"})
    assert result.exit_code == 1
    assert "FAILED.\nPlease fix the following issue(s):\n\terror 1\n\terror 2" in result.output


@mock.patch(
    "gantry.cli.projection._validate_custom_projection_configs",
    return_value=(True, []),
)
@mock.patch("gantry.logger.main.get_client")
@mock.patch(
    "gantry.cli.projection._get_s3_destination",
    return_value=(False, {"response": "error", "error": "S3 error"}),
)
def test_update_fail_get_s3_destination(mock_s3, mock_api_client, mock_validate_configs):
    runner = CliRunner()
    cli_args = ["--projection-dir", "tests/cli/custom-projections/valid_projection_dir/"]
    result = runner.invoke(update, cli_args, env={"GANTRY_API_KEY": "test"})
    assert result.exit_code == 1
    assert "Fail to set up upload location: S3 error" in result.output


@mock.patch(
    "gantry.cli.projection._validate_custom_projection_configs",
    return_value=(True, []),
)
@mock.patch("gantry.cli.projection.APIClient.request")
@mock.patch(
    "gantry.cli.projection._get_s3_destination",
    return_value=(True, {"response": "ok", "upload_url": "http://test_url", "s3_key": "test_key"}),
)
@mock.patch("gantry.cli.projection.subprocess")
@mock.patch(
    "gantry.cli.projection._upload_function_zip",
    return_value=(True, ""),
)
@mock.patch(
    "gantry.cli.projection._get_build_logs",
    return_value=("ERROR", "Error getting task logs"),
)
def test_update_success_error_get_logs(
    mock_logs, mock_zip, mock_subprocess, mock_s3, mock_api_client, mock_validate_configs
):
    mock_subprocess.run.return_value.returncode = 0
    mock_api_client.return_value = {"response": "ok", "task_id": "123abc"}

    runner = CliRunner()
    cli_args = ["--projection-dir", "tests/cli/custom-projections/valid_projection_dir/"]
    result = runner.invoke(update, cli_args, env={"GANTRY_API_KEY": "test"})
    assert result.exit_code == 0
    assert "SUCCESS\n--> Task 123abc has been submitted." in result.output


@mock.patch("gantry.cli.projection.APIClient.request")
def test_get_logs_failure(mock_api_client):
    mock_api_client.return_value = {"response": "error", "error": "some error", "logs": []}

    runner = CliRunner()
    cli_args = [
        "--application-name",
        "test-app",
        "--projection-name",
        "test-projection",
        "--start",
        "2022-11-15T17:00:00",
        "--end",
        "2022-11-15T17:01:00",
    ]
    result = runner.invoke(get_logs, cli_args, env={"GANTRY_API_KEY": "test"})
    assert result.exit_code == 1
    assert "Fail to retrieve logs: some error" in result.output


@mock.patch("gantry.cli.projection.APIClient.request")
def test_get_logs_success(mock_api_client):
    mock_api_client.return_value = {
        "response": "ok",
        "logs": [
            {
                "eventId": "123",
                "ingestionTime": 166876447801,
                "logStreamName": "stream",
                "message": "START RequestId: 2c0c8dd2-de6b-4e5c-a7aa-b8ecf53cafb2 Version: 1\n",
                "timestamp": 166876447800,
            },
            {
                "eventId": "456",
                "ingestionTime": 166876447802,
                "logStreamName": "stream",
                "message": "REPORT RequestId: 2c0c8dd2-de6b-4e5c-a7aa-b8ecf53cafb2\tDuration: 0.99 ms\tBilled Duration: 1 ms\tMemory Size: 128 MB\tMax Memory Used: 37 MB\t\n",  # noqa
                "timestamp": 166876447801,
            },
            {
                "eventId": "789",
                "ingestionTime": 166876447803,
                "logStreamName": "stream",
                "message": "END RequestId: 2c0c8dd2-de6b-4e5c-a7aa-b8ecf53cafb2\n",
                "timestamp": 166876447802,
            },
        ],
    }

    runner = CliRunner()
    cli_args = [
        "--application-name",
        "test-app",
        "--projection-name",
        "test-projection",
        "--start",
        "2022-11-15T17:00:00",
        "--end",
        "2022-11-15T17:01:00",
    ]
    result = runner.invoke(get_logs, cli_args, env={"GANTRY_API_KEY": "test"})
    assert result.exit_code == 0

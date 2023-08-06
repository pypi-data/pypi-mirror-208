import uuid

import mock
import responses
from click.testing import CliRunner
from responses import matchers

from gantry.cli.secret import create, delete, list

SECRET_NAME = "test_secret"
UNITTEST_HOST = "http://unittest"
SECRET_INFO = {
    "id": str(uuid.uuid4()),
    "secret_name": SECRET_NAME,  # type: ignore
    "organization_id": str(uuid.uuid4()),
    "secret_type": "AWS",
    "created_at": "2022-12-15T00:05:23",
}


@mock.patch("gantry.cli.secret.APIClient.request")
def test_create_secret_failure(mock_api_client, datadir):
    mock_api_client.return_value = {"response": "error", "error": "some error"}

    runner = CliRunner()
    cli_args = [
        "--name",
        SECRET_NAME,
        "--secret-type",
        "aws",
        "--secret-file",
        str(datadir / "secret.json"),
    ]
    result = runner.invoke(
        create,
        cli_args,
        env={"GANTRY_API_KEY": "test", "GANTRY_LOGS_LOCATION": UNITTEST_HOST},
    )
    assert result.exit_code == 1
    assert f"Fail to create secret {SECRET_NAME}: some error" in result.output


def test_create_secret(datadir):
    runner = CliRunner()
    cli_args = [
        "--name",
        SECRET_NAME,
        "--secret-type",
        "aws",
        "--secret-file",
        str(datadir / "secret.json"),
    ]

    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{UNITTEST_HOST}/api/v1/customer-resources/secrets",
            json={
                "response": "ok",
                "data": SECRET_INFO,
            },
            headers={"Content-Type": "application/json"},
            match=[
                matchers.json_params_matcher(
                    {
                        "secret_name": SECRET_NAME,
                        "secret_type": "AWS",
                        "secret_content": {
                            "access_key": "test-access-key",
                            "secret_key": "test-secret-key",
                        },
                    }
                )
            ],
        )

        result = runner.invoke(
            create,
            cli_args,
            env={"GANTRY_API_KEY": "test", "GANTRY_LOGS_LOCATION": UNITTEST_HOST},
        )
        assert result.exit_code == 0
        assert "--> Secret has been created." in result.output


def test_list_secrets():
    runner = CliRunner()
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/customer-resources/secrets",
            json={"response": "ok", "data": [SECRET_INFO]},
            headers={"Content-Type": "application/json"},
        )

        result = runner.invoke(
            list,
            env={"GANTRY_API_KEY": "test", "GANTRY_LOGS_LOCATION": UNITTEST_HOST},
        )
        assert result.exit_code == 0
        assert f"{SECRET_INFO}" in result.output


def test_delete_secret():
    runner = CliRunner()
    cli_args = ["--secret-id", SECRET_INFO["id"]]

    with responses.RequestsMock() as resp:
        resp.add(
            resp.DELETE,
            f"{UNITTEST_HOST}/api/v1/customer-resources/secrets/{SECRET_INFO['id']}",
            json={
                "response": "ok",
            },
            headers={"Content-Type": "application/json"},
        )

        result = runner.invoke(
            delete,
            cli_args,
            env={"GANTRY_API_KEY": "test", "GANTRY_LOGS_LOCATION": UNITTEST_HOST},
        )
        assert result.exit_code == 0
        assert f"--> Secret {SECRET_INFO['id']} has been deleted." in result.output

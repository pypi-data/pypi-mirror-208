import uuid

import mock
import responses
from click.testing import CliRunner
from responses import matchers

from gantry.cli.bucket import create, list, update_secret

BUCKET_NAME = "test-bucket"
REGION = "us-west-2"
SECRET_NAME = "test_secret"

BUCKET_INFO = {
    "id": str(uuid.uuid4()),
    "bucket_name": BUCKET_NAME,
    "region": REGION,
    "storage_type": "S3",
    "organization_id": str(uuid.uuid4()),
    "secret_id": str(uuid.uuid4()),
    "notification_enabled": False,
    "created_at": "2022-12-15T00:05:23",
}


UNITTEST_HOST = "http://unittest"


@mock.patch("gantry.cli.bucket.APIClient.request")
def test_register_bucket_failure(mock_api_client):
    mock_api_client.return_value = {"response": "error", "error": "some error"}

    runner = CliRunner()
    cli_args = [
        "--name",
        BUCKET_NAME,
        "--region",
        REGION,
        "--storage-type",
        "s3",
        "--secret",
        SECRET_NAME,
    ]
    result = runner.invoke(create, cli_args, env={"GANTRY_API_KEY": "test"})
    assert result.exit_code == 1
    assert f"Fail to register bucket {BUCKET_NAME}: some error" in result.output


def test_register_bucket():
    runner = CliRunner()
    cli_args = [
        "--name",
        BUCKET_NAME,
        "--region",
        REGION,
        "--storage-type",
        "s3",
        "--secret",
        SECRET_NAME,
    ]

    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{UNITTEST_HOST}/api/v1/customer-resources/buckets",
            json={
                "response": "ok",
                "data": BUCKET_INFO,
            },
            headers={"Content-Type": "application/json"},
            match=[
                matchers.json_params_matcher(
                    {
                        "bucket_name": BUCKET_NAME,
                        "region": REGION,
                        "storage_type": "S3",
                        "secret_name": SECRET_NAME,
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
        assert "--> Bucket test-bucket has been registered." in result.output


def test_list_buckets():
    runner = CliRunner()
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/customer-resources/buckets",
            json={
                "response": "ok",
                "data": [BUCKET_INFO],
            },
            headers={"Content-Type": "application/json"},
        )
        result = runner.invoke(
            list,
            env={"GANTRY_API_KEY": "test", "GANTRY_LOGS_LOCATION": UNITTEST_HOST},
        )
        assert result.exit_code == 0
        assert f"{BUCKET_INFO}" in result.output


def test_update_bucket():
    secret_id = str(uuid.uuid4())
    runner = CliRunner()
    cli_args = [
        "--bucket",
        "test-bucket",
        "--storage-type",
        "s3",
        "--secret-id",
        secret_id,
    ]

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/customer-resources/buckets/test-bucket?storage_type=S3",
            json={
                "response": "ok",
                "data": BUCKET_INFO,
            },
            headers={"Content-Type": "application/json"},
        )

        resp.add(
            resp.PATCH,
            f"{UNITTEST_HOST}/api/v1/customer-resources/buckets/{BUCKET_INFO['id']}",
            json={
                "response": "ok",
            },
            headers={"Content-Type": "application/json"},
            match=[
                matchers.json_params_matcher(
                    {
                        "secret_id": secret_id,
                    }
                )
            ],
        )

        result = runner.invoke(
            update_secret,
            cli_args,
            env={"GANTRY_API_KEY": "test", "GANTRY_LOGS_LOCATION": UNITTEST_HOST},
        )
        assert result.exit_code == 0
        assert f"--> Bucket test-bucket has been updated with key {secret_id}." in result.output

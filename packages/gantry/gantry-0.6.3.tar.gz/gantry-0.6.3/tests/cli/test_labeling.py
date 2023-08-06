import uuid

import boto3
import click.exceptions
import mock
import pytest
import responses
from botocore.exceptions import ClientError
from click.testing import CliRunner
from moto import mock_s3
from responses import matchers

from gantry.cli.labeling import (
    _validate_source,
    create,
    dashboard_export,
    dataset_export,
    list,
)
from gantry.exceptions import GantryRequestException

BUCKET_NAME = "test-bucket"
REGION = "us-west-2"
PROJECT_NAME = "test-project"
UNITTEST_HOST = "http://unittest"

LS_HOST = "http://test-ls-host"
LS_TOKEN = "test-ls-token"
LS_PROJ_ID = "fake-project-id"

AWS_ACCESS_KEY_ID = "test_access_key"
AWS_SECRET_ACCESS_KEY = "test_secret_access_key"
AWS_SESSION_TOKEN = "test_session_token"

TEST_ENV = {
    "GANTRY_API_KEY": "test",
    "GANTRY_LOGS_LOCATION": UNITTEST_HOST,
    "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
    "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
    "AWS_SESSION_TOKEN": AWS_SESSION_TOKEN,
    "AWS_DEFAULT_REGION": REGION,
}

unpatched_uuid = uuid.uuid4


def s3_setup(bucket_name=BUCKET_NAME, region=REGION):
    s3_client = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
    )
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )

    return s3_client


def setup_resp_with_backoff(resp: responses.RequestsMock, *args, **kwargs):
    id = unpatched_uuid()
    final_json = kwargs.pop("json", {})
    final_json["response"] = "ok"
    final_json["status"] = "SUCCESS"

    resp.add(  # type: ignore
        *args,
        **kwargs,
        status=202,
        headers={"Location": f"test-location-{id}"},
    )
    resp.add(
        resp.GET,
        f"{UNITTEST_HOST}/test-location-{id}",
        json=final_json,
    )


def setup_resp_for_gantry_pings(resp: responses.RequestsMock):
    resp.add(resp.GET, f"{UNITTEST_HOST}/api/ping", status=200)
    resp.add(resp.GET, f"{UNITTEST_HOST}/api/v1/auth-ping", status=200)


def setup_resp_for_labelstudio(resp: responses.RequestsMock, s3_prefix: str):
    ls_params = {
        "bucket": BUCKET_NAME,
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "aws_session_token": AWS_SESSION_TOKEN,
        "region_name": None,
        "s3_endpoint": None,
        "title": "Gantry S3 connection",
        "description": "Integration made by Gantry",
        "project": LS_PROJ_ID,
    }

    # create the project in label studio
    resp.add(
        resp.POST,
        f"{LS_HOST}/api/projects",
        status=201,
        json={"id": LS_PROJ_ID},
    )
    # register import s3
    resp.add(
        resp.POST,
        f"{LS_HOST}/api/storages/s3",
        match=[
            matchers.json_params_matcher(
                {
                    **ls_params,
                    "regex_filter": None,
                    "use_blob_urls": False,
                    "prefix": f"{s3_prefix}/source_data",
                    "presign": True,
                    "presign_ttl": 1,
                },
            )
        ],
        json={"id": "fake-import-id"},
    )
    # register export s3
    resp.add(
        resp.POST,
        f"{LS_HOST}/api/storages/export/s3",
        match=[
            matchers.json_params_matcher(
                {
                    **ls_params,
                    "can_delete_objects": False,
                    "prefix": f"{s3_prefix}/labeled_data",
                },
            )
        ],
        json={"id": "fake-export-id"},
    )
    # labelstudio import sync
    resp.add(
        resp.POST,
        f"{LS_HOST}/api/storages/s3/fake-import-id/sync",
        json={"response": "ok"},
    )


@mock.patch("uuid.uuid4", return_value="01234")
@mock.patch("gantry.cli.labeling.LabelStudioManager.check_status")
@mock.patch("gantry.cli.labeling._validate_dataset")
@mock_s3
def test_create_project_from_dataset_version(
    mock_validate_dataset, mock_ls_status, mock_uuid, datadir
):
    s3_client = s3_setup()
    runner = CliRunner()

    source = "gantry://datasets/fake-dataset/versions/fake-version"
    s3_prefix = f"{PROJECT_NAME}__gantry_{mock_uuid.return_value}"

    cli_args = [
        "--source",
        source,
        "--name",
        PROJECT_NAME,
        "--bucket",
        BUCKET_NAME,
        "--ls-token",
        LS_TOKEN,
        "--ls-host",
        LS_HOST,
        "--project-interface",
        str(datadir / "project_interface.xml"),
    ]

    with responses.RequestsMock() as resp:
        setup_resp_for_gantry_pings(resp)
        setup_resp_for_labelstudio(resp, s3_prefix)
        # make sure the bucket exists
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/customer-resources/buckets/{BUCKET_NAME}?storage_type=S3",
            json={},
        )
        # make sure the project doesn't exist
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/labeling/projects/{PROJECT_NAME}",
            status=404,
        )
        # create the project
        resp.add(
            resp.POST,
            f"{UNITTEST_HOST}/api/v1/labeling/projects",
            json={
                "data": {
                    "name": PROJECT_NAME,
                    "id": LS_PROJ_ID,
                },
                "response": "ok",
            },
            match=[
                matchers.json_params_matcher(
                    {
                        "name": PROJECT_NAME,
                        "bucket": BUCKET_NAME,
                        "s3_prefix": s3_prefix,
                        "source": source,
                        "ls_host": LS_HOST,
                        "import_storage_id": "fake-import-id",
                        "export_storage_id": "fake-export-id",
                    }
                )
            ],
        )
        # start the project
        setup_resp_with_backoff(
            resp,
            resp.PATCH,
            f"{UNITTEST_HOST}/api/v1/labeling/projects/{PROJECT_NAME}",
            match=[matchers.json_params_matcher({"new-status": "imported"})],
        )

        result = runner.invoke(create, args=cli_args, env=TEST_ENV)

        assert result.exit_code == 0

        assert "New Label Studio project created" in result.output
        assert "Registered labeling project in Gantry" in result.output
        assert f"Ready to start labeling: {LS_HOST}/projects" in result.output

        # make sure the folders were created
        objects = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=s3_prefix)["Contents"]
        keys = [f["Key"] for f in objects]

        assert f"{s3_prefix}/source_data/" in keys
        assert f"{s3_prefix}/labeled_data/" in keys


@mock.patch("gantry.cli.labeling._validate_dataset")
@mock_s3
def test_create_project_duplicate_name(mock_validate_dataset, datadir):
    runner = CliRunner()
    source = "gantry://datasets/fake-dataset/versions/fake-version"

    cli_args = [
        "--source",
        source,
        "--name",
        PROJECT_NAME,
        "--bucket",
        BUCKET_NAME,
        "--ls-token",
        LS_TOKEN,
        "--ls-host",
        LS_HOST,
        "--project-interface",
        str(datadir / "project_interface.xml"),
    ]

    with responses.RequestsMock() as resp:
        setup_resp_for_gantry_pings(resp)
        # make sure the bucket exists
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/customer-resources/buckets/{BUCKET_NAME}?storage_type=S3",
            json={},
        )
        # make sure the project doesn't exist (but this time it does)
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/labeling/projects/{PROJECT_NAME}",
            status=200,
        )

        result = runner.invoke(create, args=cli_args, env=TEST_ENV)

        assert result.exit_code == 1

        assert "New Label Studio project created" not in result.output
        assert result.exc_info[0] == ValueError
        assert "Name must be unique" in result.exc_info[1].args[0]


@mock.patch("gantry.cli.labeling._validate_dataset")
@mock_s3
def test_create_project_no_bucket(mock_validate_dataset, datadir):
    runner = CliRunner()
    source = "gantry://datasets/fake-dataset/versions/fake-version"

    cli_args = [
        "--source",
        source,
        "--name",
        PROJECT_NAME,
        "--bucket",
        BUCKET_NAME,
        "--ls-token",
        LS_TOKEN,
        "--ls-host",
        LS_HOST,
        "--project-interface",
        str(datadir / "project_interface.xml"),
    ]

    with responses.RequestsMock() as resp:
        setup_resp_for_gantry_pings(resp)
        # make sure the bucket exists (but it doesn't)
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/customer-resources/buckets/{BUCKET_NAME}?storage_type=S3",
            status=404,
        )

        result = runner.invoke(create, args=cli_args, env=TEST_ENV)

        assert result.exit_code == 1

        assert "New Label Studio project created" not in result.output
        assert result.exc_info[0] == RuntimeError
        assert (
            "Labeling requires customers to register bucket with their secrets"
            in result.exc_info[1].args[0]
        )


@pytest.mark.parametrize(
    "created_new_dataset",
    [True, False],
)
def test_export_project_to_dataset(created_new_dataset):
    runner = CliRunner()

    dataset_name = "fake-dataset"
    dataset_id = "fake-dataset-id"
    dataset_json = {
        "name": dataset_name,
        "id": dataset_id,
        "bucket_name": BUCKET_NAME,
        "aws_region": REGION,
        "organization_id": "fake-org-id",
        "s3_prefix": "fake-prefix",
        "disabled": False,
    }

    cli_args = [
        "--name",
        PROJECT_NAME,
        "--destination",
        dataset_name,
        "--ls-token",
        LS_TOKEN,
    ]

    with responses.RequestsMock() as resp:
        setup_resp_for_gantry_pings(resp)
        # get project
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/labeling/projects/{PROJECT_NAME}",
            json={
                "data": {"export_storage_id": "fake-export-id", "ls_host": LS_HOST},
                "response": "ok",
            },
        )
        # labelstudio export sync
        resp.add(
            resp.POST,
            f"{LS_HOST}/api/storages/export/s3/fake-export-id/sync",
            json={"response": "ok"},
        )
        # setup dataset stuff
        if created_new_dataset:
            resp.add(
                resp.GET,
                f"{UNITTEST_HOST}/api/v1/datasets/{dataset_name}",
                status=404,
            )
            resp.add(
                resp.POST,
                f"{UNITTEST_HOST}/api/v1/datasets",
                json={"data": dataset_json, "response": "ok"},
                match=[matchers.json_params_matcher({"name": dataset_name})],
            )
        else:
            resp.add(
                resp.GET,
                f"{UNITTEST_HOST}/api/v1/datasets/{dataset_name}",
                json={"data": dataset_json, "response": "ok"},
            )
        # export labels to dataset
        setup_resp_with_backoff(
            resp,
            resp.POST,
            f"{UNITTEST_HOST}/api/v1/datasets/{dataset_id}/labeled-data",
            json={"id": "fake-version-id", "response": "ok"},
            match=[matchers.json_params_matcher({"labeling-project-name": PROJECT_NAME})],
        )

        result = runner.invoke(dataset_export, args=cli_args, env=TEST_ENV)

        assert result.exit_code == 0

        assert "Synced labeled data to S3 bucket" in result.output
        if created_new_dataset:
            assert "Created new dataset" in result.output
        else:
            assert "Created new dataset" not in result.output
        assert "Labeled data has been successfully exported: gantry://datasets" in result.output


def test_export_project_to_dashboard():
    runner = CliRunner()

    app_name = "fake-application"

    cli_args = [
        "--name",
        PROJECT_NAME,
        "--destination",
        app_name,
        "--ls-token",
        LS_TOKEN,
    ]

    with responses.RequestsMock() as resp:
        setup_resp_for_gantry_pings(resp)
        # get project
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/labeling/projects/{PROJECT_NAME}",
            json={
                "data": {"export_storage_id": "fake-export-id", "ls_host": LS_HOST},
                "response": "ok",
            },
        )
        # labelstudio export sync
        resp.add(
            resp.POST,
            f"{LS_HOST}/api/storages/export/s3/fake-export-id/sync",
            json={"response": "ok"},
        )
        # get application
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/models/{app_name}",
            json={"data": {"versions": []}, "response": "ok"},  # just need to return something
        )
        # export labels to dataset
        setup_resp_with_backoff(
            resp,
            resp.POST,
            f"{UNITTEST_HOST}/api/v1/ingest/labeling",
            json={"id": "fake-version-id", "response": "ok"},
            match=[
                matchers.json_params_matcher(
                    {"labeling_project": PROJECT_NAME, "application": app_name}
                )
            ],
        )

        result = runner.invoke(dashboard_export, args=cli_args, env=TEST_ENV)

        assert result.exit_code == 0

        assert "Synced labeled data to S3 bucket" in result.output
        assert "Labeled data has been successfully exported:" in result.output
        assert app_name in result.output


@pytest.mark.parametrize(
    "export",
    [dataset_export, dashboard_export],
)
def test_export_project_no_project(export):
    runner = CliRunner()

    cli_args = [
        "--name",
        PROJECT_NAME,
        "--destination",
        "fake-dataset",
        "--ls-token",
        LS_TOKEN,
    ]

    with responses.RequestsMock() as resp:
        setup_resp_for_gantry_pings(resp)
        # get project (there is no project)
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/labeling/projects/{PROJECT_NAME}",
            status=404,
        )

        result = runner.invoke(export, args=cli_args, env=TEST_ENV)

        assert result.exit_code == 1

        assert result.exc_info[0] == GantryRequestException
        assert "A resource was not found" in result.exc_info[1].args[0]


@pytest.mark.parametrize("num_projects", [0, 1, 2])
def test_list_projects(num_projects):
    runner = CliRunner()

    cli_args = []

    projects = [
        {
            "id": "fake-proj-id",
            "org_id": "fake-org-id",
            "name": "fake-proj-name",
            "source": "fake-source",
            "bucket": "fake-bucket",
            "s3_prefix": "fake-folder",
            "ls_host": "fake-ls-host",
            "created_at": "fake-created-at",
            "import_storage_id": "fake-import-id",
            "export_storage_id": "fake-export-id",
            "status": "fake-status",
        }
    ] * num_projects

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{UNITTEST_HOST}/api/v1/labeling/projects",
            json={"data": projects, "response": "ok"},
        )

        result = runner.invoke(list, args=cli_args, env=TEST_ENV)

        assert result.exit_code == 0

        if num_projects == 0:
            assert "No labeling projects found" in result.output
        else:
            assert len(result.output.split("\n")) == num_projects + 3
            assert "fake-proj-name" in result.output


def test_validate_source_dataset():
    source_urn = "gantry://datasets/fake-dataset/versions/fake-version"
    ctx = mock.Mock()
    ctx.params = {"api_key": "fake-api-key"}
    HOST = "https://app.gantry.io"

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/fake-dataset",
            json={
                "response": "ok",
                "data": {
                    "name": "fake-dataset",
                    "id": "fake-dataset-id",
                    "bucket_name": BUCKET_NAME,
                    "aws_region": REGION,
                    "organization_id": "fake-org-id",
                    "s3_prefix": "fake-prefix",
                    "disabled": False,
                },
            },
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/fake-dataset-id/commits",
            json={
                "response": "ok",
                "data": [
                    {
                        "id": "fake-version",
                        "message": "fake-message",
                        "created_at": "fake-created-at",
                        "created_by": "fake-created-by",
                        "is_latest_commit": True,
                    }
                ],
            },
        )

        assert _validate_source(ctx, None, source_urn) == source_urn


@pytest.mark.parametrize(
    "source_urn",
    [
        "gantry://datasets/fake-dataset/versions/doesnt-exist-version",
        "gantry://datasets/doesnt-exist-dataset/versions/fake-version/",
    ],
)
def test_validate_source_dataset_invalid(source_urn):
    ctx = mock.Mock()
    ctx.params = {"api_key": "fake-api-key"}
    HOST = "https://app.gantry.io"

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/doesnt-exist-dataset",
            status=404,
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/fake-dataset",
            json={
                "response": "ok",
                "data": {
                    "name": "fake-dataset",
                    "id": "fake-dataset-id",
                    "bucket_name": BUCKET_NAME,
                    "aws_region": REGION,
                    "organization_id": "fake-org-id",
                    "s3_prefix": "fake-prefix",
                    "disabled": False,
                },
            },
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/fake-dataset-id/commits",
            json={
                "response": "ok",
                "data": [
                    {
                        "id": "fake-version",
                        "message": "fake-message",
                        "created_at": "fake-created-at",
                        "created_by": "fake-created-by",
                        "is_latest_commit": True,
                    }
                ],
            },
        )

        with pytest.raises(click.exceptions.BadParameter):
            _validate_source(ctx, None, source_urn)


def test_validate_source_batch():
    source_urn = "gantry://apps/fake-app/batches/fake-batch-id"
    ctx = mock.Mock()
    ctx.params = {"api_key": "fake-api-key"}
    HOST = "https://app.gantry.io"

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/models/fake-app/schemas",
            json={
                "response": "ok",
                "data": {"version": "0", "id": "test-id"},
            },
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/test-id/batches",
            json={
                "response": "ok",
                "data": {"batches": [{"id": "fake-batch-id"}], "metadata": {"total_count": 1}},
            },
        )

        assert _validate_source(ctx, None, source_urn) == source_urn


@pytest.mark.parametrize(
    "source_urn",
    [
        "gantry://apps/fake-app/batches/doesnt-exist",
        "gantry://apps/doesnt-exist/batches/fake-batch-id",
    ],
)
def test_validate_source_batch_invalid(source_urn):
    ctx = mock.Mock()
    ctx.params = {"api_key": "fake-api-key"}
    HOST = "https://app.gantry.io"

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/models/doesnt-exist/schemas",
            status=404,
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/models/fake-app/schemas",
            json={
                "response": "ok",
                "data": {"version": "0", "id": "test-id"},
            },
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/test-id/batches",
            json={
                "response": "ok",
                "data": {"batches": [{"id": "fake-batch-id"}], "metadata": {"total_count": 1}},
            },
        )

        with pytest.raises(click.exceptions.BadParameter):
            _validate_source(ctx, None, source_urn)

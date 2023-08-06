import re
import uuid
from typing import Optional, Tuple
from urllib.parse import urlparse

import backoff
import boto3
import botocore
import click
import requests
from boto3 import Session
from click_aliases import ClickAliasedGroup
from halo import Halo
from label_studio_sdk import Client as LSClient  # type: ignore
from label_studio_sdk import Project  # type: ignore
from requests.exceptions import HTTPError
from tabulate import tabulate

import gantry
from gantry import dataset as gdataset
from gantry import query as gquery
from gantry.api_client import APIClient
from gantry.exceptions import DatasetNotFoundError, GantryRequestException


class LabelStudioManager:
    def __init__(self, ls_cli: LSClient) -> None:
        self.ls_cli = ls_cli

    def check_status(self):
        status = self.ls_cli.check_connection().get("status")
        if status != "UP":
            raise RuntimeError(f"LS instance not accessible: {status}")

        try:
            self.ls_cli.get_projects()
        except HTTPError as err:
            if err.response.status_code == 401:
                raise RuntimeError("Invalid Label Studio user token")
            else:
                raise RuntimeError(f"Cannot access LS: {err.response.text}")

    def create_project(self, name: str, project_interface: str):
        with open(project_interface, "r") as f:
            return self.ls_cli.start_project(
                title=name, description="Gantry generated project", label_config=f.read()
            )


def _register_import_storage(
    project: Project,
    bucket: str,
    source_data_folder: str,
    s3_access_key: str,
    s3_secret_key: str,
    s3_token: str,
) -> str:
    # https://labelstud.io/sdk/project.html#label_studio_sdk.project.Project.connect_s3_import_storage
    s3_storage = project.connect_s3_import_storage(
        bucket=bucket,
        prefix=source_data_folder,
        use_blob_urls=False,
        title="Gantry S3 connection",
        description="Integration made by Gantry",
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        aws_session_token=s3_token,
    )
    return s3_storage["id"]


def _register_export_storage(
    project: Project,
    bucket: str,
    source_data_folder: str,
    s3_access_key: str,
    s3_secret_key: str,
    s3_token,
) -> str:
    # https://labelstud.io/sdk/project.html#label_studio_sdk.project.Project.connect_s3_export_storage
    s3_storage = project.connect_s3_export_storage(
        bucket=bucket,
        prefix=source_data_folder,
        title="Gantry S3 connection",
        description="Integration made by Gantry",
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        aws_session_token=s3_token,
    )
    return s3_storage["id"]


def _sync_import_storage(storage_id: str, ls_host: str, ls_token: str) -> None:
    resp = requests.post(
        f"{ls_host}/api/storages/s3/{storage_id}/sync",
        headers={"Authorization": f"Token {ls_token}"},
    )
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"Cannot sync storage {storage_id}: {exc}. Are AWS creds correct?")


def _sync_export_storage(storage_id: str, ls_host: str, ls_token: str) -> None:
    resp = requests.post(
        f"{ls_host}/api/storages/export/s3/{storage_id}/sync",
        headers={"Authorization": f"Token {ls_token}"},
    )
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Cannot sync storage {storage_id}: {e}")


def _generate_s3_prefix(name) -> str:
    id_ = uuid.uuid4()
    return f"{name}__gantry_{str(id_)[:5]}"


def _create_folder_structure(
    s3_cli: "botocore.client.S3", bucket: str, s3_prefix: str
) -> Tuple[str, str]:
    # LS expects folder names to be without trailing slash
    folders = (f"{s3_prefix}/source_data", f"{s3_prefix}/labeled_data")

    for folder in folders:
        s3_cli.put_object(Bucket=bucket, Key=f"{folder}/")  # s3 does need the trailing slash

    return folders


@click.group(cls=ClickAliasedGroup)
def labeling():
    """
    Labeling cli
    """


CREATE_SOURCE_HELP = """
Source needs to be a URN. Currently only datasets are valid URNs:
'gantry://datasets/<dataset_name>/versions/<version_id>'.
"""


def _get_aws_creds(api_client: APIClient, bucket_name: str) -> Tuple[str, str, str, str]:
    session = Session()
    credentials = session.get_credentials()
    # Credentials are refreshable, so accessing your access key / secret key
    # separately can lead to a race condition. Use this to get an actual matched
    # set.
    current_credentials = credentials.get_frozen_credentials()

    return (
        current_credentials.access_key,
        current_credentials.secret_key,
        current_credentials.token,
        session.region_name,
    )


DATASET_URI_REGEX = re.compile(
    r"gantry://datasets/(?P<dataset_name>[a-zA-Z0-9_-]+)/"
    r"versions/(?P<dataset_version>[a-zA-Z0-9_-]+)"
)
BATCH_ID_URI_REGEX = re.compile(
    r"gantry://apps/(?P<app_name>[a-zA-Z0-9._-]+)/batches/(?P<batch_id>[a-zA-Z0-9_-]+)"
)


def _validate_dataset(name: str, version: str) -> None:
    try:
        versions = gdataset.list_dataset_versions(name)
        if version not in {version["version_id"] for version in versions}:
            raise click.BadParameter(f"Version '{version}' doesn't exist for dataset '{name}'")
    except DatasetNotFoundError:
        raise click.BadParameter(f"Dataset '{name}' doesn't exist")


def _validate_batch_id(app: str, batch_id: str) -> None:
    try:
        batches = gquery.list_application_batches(application=app)
        if batch_id not in (b["id"] for b in batches):
            raise click.BadParameter(f"Batch '{batch_id}' doesn't exist for app '{app}'")
    except GantryRequestException:
        raise click.BadParameter(f"App '{app}' doesn't exist")


def _validate_source(ctx, param, value):
    gantry.init(api_key=ctx.params["api_key"])

    dataset_regex_match = DATASET_URI_REGEX.match(value)
    batch_id_regex_match = BATCH_ID_URI_REGEX.match(value)
    if dataset_regex_match:
        dataset_name, version = (
            dataset_regex_match.groupdict()["dataset_name"],
            dataset_regex_match.groupdict()["dataset_version"],
        )
        _validate_dataset(dataset_name, version)
    elif batch_id_regex_match:
        app, batch_id = (
            batch_id_regex_match.groupdict()["app_name"],
            batch_id_regex_match.groupdict()["batch_id"],
        )
        _validate_batch_id(app, batch_id)
    else:
        raise click.BadParameter(
            f"'{value}' is not a valid source. Only "
            "'gantry://datasets/<dataset_name>/versions/<dataset_version_id>'"
            " and 'gantry://apps/<app_name>/batches/<batch_id>' URIs supported currently."
        )

    return value


def _validate_protocol(ctx, param, value):
    parsed_url = urlparse(value)
    if parsed_url.scheme == "http":
        click.secho(
            "--> WARNING: Label Studio instance over plain HTTP. Connection is not safe.",
            fg="yellow",
        )
    return value


@labeling.command(
    aliases=["create"],
    help="Create a labeling job.",
)
@click.option(
    "-s",
    "--source",
    type=click.STRING,
    required=True,
    help=CREATE_SOURCE_HELP,
    callback=_validate_source,
)
@click.option(
    "-n", "--name", type=click.STRING, required=True, help="Name of the Label studio project"
)
@click.option(
    "--bucket",
    type=click.STRING,
    required=True,
    help="S3 bucket name Gantry will use as LS backend storage",
)
@click.option("--ls-token", type=click.STRING, required=True, help="Label studio user token")
@click.option(
    "--ls-host",
    type=click.STRING,
    required=True,
    help="Label studio host",
    callback=_validate_protocol,
)
@click.option(
    "--project-interface",
    type=click.STRING,
    required=True,
    help="Path to Label studio labeling spec",
)
@click.option(
    "--api-key",
    type=click.STRING,
    required=False,
    help="Gantry api key. If not provided, GANTRY_API_KEY env var will be used",
    is_eager=True,  # need this to be eager to be accessible in source validation.
)
def create(
    source: str,
    name: str,
    bucket: str,
    ls_token: str,
    ls_host: str,
    project_interface: str,
    api_key: Optional[str],
):
    cli = LSClient(url=ls_host, api_key=ls_token)
    cli = LabelStudioManager(cli)

    api_client: APIClient = gantry.get_client().log_store._api_client
    try:
        _ = api_client.request(
            "GET",
            f"/api/v1/customer-resources/buckets/{bucket}?storage_type=S3",
            raise_for_status=True,
        )
    except GantryRequestException:
        raise RuntimeError(
            # TODO -> insert docs
            f"Bucket '{bucket}' was not registered in Gantry. Labeling "
            "requires customers to register bucket with their secrets prior "
            "to creating a labeling project. Please refer to docs on how "
            "to register a bucket."
        )

    try:
        _ = api_client.request("GET", f"/api/v1/labeling/projects/{name}", raise_for_status=True)
        raise ValueError(
            f"Name must be unique. A labeling project with name '{name}' already exists"
        )
    except GantryRequestException as exc:
        if exc.status_code != 404:
            raise

    cli.check_status()
    click.secho("--> Label Studio instance accessible.", fg="green")

    project = cli.create_project(name, project_interface)
    click.secho(f"--> New Label Studio project created [id={project.id}].", fg="green")

    aws_access_key_id, aws_secret_access_key, aws_session_token, region = _get_aws_creds(
        api_client, bucket
    )
    s3_cli = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region,
    )

    s3_prefix = _generate_s3_prefix(name)
    source_data_folder, labeled_data_folder = _create_folder_structure(s3_cli, bucket, s3_prefix)
    click.secho("--> S3 bucket folder creation done.", fg="green")

    import_storage_id = _register_import_storage(
        project,
        bucket,
        source_data_folder,
        aws_access_key_id,
        aws_secret_access_key,
        aws_session_token,
    )
    export_storage_id = _register_export_storage(
        project,
        bucket,
        labeled_data_folder,
        aws_access_key_id,
        aws_secret_access_key,
        aws_session_token,
    )
    click.secho(
        "--> S3 source integrated with Label Studio project.",
        fg="green",
    )

    resp = api_client.request(
        "POST",
        "/api/v1/labeling/projects",
        raise_for_status=True,
        json={
            "name": name,
            "bucket": bucket,
            "s3_prefix": s3_prefix,
            "source": source,
            "ls_host": ls_host,
            "import_storage_id": import_storage_id,
            "export_storage_id": export_storage_id,
        },
    )
    data = resp["data"]
    click.secho(
        f"--> Registered labeling project in Gantry [id={data['id']}]",
        fg="green",
    )

    with Halo(text="Pushing data into LabelStudio (this could take a while)...", spinner="dots"):
        # https://farazdagi.com/posts/2014-10-16-rest-long-running-jobs/
        resp = api_client.request(
            "PATCH",
            f"/api/v1/labeling/projects/{name}",
            raise_for_status=True,
            json={"new-status": "imported"},
            raw_response=True,
        )
        status_url = resp.headers["Location"]
        status = wait_until_success(api_client, status_url)
        if status == "FAILURE":
            click.secho(
                "--> Pushing data failed. Contact Gantry for further instruction "
                f"[project={name}]",
                fg="red",
            )
            return

        _sync_import_storage(import_storage_id, ls_host, ls_token)

    click.secho(
        (
            "--> Synced source data. Ready to start labeling: "
            f"{ls_host.rstrip('/')}/projects/{project.id}"
        ),
        fg="green",
    )


@backoff.on_predicate(backoff.constant, lambda x: x not in ["SUCCESS", "FAILURE"], interval=1)
def wait_until_success(api_client, status_url):
    resp = api_client.request("GET", status_url)
    return resp["status"]


@labeling.command(
    aliases=["list"],
    help="List all labeling job.",
)
@click.option(
    "--api-key",
    type=click.STRING,
    required=False,
    help="Gantry api key. If not provided, GANTRY_API_KEY env var will be used",
)
def list(api_key):
    gantry.init(api_key=api_key)
    api_client: APIClient = gantry.get_client().log_store._api_client
    resp = api_client.request("GET", "/api/v1/labeling/projects", raise_for_status=True)
    data = resp["data"]
    filtered_data = [
        {
            k: v
            for k, v in item.items()
            if k not in ["org_id", "id", "ls_host", "import_storage_id", "export_storage_id"]
        }
        for item in data
    ]
    if filtered_data:
        print(tabulate(filtered_data, headers="keys"))
    else:
        click.secho("--> No labeling projects found.", fg="green")


@labeling.command(
    aliases=["export"],
    help="Export labeled data from Label Studio into a Gantry dataset",
)
@click.option(
    "-n", "--name", type=click.STRING, required=True, help="Name of the Label studio project"
)
@click.option(
    "-d",
    "--destination",
    type=click.STRING,
    required=True,
    help="Name of the destination dataset. If dataset does not exist, Gantry will create it.",
)
@click.option("--ls-token", type=click.STRING, required=True, help="Label studio user token")
@click.option(
    "--api-key",
    type=click.STRING,
    required=False,
    help="Gantry api key. If not provided, GANTRY_API_KEY env var will be used",
)
def dataset_export(api_key: str, destination: str, ls_token: str, name: str) -> None:
    gantry.init(api_key=api_key)
    api_client: APIClient = gantry.get_client().log_store._api_client
    resp = api_client.request("GET", f"/api/v1/labeling/projects/{name}", raise_for_status=True)
    data = resp["data"]
    _sync_export_storage(data["export_storage_id"], data["ls_host"], ls_token)
    click.secho("--> Synced labeled data to S3 bucket", fg="green")

    new_dataset = False

    with Halo(text="Exporting labeled data...", spinner="dots"):
        try:
            dataset = gdataset.get_dataset(destination)
        except DatasetNotFoundError:
            dataset = gdataset.create_dataset(destination)
            new_dataset = True

        # https://farazdagi.com/posts/2014-10-16-rest-long-running-jobs/
        resp = api_client.request(
            "POST",
            f"/api/v1/datasets/{dataset._dataset_id}/labeled-data",
            json={
                "labeling-project-name": name,
            },
            raw_response=True,
            raise_for_status=True,
        )
        status_url = resp.headers["Location"]
        status = wait_until_success(api_client, status_url)
        if status == "FAILURE":
            click.secho(
                "--> Exporting data failed. Contact Gantry for further instruction "
                f"[project={name}]",
                fg="red",
            )
            return

        resp = api_client.request("GET", status_url)
        dataset_uri = f"gantry://datasets/{destination}/versions/{resp['id']}"

    if new_dataset:
        click.secho(f"--> Created new dataset '{destination}'", fg="yellow")
    click.secho(
        f"--> Labeled data has been successfully exported: {dataset_uri}",
        fg="green",
    )


@labeling.command(
    aliases=["export"],
    help="Export labeled data from Label Studio into Gantry dashboard.",
)
@click.option(
    "-n", "--name", type=click.STRING, required=True, help="Name of the Label studio project"
)
@click.option(
    "-d",
    "--destination",
    type=click.STRING,
    required=True,
    help="Name of the gantry application. Application needs to exist and the source data "
    "needs to have been extracted from this same application",
)
@click.option("--ls-token", type=click.STRING, required=True, help="Label studio user token")
@click.option(
    "--api-key",
    type=click.STRING,
    required=False,
    help="Gantry api key. If not provided, GANTRY_API_KEY environment variable will be used",
)
def dashboard_export(api_key: str, destination: str, ls_token: str, name: str) -> None:
    gantry.init(api_key=api_key)
    api_client: APIClient = gantry.get_client().log_store._api_client
    resp = api_client.request("GET", f"/api/v1/labeling/projects/{name}", raise_for_status=True)
    data = resp["data"]
    try:
        _ = gquery.list_application_versions(destination)
    except GantryRequestException:
        raise ValueError(
            f"Application '{destination}' was not found. Exporting to dashboard only "
            "works if application exists and source data from the labeling project "
            "was extracted from this application."
        )

    _sync_export_storage(data["export_storage_id"], data["ls_host"], ls_token)
    click.secho("--> Synced labeled data to S3 bucket", fg="green")

    with Halo(text="Exporting labeled data...", spinner="dots"):
        # https://farazdagi.com/posts/2014-10-16-rest-long-running-jobs/
        resp = api_client.request(
            "POST",
            "/api/v1/ingest/labeling",
            json={
                "application": destination,
                "labeling_project": name,
            },
            raw_response=True,
            raise_for_status=True,
        )
        status_url = resp.headers["Location"]
        status = wait_until_success(api_client, status_url)
        if status == "FAILURE":
            click.secho(
                "--> Exporting data failed. Contact Gantry for further instruction "
                f"[project={name}]",
                fg="red",
            )
            return
        resp = api_client.request("GET", status_url)
        dashboard_uri = f"https://app.gantry.io/applications/{destination}/data"

    click.secho(
        f"--> Labeled data has been successfully exported: {dashboard_uri}",
        fg="green",
    )

import datetime
import json
import logging
import os
import pathlib
import subprocess
import tempfile
import zipfile
from time import sleep
from typing import Dict, List, Tuple

import click
import requests
import yaml
from click_aliases import ClickAliasedGroup

import gantry
from gantry.api_client import APIClient

logger = logging.getLogger(__name__)


PENDING_TASK_STATUSES = [
    "NOT_YET_STARTED",
    "BUILD_IN_PROGRESS",
    "BUILD_SUCCEEDED",
    "PUSH_SUCCEEDED",
    "PUBLISH_LAMBDA_VERSION_SUCCEEDED",
]


@click.group(cls=ClickAliasedGroup)
def projection():
    """
    Use this to register a new custom projection to Gantry.
    """


class DependenciesInstallError(Exception):
    pass


def _update_dev_projection(
    api_client: APIClient, projection: Dict, projection_dir: str, dry_run: bool
):
    """
    For Gantry's developers only: Upload a custom projection directly from a folder
    that contains:
        1. config.yaml: contains custom projection definition
        2. function.zip: source code with all required dependencies to get invoked as a lambda
    """
    click.secho("Parsing custom projection configs...", nl=False, fg="cyan")
    projection = _get_custom_projection_configs(projection_dir)
    click.secho("SUCCESS", fg="cyan")

    click.secho("Validate custom projection definition...", nl=False, fg="cyan")
    valid_config, err_msgs = _validate_custom_projection_configs(api_client, projection)
    if not valid_config:
        click.secho("FAILED.", fg="red")
        if err_msgs:
            click.secho("Please fix the following issue(s):", fg="red")
            for err in err_msgs:
                click.secho(f"\t{err}")

        raise click.ClickException("Invalid projection definition")
    click.secho("SUCCESS", fg="cyan")

    if dry_run:
        click.secho("Dry run complete.", fg="cyan")
        return True

    click.secho("Set up upload location...", nl=False, fg="cyan")
    retrieved, resp = _get_s3_destination(api_client, projection)
    if not retrieved:
        click.secho("FAILED.", fg="red")
        err_msg = resp.get("error", "")
        raise click.ClickException(f"Fail to set up upload location: {err_msg}")
    click.secho("SUCCESS", fg="cyan")

    upload_url, s3_key = resp["upload_url"], resp["s3_key"]
    zip_filepath = f"{projection_dir}/function.zip"
    proc = subprocess.run(["curl", "--upload-file", zip_filepath, upload_url])
    if proc.returncode != 0:
        return click.ClickException("Failed to upload custom projection function")

    request_sent, task_id, err_msg = _async_update_custom_projection(api_client, s3_key, projection)
    if not request_sent:
        click.secho("FAILED.", fg="red")
        raise click.ClickException(
            f"Request to submit from-file custom projection failed: {err_msg}"
        )
    click.secho(f"SUCCESS. Task {task_id} has been submitted.", fg="cyan")


@projection.command(aliases=["create"], help="Create or update a custom projection in Gantry")
@click.option("--projection-dir", type=click.Path())
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Enable dry run to verify inputs before actually submitting a custom projection to Gantry",
)
def update(projection_dir, dry_run):
    gantry.init()
    api_client = gantry.get_client().log_store._api_client

    click.secho("Parsing custom projection configs...", nl=False, fg="cyan")
    projection = _get_custom_projection_configs(projection_dir)
    click.secho("SUCCESS", fg="cyan")

    if _is_dev_projection(projection):
        _update_dev_projection(api_client, projection, projection_dir, dry_run)
    else:
        _update_projection(api_client, projection, projection_dir, dry_run)


def _update_projection(api_client: APIClient, projection: Dict, projection_dir: str, dry_run: bool):
    click.secho("Validate custom projection definition...", nl=False, fg="cyan")
    valid_config, err_msgs = _validate_custom_projection_configs(api_client, projection)
    if not valid_config:
        click.secho("FAILED.", fg="red")
        if err_msgs:
            click.secho("Please fix the following issue(s):", fg="red")
            for err in err_msgs:
                click.secho(f"\t{err}")

        raise click.ClickException("Invalid projection definition")
    click.secho("SUCCESS", fg="cyan")

    if dry_run:
        click.secho("Dry run complete.", fg="cyan")
        return True

    click.secho("Set up upload location...", nl=False, fg="cyan")
    retrieved, resp = _get_s3_destination(api_client, projection)
    if not retrieved:
        click.secho("FAILED.", fg="red")
        err_msg = resp.get("error", "")
        raise click.ClickException(f"Fail to set up upload location: {err_msg}")
    click.secho("SUCCESS", fg="cyan")

    upload_url, s3_key = resp["upload_url"], resp["s3_key"]

    click.secho("Upload new definition...", nl=False, fg="cyan")
    with tempfile.TemporaryDirectory() as tmpdirname:
        uploaded, err_msg = _upload_function_zip(
            os.path.join(tmpdirname, "function.zip"), projection_dir, upload_url
        )

    if not uploaded:
        click.secho("FAILED.", fg="red")
        raise click.ClickException(f"Fail to upload new projection definition: {err_msg}")
    click.secho("SUCCESS", fg="cyan")

    click.secho("Submit build custom projection request...", nl=False, fg="cyan")
    request_sent, task_id, err_msg = _async_update_custom_projection(api_client, s3_key, projection)
    if not request_sent:
        click.secho("FAILED.", fg="red")
        raise click.ClickException(f"Request to build custom projection failed: {err_msg}")
    click.secho("SUCCESS", fg="cyan")
    click.secho(f"--> Task {task_id} has been submitted.")

    click.secho("Check build progress...", nl=False, fg="cyan")

    _call_get_build_logs(api_client, task_id)


@projection.command("get-build-logs", help="Display custom projection build logs given task ID")
@click.option("--task-id", type=click.STRING)
def get_build_logs(task_id):
    gantry.init()
    api_client = gantry.get_client().log_store._api_client
    _call_get_build_logs(api_client, task_id)


def _call_get_build_logs(api_client: APIClient, task_id: str):
    status = "NOT_YET_STARTED"
    i, max_attempts, interval_seconds = 0, 60, 10
    while i < max_attempts and status in PENDING_TASK_STATUSES:
        new_status, logs = _get_build_logs(api_client, task_id)
        if status == "ERROR":
            click.secho(f"--> {status}", nl=False, fg="red")
            click.secho(logs)
            break
        elif status == new_status:
            click.secho(".", nl=False)
        else:
            status = new_status
            click.secho("")
            if "FAILED" in status:
                click.secho(f"--> {status}", nl=False, fg="red")
            else:
                click.secho(f"--> {status}", nl=False)
            if logs:
                click.secho("")
                click.secho("Build logs:", fg="cyan")
                click.secho(logs)

        i += 1
        sleep(interval_seconds)

    if i == max_attempts:
        click.secho("Closing connection, custom projection build is still in progress.")


@projection.command("get-logs", help="Retrieve custom projection run logs given a time range")
@click.option("--application-name", type=click.STRING)
@click.option("--projection-name", type=click.STRING)
@click.option(
    "--start",
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]),
    default=None,
    help="Provide a start time to search for logs",
)
@click.option(
    "--end",
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]),
    default=None,
    help="Provide an end time to search for logs",
)
@click.option(
    "--tail",
    type=click.INT,
    default=None,
    help="Get the most recent events. If this option is used, --start and --end will be ignored",
)
@click.option("-v", "--verbose", is_flag=True, default=False, help="List raw event logs")
def get_logs(application_name, projection_name, start, end, tail, verbose):
    gantry.init()
    api_client = gantry.get_client().log_store._api_client

    params = {"limit": tail, "start_time": start, "end_time": end}
    response = api_client.request(
        "GET",
        f"/api/v1/{application_name}/custom_projections/{projection_name}/cloudwatch_logs",
        params=params,
    )
    if response.get("response") != "ok":
        err_msg = response.get("error", "unknown error")
        raise click.ClickException(f"Fail to retrieve logs: {err_msg}.")

    event_logs = response.get("logs", [])
    _display_logs(event_logs, verbose)


def _display_logs(events: List[Dict], verbose: bool = False):
    if verbose:
        for event in events:
            click.echo(event)
    else:
        click.secho(f"Found {len(events)} event(s).", fg="cyan")
        for event in events:
            _display_formatted_log(event)


def _display_formatted_log(event: Dict):
    def format_ts(timestamp: int) -> str:
        timestamp_seconds = timestamp / 1000.0
        return datetime.datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d %H:%M:%S")

    click.secho(f'{format_ts(event["timestamp"])}: ', nl=False, fg="cyan")
    click.secho(event["message"].strip())


def _upload_function_zip(
    zip_file: str, projection_dir: str, presigned_url: str
) -> Tuple[bool, str]:
    zipped, err_msg = _zip_function(projection_dir, zip_file)
    if not zipped:
        return False, err_msg

    resp = requests.put(presigned_url, files={"file": open(zip_file, "rb")})

    if resp.status_code != 200:
        click.secho(resp.text)
        return False, "Failed to upload custom projection function"
    return True, ""


def _zip_function(projection_dir: str, zip_file: str) -> Tuple[bool, str]:
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(projection_dir):
            for file in files:
                filepath = os.path.join(root, file)

                relpath = os.path.relpath(filepath, projection_dir)

                # if this file is part of the extra_deps directory
                # move it up and out of the extra_deps directory
                # by removing the first part of the path
                relpath_path = pathlib.Path(relpath)
                if relpath_path.parts[0] == "extra_deps":
                    relpath = str(pathlib.Path(*relpath_path.parts[1:]))

                zipf.write(filepath, relpath)

    return True, ""


def _get_custom_projection_configs(projection_dir: str) -> Dict:
    config_file = "config.yaml"
    projection = {}
    try:
        with open(f"{projection_dir}/{config_file}", "r") as stream:
            projection = yaml.safe_load(stream)
    except FileNotFoundError:
        raise ValueError(f"{config_file} not found under projection directory.")

    return projection


def _validate_custom_projection_configs(
    api_client: APIClient, projection: Dict
) -> Tuple[bool, List[str]]:
    response = api_client.request(
        "POST",
        "/api/v1/custom_projections/validate",
        data={"projection": json.dumps(projection)},
    )

    if response.get("response") == "ok":
        return True, []
    return False, response.get("errors", [])


def _get_s3_destination(api_client: APIClient, projection: Dict) -> Tuple[bool, Dict]:
    response = api_client.request(
        "GET",
        "/api/v1/custom_projections/pre-upload",
        params={
            "projection_name": projection["function_definition"]["projection_name"],
        },
    )

    if response.get("response") == "ok":
        return True, response
    return False, response


def _async_update_custom_projection(
    api_client: APIClient, s3_key: str, projection: Dict
) -> Tuple[bool, str, str]:
    response = api_client.request(
        "POST",
        "/api/v1/custom_projections",
        data={"s3_key": s3_key, "projection": json.dumps(projection)},
    )

    if response.get("response") == "ok":
        return True, response["task_id"], ""
    return False, "", response.get("error", "Error updating custom projection")


def _get_build_logs(api_client: APIClient, task_id: str) -> Tuple[str, str]:
    response = api_client.request(
        "GET",
        f"/api/v1/custom_projections/logs/{task_id}",
    )
    if response.get("response") == "ok":
        return str(response["status"]), response["logs"]
    return "ERROR", "Error getting task logs"


def _is_dev_projection(projection: Dict) -> bool:
    function_def = projection.get("function_definition")
    if function_def and function_def.get("mode") == "lambda_dev":
        return True
    return False


if __name__ == "__main__":
    projection()

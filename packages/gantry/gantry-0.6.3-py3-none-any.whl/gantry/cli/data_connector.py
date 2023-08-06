import json
from typing import Optional

import click
from click_aliases import ClickAliasedGroup

import gantry
from gantry.api_client import APIClient


@click.group(cls=ClickAliasedGroup)
def data_connector():
    """
    Use this to manage your data connectors with gantry.
    """
    pass


@data_connector.command(
    aliases=["create"],
    help="Creates a new data connector to your data source with Gantry.",
)
@click.option(
    "--name", type=click.STRING, required=True, help="A unique name of the data connector"
)
@click.option(
    "--connection-type",
    type=click.Choice(
        ["SNOWFLAKE", "S3"],
        case_sensitive=False,
    ),
    required=True,
    help="Type of the source data connection",
)
@click.option(
    "--database-name",
    type=click.STRING,
    required=False,
    default="",
    help="Name of the source database. WARNING: this field is DEPRECATED and will be removed in a "
    "future release. Please provide database name to 'options' field.",
)
@click.option(
    "--secret-name",
    type=click.STRING,
    required=True,
    help="Name of the secret registered with Gantry",
)
@click.option(
    "--description", type=click.STRING, required=True, help="Description of the data connector"
)
@click.option(
    "--options",
    type=click.STRING,
    required=True,
    help="""
JSON string of the options for the data connector.

For SNOWFLAKE connection type, the options should be:
    {
        "snowflake_database_name": "string",
        "snowflake_schema_name": "string",
        "snowflake_table_name": "string"
    }

For S3 connection type, the options should be:
    {
        "s3_bucket_name": "string",
        "s3_path_prefix": "string",
        "s3_filetype": "string",
    }
    S3 bucket name is the one provided in the secret you have registered with Gantry.
""",
)
def create(
    name: str,
    connection_type: str,
    database_name: str,
    secret_name: str,
    description: str,
    options: str,
):
    gantry.init()
    api_client: APIClient = gantry.get_client().log_store._api_client
    request_body = {
        "name": name,
        "connection_type": connection_type,
        "database_name": database_name,
        "secret_name": secret_name,
        "description": description,
        "options": json.loads(options),
    }

    resp = api_client.request(
        "POST", "/api/v1/data-connectors/sources", json=request_body, raise_for_status=True
    )

    click.secho("--> ", nl=False, fg="cyan")
    click.secho(f"A source data connector has been created.\n {json.dumps(resp['data'], indent=4)}")


@data_connector.command(
    aliases=["list"],
    help="List data connectors registered with Gantry.",
)
def list():
    gantry.init()
    api_client: APIClient = gantry.get_client().log_store._api_client
    resp = api_client.request("GET", "/api/v1/data-connectors", raise_for_status=True)

    click.secho(f"--> A list of registered data connectors:\n {json.dumps(resp['data'], indent=4)}")


@data_connector.command(
    aliases=["delete"],
    help="Deletes a data connector.",
)
@click.option(
    "--name", type=click.STRING, required=True, help="A unique name of the data connector"
)
def delete(name: str):
    gantry.init()
    api_client: APIClient = gantry.get_client().log_store._api_client
    resp = api_client.request(
        "DELETE", f"/api/v1/data-connectors/sources/{name}", raise_for_status=True
    )

    click.secho(
        f"--> Deleted the source data connector {name}:\n {json.dumps(resp['data'], indent=4)}"
    )


@data_connector.command(
    aliases=["list_pipelines"],
    help="Lists the pipelines for a given app name and status.",
)
@click.option("--app-name", type=click.STRING, required=True, help="The name of the application")
@click.option(
    "--status",
    required=False,
    type=click.Choice(
        ["enabled", "disabled", "any"],
        case_sensitive=False,
    ),
    help="The status of the data connectors",
)
def list_pipelines(app_name: str, status: Optional[str]):
    gantry.init()
    api_client: APIClient = gantry.get_client().log_store._api_client
    enabled_status = "True" if status == "enabled" else "False" if status == "disabled" else "True"
    resp = api_client.request(
        "GET",
        f"/api/v1/data-connectors/pipelines?app_name={app_name}&enabled_status={enabled_status}",
        raise_for_status=True,
    )

    click.secho(
        f"--> The following pipelines are given for \"{app_name}\" app with status \"{status}\":\n\
{json.dumps(resp['data'], indent=4)}"
    )


@data_connector.command(
    aliases=["list_pipeline_operations"],
    help="Lists pipeline operations for a given pipeline name, appname, and status.",
)
@click.option("--pipeline-name", type=click.STRING, required=True, help="The data pipeline name")
@click.option("--app-name", type=click.STRING, required=True, help="The name of the application")
@click.option(
    "--status",
    required=False,
    type=click.Choice(
        ["QUEUED", "RUNNING", "SUCCEEDED", "FAILED"],
        case_sensitive=False,
    ),
    help="The pipeline operation status to filter by",
)
def list_pipeline_operations(pipeline_name: str, app_name: str, status: Optional[str] = ""):
    gantry.init()
    api_client: APIClient = gantry.get_client().log_store._api_client
    query = (
        f"/api/v1/data-connectors/pipeline-operations?app_name={app_name}"
        f"&pipeline_name={pipeline_name}&status={status or ''}"
    )
    resp = api_client.request(
        "GET",
        query,
        raise_for_status=True,
    )

    echo = (
        f"--> The following pipeline operations are given for APP={app_name} "
        f"and PIPELINE={pipeline_name} and STATUS={status} : )\n "
        f"{json.dumps(resp['data'], indent=4)}"
    )
    click.secho(echo)


@data_connector.command(
    aliases=["delete"],
    help="Deletes a data pipeline.",
)
@click.option("--pipeline-name", type=click.STRING, required=True, help="The data pipeline name")
@click.option("--app-name", type=click.STRING, required=True, help="The name of the application")
@click.option("--app-version", type=click.STRING, required=False, help="The version of the model")
def delete_pipeline(pipeline_name: str, app_name: str, app_version: str):
    gantry.init()
    api_client: APIClient = gantry.get_client().log_store._api_client
    query = (
        f"/api/v1/data-connectors/pipelines?pipeline_name={pipeline_name}&app_name={app_name}"
        f"&app_version={app_version}"
    )
    resp = api_client.request(
        "DELETE",
        query,
        raise_for_status=True,
    )

    click.secho(f"--> Deleted the pipeline{pipeline_name}:\n {json.dumps(resp['data'], indent=4)}")


if __name__ == "__main__":
    data_connector()

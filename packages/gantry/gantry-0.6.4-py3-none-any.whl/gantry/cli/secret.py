import json

import click
from click_aliases import ClickAliasedGroup

import gantry
from gantry.api_client import APIClient
from gantry.utils import check_response_status


@click.group(cls=ClickAliasedGroup)
def secret():
    """
    Use this to manage your secret with gantry.
    """


@secret.command(
    aliases=["create"],
    help="Create a secret.",
)
@click.option("--name", type=click.STRING, required=True, help="Secret name")
@click.option(
    "--secret-type",
    required=True,
    type=click.Choice(
        ["AWS", "GCP", "SNOWFLAKE_CONN_STR"],
        case_sensitive=False,
    ),
)
@click.option(
    "--secret-file",
    type=click.STRING,
    required=True,
    help="Json file name which contain your secret info",
)
def create(name: str, secret_type: str, secret_file: str):
    gantry.init()
    api_client: APIClient = gantry.get_client().log_store._api_client
    with open(secret_file, "r") as f:
        data = {
            "secret_name": name,
            "secret_type": secret_type.upper(),
            "secret_content": json.load(f),
        }

    resp = api_client.request(
        "POST", "/api/v1/customer-resources/secrets", json=data, raise_for_status=True
    )

    check_response_status(resp, f"Fail to create secret {name}")
    click.secho(f"--> Secret has been created.\n {resp['data']}")


@secret.command(
    aliases=["list"],
    help="List your secrets.",
)
def list():
    gantry.init()
    api_client: APIClient = gantry.get_client().log_store._api_client

    resp = api_client.request("GET", "/api/v1/customer-resources/secrets", raise_for_status=True)
    check_response_status(resp, "Fail to list secrets")
    for data in resp["data"]:
        click.secho(data)


@secret.command(
    aliases=["delete"],
    help="Delete secret",
)
@click.option("--secret-id", type=click.STRING, required=True, help="Secret id")
def delete(secret_id: str):
    gantry.init()
    api_client: APIClient = gantry.get_client().log_store._api_client

    resp = api_client.request(
        "DELETE", f"/api/v1/customer-resources/secrets/{secret_id}", raise_for_status=True
    )

    check_response_status(resp, "Fail to delete secret")
    click.secho(f"--> Secret {secret_id} has been deleted.")

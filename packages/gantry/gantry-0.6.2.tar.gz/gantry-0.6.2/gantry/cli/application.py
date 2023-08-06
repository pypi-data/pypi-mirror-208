from typing import Optional

import click
from click_aliases import ClickAliasedGroup

import gantry
from gantry.query.core.utils import get_application_node_id


@click.group(cls=ClickAliasedGroup)
def application():
    """
    Use this to handle application metadata in gantry.
    """


@application.command(
    aliases=["hard_delete"],
    help="Hard delete an existing application in Gantry. \
    This is an irreversible action!",
)
@click.option("--application-name", type=click.STRING)
@click.option("--version", default=None, type=click.STRING)
def hard_delete(application_name: str, version: Optional[str]):
    gantry.init()
    api_client = gantry.get_client().log_store._api_client
    click.confirm(
        f"Are you sure you want to hard delete the application: {application_name} \
at version: {version if version is not None else 'latest'}?",
        abort=True,
    )
    application_id = get_application_node_id(api_client, application_name, version=version)
    response = api_client.request(
        "POST",
        f"/api/v1/applications/{application_id}/hard_delete",
    )
    if response.get("response") != "ok":
        err_msg = response.get("error", "unknown error")
        raise click.ClickException(f"Fail to hard delete application: {err_msg}.")

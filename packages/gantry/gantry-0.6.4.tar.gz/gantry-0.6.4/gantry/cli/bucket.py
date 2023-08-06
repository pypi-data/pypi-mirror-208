from typing import Optional

import click
from click_aliases import ClickAliasedGroup

import gantry
from gantry.api_client import APIClient
from gantry.utils import check_response_status

STORAGE_TYPES = ["S3", "GCS"]


@click.group(cls=ClickAliasedGroup)
def bucket():
    """
    Use this to manage your bucket with gantry.
    """


@bucket.command(
    aliases=["create"],
    help="Register your bucket with Gantry.",
)
@click.option("--name", type=click.STRING, required=True, help="Bucket name")
@click.option(
    "--region",
    type=click.STRING,
    required=True,
    help="Region of your bucket, for GCS buckets you can set this to auto",
)
@click.option(
    "--storage-type", required=True, type=click.Choice(STORAGE_TYPES, case_sensitive=False)
)
@click.option("--secret", default=None, type=click.STRING, help="Secret name")
def create(name: str, region: str, storage_type: str, secret: Optional[str]):
    gantry.init()
    api_client = gantry.get_client().log_store._api_client
    data = {
        "bucket_name": name,
        "region": region,
        "storage_type": storage_type.upper(),
        "secret_name": secret,
    }

    resp = api_client.request(
        "POST", "/api/v1/customer-resources/buckets", json=data, raise_for_status=True
    )

    check_response_status(resp, f"Fail to register bucket {name}")
    click.secho(f"--> Bucket {name} has been registered.")


@bucket.command(
    aliases=["list"],
    help="List buckets.",
)
def list():
    gantry.init()
    api_client = gantry.get_client().log_store._api_client

    resp = api_client.request("GET", "/api/v1/customer-resources/buckets", raise_for_status=True)

    check_response_status(resp, "Fail to list buckets")
    for data in resp["data"]:
        click.secho(data)


@bucket.command(
    aliases=["update-secrete"],
    help="Update bucket secret key.",
)
@click.option("--bucket", type=click.STRING, required=True, help="Bucket name")
@click.option(
    "--storage-type", required=True, type=click.Choice(STORAGE_TYPES, case_sensitive=False)
)
@click.option("--secret-id", type=click.STRING, default=None, help="Secret id")
def update_secret(bucket: str, storage_type: str, secret_id: Optional[str]):
    gantry.init()
    api_client = gantry.get_client().log_store._api_client
    bucket_id = _get_bucket_id(api_client, bucket, storage_type.upper())
    data = {}
    if secret_id:
        data["secret_id"] = secret_id

    resp = api_client.request(
        "PATCH", f"/api/v1/customer-resources/buckets/{bucket_id}", json=data, raise_for_status=True
    )
    check_response_status(resp, f"Fail to update bucket {bucket}")
    click.secho(f"--> Bucket {bucket} has been updated with key {secret_id}.")


def _get_bucket_id(api_client: APIClient, bucket_name: str, storage_type: str) -> str:
    resp = api_client.request(
        "GET",
        f"/api/v1/customer-resources/buckets/{bucket_name}?storage_type={storage_type.upper()}",
        raise_for_status=True,
    )
    return resp["data"]["id"]

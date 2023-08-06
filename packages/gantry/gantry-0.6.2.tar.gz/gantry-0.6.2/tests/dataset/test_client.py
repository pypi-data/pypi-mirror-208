import pathlib
import uuid

import pytest
import responses

from gantry.api_client import APIClient
from gantry.dataset.client import GantryDatasetClient
from gantry.exceptions import DatasetNotFoundError, GantryRequestException

from .conftest import BUCKET_NAME, DATASET_ID, DATASET_NAME, HOST


@pytest.fixture
def test_api_client():
    return APIClient(origin=HOST)


@pytest.fixture
def test_client(test_api_client):
    return GantryDatasetClient(
        api_client=test_api_client,
        working_directory=".",
    )


def test_create_dataset(test_client, test_dataset):
    """
    Test create dataset
    """
    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/datasets",
            json={
                "response": "ok",
                "data": test_dataset,
            },
            headers={"Content-Type": "application/json"},
        )
        dataset = test_client.create_dataset(DATASET_NAME)
        assert dataset._dataset_id == DATASET_ID
        assert dataset.dataset_name == DATASET_NAME
        assert dataset.workspace == "."


def test_create_dataset_with_model(test_client, test_dataset):
    """
    Test create dataset with model name
    """
    with responses.RequestsMock() as resp:
        MODEL_ID = str(uuid.uuid4())
        MODEL_NAME = "test_model"
        resp.add(
            resp.GET,
            f"https://test-api/api/v1/applications/{MODEL_NAME}/schemas",
            json={
                "response": "ok",
                "data": {"id": MODEL_ID},
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/datasets",
            json={
                "response": "ok",
                "data": test_dataset,
            },
            headers={"Content-Type": "application/json"},
            match=[
                responses.matchers.json_params_matcher(
                    {
                        "name": DATASET_NAME,
                        "model_id": MODEL_ID,
                        "bucket_name": BUCKET_NAME,
                    }
                )
            ],
        )
        dataset = test_client.create_dataset(
            DATASET_NAME, bucket_name=BUCKET_NAME, app_name="test_model"
        )
        assert dataset._dataset_id == DATASET_ID
        assert dataset.dataset_name == DATASET_NAME
        assert dataset.workspace == "."


def test_get_dataset(test_client, test_dataset):
    """
    Test get dataset
    """
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_NAME}",
            json={
                "response": "ok",
                "data": test_dataset,
            },
            headers={"Content-Type": "application/json"},
        )
        dataset = test_client.get_dataset(DATASET_NAME)
        assert dataset._dataset_id == DATASET_ID
        assert dataset.dataset_name == DATASET_NAME
        assert dataset.workspace == "."


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [(404, DatasetNotFoundError), (500, GantryRequestException)],
)
def test_get_dataset_error(test_client, status_code, expected_error):
    """
    Test get dataset error
    """
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_NAME}",
            status=status_code,
            headers={"Content-Type": "application/json"},
        )
        with pytest.raises(expected_error):
            test_client.get_dataset(DATASET_NAME)


def test_list_dataset_versions(test_client, test_dataset, commit_history):
    """
    Test get dataset commits
    """
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_NAME}",
            json={
                "response": "ok",
                "data": test_dataset,
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/commits",
            json={
                "response": "ok",
                "data": commit_history,
            },
            headers={"Content-Type": "application/json"},
        )
        commits = test_client.list_dataset_versions(DATASET_NAME)
        assert len(commits) == 2


@pytest.mark.parametrize("include_deleted", [True, False])
def test_list_datasets(test_client, test_dataset, include_deleted):
    """
    List datasets
    """
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets?include_deleted={include_deleted}",
            json={
                "response": "ok",
                "data": [test_dataset],
            },
            headers={"Content-Type": "application/json"},
        )
        datasets = test_client.list_datasets(include_deleted=include_deleted)
        assert len(datasets) == 1


def test_delete_dataset(test_client, test_dataset):
    """
    Delete specific dataset
    """
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_NAME}",
            json={
                "response": "ok",
                "data": test_dataset,
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.DELETE,
            f"{HOST}/api/v1/datasets/{DATASET_ID}",
            json={
                "response": "ok",
            },
            headers={"Content-Type": "application/json"},
        )

        test_client.delete_dataset(DATASET_NAME)


def test_set_working_dir(test_client):
    assert test_client.working_directory == "."
    test_client.set_working_directory("test_dir")
    assert test_client.working_directory == str(pathlib.Path("test_dir").resolve())

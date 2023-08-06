import datetime
import json
import logging
import os
import uuid
from io import StringIO
from pathlib import Path

import datasets
import pandas as pd
import pytest
import responses
from datasets import Sequence, Value, builder
from mock import patch
from responses import matchers

from gantry.api_client import APIClient
from gantry.dataset.constants import (
    DATASET_MANIFEST_FILE,
    DATASET_STASH_FILE,
    DELETED_FILES,
    MODIFIED_FILES,
    NEW_FILES,
    STASH_FOLDER,
)
from gantry.dataset.gantry_dataset import DatasetFileInfo, GantryDataset
from gantry.exceptions import (
    DataSchemaMismatchError,
    DatasetCommitNotFoundError,
    DatasetHeadOutOfDateException,
    DatasetNotFoundError,
    GantryException,
    GantryRequestException,
    NoTabularDataError,
)
from gantry.query.core.dataframe import GantryDataFrame
from gantry.utils import get_files_checksum, list_all_files

from .conftest import (
    AWS_REGION,
    BUCKET_NAME,
    COMMIT_MSG,
    CONF_OBJ_KEY,
    CSV_OBJ_KEY,
    DATASET_ID,
    DATASET_NAME,
    HOST,
    IMG_OBJ_KEY,
    MANIFEST_OBJ_KEY,
    MANIFEST_VERSION_ID,
    README_OBJ_KEY,
    S3_PREFIX,
)


@pytest.fixture
def test_api_client():
    return APIClient(origin=HOST)


@pytest.fixture(scope="function")
def gantry_dataset_obj(test_api_client, datadir):
    return GantryDataset(
        api_client=test_api_client,
        dataset_name=DATASET_NAME,
        dataset_id=DATASET_ID,
        bucket_name=BUCKET_NAME,
        aws_region=AWS_REGION,
        dataset_s3_prefix=S3_PREFIX,
        workspace=datadir,
    )


def test_list_commits(gantry_dataset_obj, commit_history):
    """
    Test get dataset commits
    """
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/commits",
            json={
                "response": "ok",
                "data": commit_history,
            },
            headers={"Content-Type": "application/json"},
        )
        commits = gantry_dataset_obj.list_versions()
        assert len(commits) == 2


def test_get_commit(gantry_dataset_obj, commit_history):
    """
    Test get commit information
    """
    expected_commit = commit_history[1]
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/commits/{expected_commit['id']}",
            json={
                "response": "ok",
                "data": expected_commit,
            },
            headers={"Content-Type": "application/json"},
        )
        commit = gantry_dataset_obj._get_commit(expected_commit["id"])
        assert commit == expected_commit


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [(404, DatasetCommitNotFoundError), (500, GantryRequestException)],
)
def test_get_commit_error(gantry_dataset_obj, commit_history, status_code, expected_error):
    commit_id = commit_history[0]["id"]
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/commits/{commit_id}",
            status=status_code,
            headers={"Content-Type": "application/json"},
        )
        with pytest.raises(expected_error):
            gantry_dataset_obj._get_commit(commit_id)


def test_get_latest_commit(gantry_dataset_obj, commit_history):
    """
    Test get latest commit
    """
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/commits",
            json={
                "response": "ok",
                "data": commit_history,
            },
            headers={"Content-Type": "application/json"},
        )
        latest_commit = gantry_dataset_obj._get_latest_commit()
        assert latest_commit["id"] == "8ee0f6d5-c84c-473a-931a-5148b2e704d7"
        assert latest_commit["is_latest_commit"]


def test_get_diff(gantry_dataset_obj):
    """
    Test get local edit diff
    """
    # overwrite the dataset name
    gantry_dataset_obj.dataset_name = "show_diff_dataset"

    diff = gantry_dataset_obj.get_diff()

    assert set(diff[NEW_FILES]) == {"artifacts/kitten.png", "tabular_manifests/feedback.csv"}
    assert diff[MODIFIED_FILES] == ["dataset_config.yaml"]
    assert diff[DELETED_FILES] == ["README.md"]


def test_get_diff_not_exist(gantry_dataset_obj):
    """
    Test get diff without download the dataset
    """
    # overwrite the dataset name
    gantry_dataset_obj.dataset_name = "dataset_not_exist"
    with pytest.raises(DatasetNotFoundError):
        gantry_dataset_obj.get_diff()


def test_create_commit_without_download(gantry_dataset_obj):
    """
    Test create commit when no dataset downloaded locally
    """
    # overwrite the dataset name
    gantry_dataset_obj.dataset_name = "dataset_not_exist"
    with pytest.raises(DatasetNotFoundError):
        gantry_dataset_obj.push_version("test commit")


@patch(
    "gantry.dataset.gantry_dataset.GantryDataset._get_manifest_presign_url",
    return_value="s3://manifest/presign/url",
)
@patch("gantry.dataset.gantry_dataset.GantryDataset._get_tabular_files", return_value=[])
@patch(
    "gantry.dataset.gantry_dataset.GantryDataset._extract_feature_schema_from_s3", return_value={}
)
def test_pull_huggingface_dataset_by_version_no_schema(
    mock_get_presign_url,
    mock_get_tabular_files,
    mock_extract_feature_schema_from_s3,
    gantry_dataset_obj,
):
    """
    Test pull huggingface dataset by version
    """
    with pytest.raises(DataSchemaMismatchError):
        gantry_dataset_obj.pull_huggingface_dataset_by_version(
            hf_dataset_name="hf_test",
            version_id="1.0.0",
        )


@patch(
    "gantry.dataset.gantry_dataset.GantryDataset._get_manifest_presign_url",
    return_value="s3://manifest/presign/url",
)
@patch("gantry.dataset.gantry_dataset.GantryDataset._get_tabular_files", return_value=[])
@patch(
    "gantry.dataset.gantry_dataset.GantryDataset._extract_feature_schema_from_s3",
    return_value={"feature": "schema"},
)
def test_pull_huggingface_dataset_by_version_no_data(
    mock_get_presign_url,
    mock_get_tabular_files,
    mock_extract_feature_schema_from_s3,
    gantry_dataset_obj,
):
    """
    Test pull huggingface dataset by version
    """
    with pytest.raises(NoTabularDataError):
        gantry_dataset_obj.pull_huggingface_dataset_by_version(
            hf_dataset_name="hf_test",
            version_id="1.0.0",
        )


@pytest.mark.parametrize("correct_schema, streaming", [(True, True), (True, False), (False, False)])
@patch(
    "gantry.dataset.gantry_dataset.GantryDataset._get_manifest_presign_url",
    return_value="s3://manifest/presign/url",
)
@patch("gantry.dataset.gantry_dataset.GantryDataset._get_tabular_files")
@patch("gantry.dataset.gantry_dataset.GantryDataset._extract_feature_schema_from_s3")
@patch("gantry.dataset.gantry_dataset.GantryDataset._generate_get_presign_url")
def test_pull_huggingface_dataset_by_version(
    mock_generate_get_presign_url,
    mock_extract_feature_schema_from_s3,
    mock_get_tabular_files,
    mock_get_manifest_presign_url,
    correct_schema,
    streaming,
    gantry_dataset_obj,
    datadir,
):
    """
    Test pull huggingface dataset by version
    """

    if correct_schema:
        mock_extract_feature_schema_from_s3.return_value = {
            "inputs.credit_history": Value(dtype="string", id=None),
            "inputs.credit_scores": Sequence(
                feature=Value(dtype="float64", id=None), length=-1, id=None
            ),
            "inputs.description": Value(dtype="string", id=None),
            "inputs.image_uri": Value(dtype="string", id=None),
            "inputs.income": Value(dtype="int64", id=None),
            "inputs.loan_id": Value(dtype="string", id=None),
            "inputs.prediction": Value(dtype="bool", id=None),
            "inputs.timestamp": Value(dtype="timestamp[ns, tz=UTC]", id=None),
            "outputs.output": Value(dtype="float64", id=None),
            "feedback.loan_repaid": Value(dtype="bool", id=None),
            "__time": Value(dtype="timestamp[ns, tz=UTC]", id=None),
        }
    else:
        mock_extract_feature_schema_from_s3.return_value = {
            "inputs.credit_history": Value(dtype="string", id=None),
            "inputs.prediction": Value(dtype="bool", id=None),
            "inputs.timestamp": Value(dtype="timestamp[ns, tz=UTC]", id=None),
            "outputs.output": Value(dtype="float64", id=None),
            "feedback.loan_repaid": Value(dtype="bool", id=None),
            "__time": Value(dtype="timestamp[ns, tz=UTC]", id=None),
        }

    def side_effect(**kwargs):
        return {f.file_name: f.url for f in kwargs["batch"]}

    mock_get_tabular_files.return_value = [
        DatasetFileInfo(
            file_name="mock_tabular_file_1.csv",
            # for unit test we use local file path instead of s3 url
            url=str(datadir / "hf-test" / "tabular_manifests" / "hf_dataset_1.csv"),
            version_id="mock_version_id",
        ),
        DatasetFileInfo(
            file_name="mock_tabular_file_2.csv",
            url=str(datadir / "hf-test" / "tabular_manifests" / "hf_dataset_2.csv"),
            version_id="mock_version_id",
        ),
    ]
    mock_generate_get_presign_url.side_effect = side_effect

    if correct_schema:
        hf_dataset = gantry_dataset_obj.pull_huggingface_dataset_by_version(
            version_id="mock_version_id", hf_dataset_name="hf_test", streaming=streaming
        )
        if not streaming:
            assert len(hf_dataset) == 40
        else:
            assert len(list(hf_dataset)) == 40
            hf_dataset.__class__ = datasets.iterable_dataset.IterableDataset

        assert hf_dataset.features == {
            "inputs.credit_history": Value(dtype="string", id=None),
            "inputs.credit_scores": Sequence(
                feature=Value(dtype="float64", id=None), length=-1, id=None
            ),
            "inputs.description": Value(dtype="string", id=None),
            "inputs.image_uri": Value(dtype="string", id=None),
            "inputs.income": Value(dtype="int64", id=None),
            "inputs.loan_id": Value(dtype="string", id=None),
            "inputs.prediction": Value(dtype="bool", id=None),
            "inputs.timestamp": Value(dtype="timestamp[ns, tz=UTC]", id=None),
            "outputs.output": Value(dtype="float64", id=None),
            "feedback.loan_repaid": Value(dtype="bool", id=None),
            "__time": Value(dtype="timestamp[ns, tz=UTC]", id=None),
        }
        assert hf_dataset.builder_name == "hf_test"
    else:
        with pytest.raises(DataSchemaMismatchError):
            hf_dataset = gantry_dataset_obj.pull_huggingface_dataset_by_version(
                version_id="mock_version_id", hf_dataset_name="hf_test"
            )


def test_get_tabular_files(gantry_dataset_obj, datadir):
    with responses.RequestsMock() as resp:
        MOCK_URL = "http://mock-url"
        manifest_file = datadir / "hf-test" / ".dataset_metadata" / ".gantry_manifest.jsonl"
        resp.add(responses.GET, MOCK_URL, body=manifest_file.read_text())
        tabular_files = gantry_dataset_obj._get_tabular_files(MOCK_URL)
        assert len(tabular_files) == 2
        assert tabular_files[0].file_name.endswith(".csv")
        assert tabular_files[0].file_name.endswith(".csv")


@patch("gantry.dataset.gantry_dataset.GantryDataset._get_obj_key", return_value="mock_obj")
@patch(
    "gantry.dataset.gantry_dataset.GantryDataset._generate_get_presign_url",
    return_value={"mock_obj": "http://mock-config-url"},
)
def test_extract_feature_schema_from_s3(
    mock_generate_get_presign_url, mock_get_obj_key, gantry_dataset_obj, datadir
):
    MANIFEST_URL = "http://mock-manifest-url"
    with responses.RequestsMock() as resp:
        manifest_file = datadir / "hf-test" / ".dataset_metadata" / ".gantry_manifest.jsonl"
        resp.add(responses.GET, MANIFEST_URL, body=manifest_file.read_text())
        config_file = datadir / "hf-test" / "dataset_config.yaml"
        resp.add(responses.GET, "http://mock-config-url", body=config_file.read_text())
        features = gantry_dataset_obj._extract_feature_schema_from_s3(MANIFEST_URL)
        assert len(features) == 11


@pytest.mark.parametrize("use_latest_commit", [True, False])
@patch("gantry.dataset.gantry_dataset.GantryDataset._get_commit")
@patch("gantry.dataset.gantry_dataset.GantryDataset._get_latest_commit")
@patch("gantry.dataset.gantry_dataset.GantryDataset._generate_get_presign_url")
def test_get_manifest_presign_url(
    mock_generate_get_presign_url,
    mock_get_latest_commit,
    mock_get_commit,
    use_latest_commit,
    commit_history,
    gantry_dataset_obj,
):
    mock_get_latest_commit.return_value = commit_history[0]
    mock_get_commit.return_value = commit_history[1]

    def side_effect(args):
        return {gantry_dataset_obj._get_obj_key(args[0].url): f"{args[0].url}-presign"}

    mock_generate_get_presign_url.side_effect = side_effect
    if use_latest_commit:
        presign_url = gantry_dataset_obj._get_manifest_presign_url()
    else:
        presign_url = gantry_dataset_obj._get_manifest_presign_url(
            version_id=commit_history[1]["id"]
        )
    assert presign_url.endswith("presign")


@pytest.mark.parametrize(
    ["dataset_name", "hf_name", "expected_name", "streaming"],
    [
        ("hf-test", "hf_name", "hf_name", False),
        ("hf-test", None, "hftest", False),
        ("hf-test", "hf_name", "hf_name", True),
        ("hf-test", None, "hftest", True),
    ],
)
def test_get_huggingface_dataset(
    dataset_name, hf_name, expected_name, streaming, gantry_dataset_obj
):
    """
    Test get local edit diff
    """
    # overwrite the dataset name
    gantry_dataset_obj.dataset_name = dataset_name

    hf_dataset = gantry_dataset_obj.get_huggingface_dataset(
        hf_dataset_name=hf_name, streaming=streaming
    )

    if not streaming:
        assert len(hf_dataset) == 40
    else:
        len(list(hf_dataset)) == 40
        assert hf_dataset.__class__ == datasets.iterable_dataset.IterableDataset

    assert hf_dataset.features == {
        "inputs.credit_history": Value(dtype="string", id=None),
        "inputs.credit_scores": Sequence(
            feature=Value(dtype="float64", id=None), length=-1, id=None
        ),
        "inputs.description": Value(dtype="string", id=None),
        "inputs.image_uri": Value(dtype="string", id=None),
        "inputs.income": Value(dtype="int64", id=None),
        "inputs.loan_id": Value(dtype="string", id=None),
        "inputs.prediction": Value(dtype="bool", id=None),
        "inputs.timestamp": Value(dtype="timestamp[ns, tz=UTC]", id=None),
        "outputs.output": Value(dtype="float64", id=None),
        "feedback.loan_repaid": Value(dtype="bool", id=None),
        "__time": Value(dtype="timestamp[ns, tz=UTC]", id=None),
    }
    assert hf_dataset.builder_name == expected_name


@pytest.mark.parametrize(
    ["dataset_name", "hf_name", "load_from_remote"],
    [
        ("12-123", None, True),
        ("hf_test", "123", True),
        ("12-123", None, False),
        ("hf_test", "123", False),
    ],
)
def test_get_huggingface_dataset_error(dataset_name, hf_name, load_from_remote, gantry_dataset_obj):
    gantry_dataset_obj.dataset_name = dataset_name
    if load_from_remote:
        hf_dataset = gantry_dataset_obj.pull_huggingface_dataset_by_version(hf_dataset_name=hf_name)
    else:
        hf_dataset = gantry_dataset_obj.get_huggingface_dataset(hf_dataset_name=hf_name)

    assert hf_dataset is None


def test_get_huggingface_dataset_no_folder(gantry_dataset_obj):
    """
    Test error when no tabular manifests folder
    """
    gantry_dataset_obj.dataset_name = "no_tabular_manifest_dataset"

    with pytest.raises(NoTabularDataError):
        gantry_dataset_obj.get_huggingface_dataset()


def test_get_huggingface_dataset_mismatch_schema(gantry_dataset_obj):
    """
    Test error when no tabular manifests folder
    """
    gantry_dataset_obj.dataset_name = "mismatch_config_dataset"

    with pytest.raises(DataSchemaMismatchError):
        gantry_dataset_obj.get_huggingface_dataset()


def test_get_huggingface_dataset_bad_data_type_schema(gantry_dataset_obj):
    """
    Test error when no tabular manifests folder
    """
    gantry_dataset_obj.dataset_name = "bad_data_config_dataset"

    with pytest.raises(DataSchemaMismatchError) as e:
        gantry_dataset_obj.get_huggingface_dataset()

    assert isinstance(e.value.__cause__, builder.DatasetGenerationError)


def setup_resp_for_deleted_check(resp, is_deleted=False, dataset_name=DATASET_NAME):
    resp.add(
        resp.GET,
        f"{HOST}/api/v1/datasets/{dataset_name}",
        json={
            "response": "ok",
            "data": {
                "id": DATASET_ID,
                "name": dataset_name,
                "organization_id": "fake-org-id",
                "bucket_name": BUCKET_NAME,
                "disabled": is_deleted,
            },
        },
        headers={"Content-Type": "application/json"},
    )


def setup_resp_for_head_check(resp, latest_commit, dataset_id=DATASET_ID):
    resp.add(
        resp.GET,
        f"{HOST}/api/v1/datasets/{dataset_id}/commits",
        json={
            "response": "ok",
            "data": [latest_commit],
        },
        headers={"Content-Type": "application/json"},
    )


def setup_resp_for_create_commit(
    datadir, resp, create_commit_resp_json, commit_id, create_commit_status_code=200
):
    # fake urls for uploading files
    resp.add(
        resp.POST,
        f"{HOST}/api/v1/datasets/{DATASET_ID}/presign/putobject",
        json={
            "response": "ok",
            "data": {
                MANIFEST_OBJ_KEY: f"{HOST}/fake_presigned_url",
                CONF_OBJ_KEY: f"{HOST}/fake_presigned_url",
                README_OBJ_KEY: f"{HOST}/fake_presigned_url",
                IMG_OBJ_KEY: f"{HOST}/fake_presigned_url",
                CSV_OBJ_KEY: f"{HOST}/fake_presigned_url",
            },
        },
        headers={"Content-Type": "application/json"},
    )
    resp.add(
        resp.PUT,
        f"{HOST}/fake_presigned_url",
        json={"response": "ok"},
        headers={"Content-Type": "application/json", "x-amz-version-id": MANIFEST_VERSION_ID},
    )

    with open(datadir / f"{DATASET_NAME}/.dataset_metadata/HEAD") as f:
        old_commit = json.load(f)

    # for the actual commit creation request
    resp.add(
        resp.POST,
        f"{HOST}/api/v1/datasets/{DATASET_ID}/commits",
        json=create_commit_resp_json,
        headers={"Content-Type": "application/json"},
        status=create_commit_status_code,
        match=[
            matchers.json_params_matcher(
                {
                    "message": COMMIT_MSG,
                    "metadata_s3_file_version": MANIFEST_VERSION_ID,
                    "parent_commit_id": old_commit["id"],
                    "commit_id": commit_id,
                }
            )
        ],
    )


def setup_resp_for_sync(
    resp,
    commit_id,
    commit_json,
    manifest_file,
    dataset_id=DATASET_ID,
    do_fake_presigned=True,
):
    # getting commit info
    if commit_id is not None:  # if commit_id is specified
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{dataset_id}/commits/{commit_id}",
            json={
                "response": "ok",
                "data": commit_json,
            },
            headers={"Content-Type": "application/json"},
        )
    else:  # if we're syncing to latest
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{dataset_id}/commits",
            json={
                "response": "ok",
                "data": [commit_json],
            },
            headers={"Content-Type": "application/json"},
        )

    # getting the fake urls for the objects
    resp.add(
        resp.POST,
        f"{HOST}/api/v1/datasets/{dataset_id}/presign/getobject",
        json={
            "response": "ok",
            "data": {
                MANIFEST_OBJ_KEY: f"{HOST}/fake_manifest",
                CONF_OBJ_KEY: f"{HOST}/fake_presigned_url",
                README_OBJ_KEY: f"{HOST}/fake_presigned_url",
            },
        },
        headers={"Content-Type": "application/json"},
    )

    # adding responses for the fake download urls
    req_kwargs = {
        "stream": True,
    }
    resp.add(
        resp.GET,
        f"{HOST}/fake_manifest",
        body=manifest_file.read(),
        match=[matchers.request_kwargs_matcher(req_kwargs)],
    )
    if do_fake_presigned:
        resp.add(
            resp.GET,
            f"{HOST}/fake_presigned_url",
            body="fake_response",
            match=[matchers.request_kwargs_matcher(req_kwargs)],
        )


def setup_resp_for_add_file(resp, commit_message, filename, parent_commit_id=None):
    file_dir = "artifacts"
    if len(filename) > 4 and filename[-4:] == ".csv":
        file_dir = "tabular_manifests"

    file_url = f"org_id/datasets/v1/{DATASET_NAME}/test-uuid-1/{file_dir}/{filename}"

    # for uploading the added file and the manifest file
    resp.add(
        resp.POST,
        f"{HOST}/api/v1/datasets/{DATASET_ID}/presign/putobject",
        json={
            "response": "ok",
            "data": {
                file_url: f"{HOST}/fake_presigned_url_0",
                MANIFEST_OBJ_KEY: f"{HOST}/fake_presigned_url_1",
            },
        },
        headers={"Content-Type": "application/json"},
    )
    # for downloading the manifest file
    resp.add(
        resp.POST,
        f"{HOST}/api/v1/datasets/{DATASET_ID}/presign/getobject",
        json={
            "response": "ok",
            "data": {
                MANIFEST_OBJ_KEY: f"{HOST}/fake_presigned_url_2",
            },
        },
        headers={"Content-Type": "application/json"},
    )

    # fake presigned urls for downloading/uploading files
    resp.add(
        resp.PUT,
        f"{HOST}/fake_presigned_url_0",
        json={"response": "ok"},
        headers={"x-amz-version-id": "fake_version_id"},
    )
    resp.add(
        resp.PUT,
        f"{HOST}/fake_presigned_url_1",
        json={"response": "ok"},
        headers={"x-amz-version-id": MANIFEST_VERSION_ID},
    )
    resp.add(
        resp.GET,
        f"{HOST}/fake_presigned_url_2",
        body="test-string",
    )

    # for getting the latest commit
    if not parent_commit_id:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/commits",
            json={
                "response": "ok",
                "data": [{"id": "4569ef0b-ff96-4110-a606-8d9d54fab382"}],
            },
            headers={"Content-Type": "application/json"},
        )

    # for the actual commit creation request
    resp.add(
        resp.POST,
        f"{HOST}/api/v1/datasets/{DATASET_ID}/commits",
        json={
            "data": {
                "created_at": "Wed, 07 Oct 2022 06:11:02 GMT",
                "created_by": "db459d6d-c83b-496d-b659-e48bca971156",
                "dataset_id": DATASET_ID,
                "id": "add-file-commit-id",
                "is_latest_commit": True,
                "message": commit_message,
                "metadata_s3_file_version": MANIFEST_VERSION_ID,
                "parent_commit": "8ee0f6d5-c84c-473a-931a-5148b2e704d7",
            },
        },
        headers={"Content-Type": "application/json"},
        status=200,
        match=[
            matchers.json_params_matcher(
                {
                    "message": commit_message,
                    "metadata_s3_file_version": MANIFEST_VERSION_ID,
                    "parent_commit_id": parent_commit_id or "4569ef0b-ff96-4110-a606-8d9d54fab382",
                    "commit_id": "test-uuid-1",
                }
            )
        ],
    )


@patch("uuid.uuid4", return_value="test-uuid-1")
def test_create_commit(mock_uuid, datadir, gantry_dataset_obj, commit_history):
    """
    Test create commit succeed
    """
    with responses.RequestsMock() as resp:
        setup_resp_for_create_commit(
            datadir, resp, {"response": "ok", "data": commit_history[0]}, "test-uuid-1"
        )
        setup_resp_for_deleted_check(resp)
        with open(datadir / f"{DATASET_NAME}/.dataset_metadata/HEAD") as f:
            setup_resp_for_head_check(resp, json.load(f))  # we are on latest commit

        gantry_dataset_obj.push_version(COMMIT_MSG)

        diff = gantry_dataset_obj.get_diff()

        # verify no diff after a successful commit
        assert not diff[NEW_FILES]
        assert not diff[MODIFIED_FILES]
        assert not diff[DELETED_FILES]

        with open(datadir / f"{DATASET_NAME}/.dataset_metadata/HEAD") as f:
            assert json.load(f) == commit_history[0]  # verify HEAD has been updated


@patch("uuid.uuid4", return_value="test-uuid-1")
def test_create_commit_failure(mock_uuid, datadir, gantry_dataset_obj, commit_history):
    """
    Test create commit failure, in this case we detect the head is not up to date and stop
    prematurely. This will happen during a race condition when another user committed a change and
    the local copy has not been synced subsequently.
    """
    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        setup_resp_for_head_check(resp, commit_history[0])  # we are NOT on latest commit

        with pytest.raises(DatasetHeadOutOfDateException):
            gantry_dataset_obj.push_version(COMMIT_MSG)

        diff = gantry_dataset_obj.get_diff()

        # since commit failed the local diff will be the same
        assert set(diff[NEW_FILES]) == {"artifacts/kitten.png", "tabular_manifests/feedback.csv"}
        assert diff[MODIFIED_FILES] == ["dataset_config.yaml"]
        assert diff[DELETED_FILES] == ["README.md"]


def test_create_commit_nochange(datadir, gantry_dataset_obj):
    """
    Test create commit without any local change
    """
    dataset_name = "unittest_dataset"

    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp, dataset_name=dataset_name)

        gantry_dataset_obj.dataset_name = dataset_name
        with open(datadir / f"{dataset_name}/.dataset_metadata/HEAD") as f:
            old_commit = json.load(f)

        new_commit = gantry_dataset_obj.push_version("new commit")
        assert old_commit == new_commit


def create_mock_manifest(commit_history):
    gantry_manifest = StringIO()
    config_file_info = {
        "file_name": "dataset_config.yaml",
        "url": f"s3://test-bucket/{CONF_OBJ_KEY}",
        "sha256": "unmatched_sha256",
        "version_id": "random_vid_for_config",
    }

    gantry_manifest.write(f"{json.dumps(config_file_info)}\n")

    readme_file_info = {
        "file_name": "README.md",
        "url": f"s3://test-bucket/{README_OBJ_KEY}",
        "sha256": "unmatched_sha256",
        "version_id": "random_vid_for_readme",
    }

    gantry_manifest.write(f"{json.dumps(readme_file_info)}\n")
    gantry_manifest.seek(0)
    commit_json = commit_history[1]

    return gantry_manifest, commit_json


@pytest.mark.parametrize("commit_id", [None, "eb2e7242-3340-4edf-8366-90d4fce897ce"])
def test_pull_dataset(commit_id, datadir, gantry_dataset_obj, commit_history):
    """
    Test sync local data set
    1. To latest commit
    2. To a specific commit
    """
    manifest_file, commit_json = create_mock_manifest(commit_history)

    gantry_dataset_obj.dataset_name = "show_diff_dataset"

    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        setup_resp_for_sync(resp, commit_id, commit_json, manifest_file)

        commit = gantry_dataset_obj.pull(commit_id, forced=True)
        assert commit == gantry_dataset_obj._prune_commit_info(commit_json)
        with open(datadir / "show_diff_dataset/dataset_config.yaml", "r") as f:
            assert f.read() == "fake_response"

        with open(datadir / "show_diff_dataset/README.md", "r") as f:
            assert f.read() == "fake_response"

        with open(datadir / "show_diff_dataset/.dataset_metadata/HEAD") as f:
            assert json.load(f) == commit_json

        assert not list_all_files(Path(datadir / "show_diff_dataset/tabular_manifests"))
        assert not list_all_files(Path(datadir / "show_diff_dataset/artifacts"))


def test_pull_local_changes(datadir, gantry_dataset_obj):
    """
    Test trying to pull when local changes exist without forced=True
    """
    with open(datadir / "show_diff_dataset/.dataset_metadata/HEAD") as f:
        original_head = json.load(f)

    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        commit = gantry_dataset_obj.pull()

        assert commit is None

        with open(datadir / "show_diff_dataset/.dataset_metadata/HEAD") as f:
            assert original_head == json.load(f)


def test_to_jsonl():
    file_info = DatasetFileInfo(
        file_name="test_file",
        url="s3://test-bucket/key",
        version_id="version_id",
        sha256="mock_sha256",
    )
    assert (
        file_info.to_jsonl()
        == '{"file_name": "test_file", "url": "s3://test-bucket/key", "version_id": "version_id", \
"sha256": "mock_sha256"}\n'
    )


@pytest.mark.parametrize(
    ["file_name", "url", "version_id", "sha256"],
    [
        (None, "s3://test-bucket/key", "version_id", "mock_sha256"),
        ("test_file", None, "version_id", "mock_sha256"),
        ("test_file", "s3://test-bucket/key", None, "mock_sha256"),
        ("test_file", "s3://test-bucket/key", "version_id", None),
    ],
)
def test_to_jsonl_value_error(file_name, url, version_id, sha256):
    file_info = DatasetFileInfo(
        file_name=file_name,
        url=url,
        version_id=version_id,
        sha256=sha256,
    )
    with pytest.raises(ValueError):
        file_info.to_jsonl()


def test_rollback(datadir, gantry_dataset_obj, commit_history):
    """
    Test rollback to previous commit
    """
    manifest_file, _ = create_mock_manifest(commit_history)
    original_commit = commit_history[1]
    new_commit = commit_history[0]

    rollback_commit = {
        "created_at": "Wed, 05 Oct 2022 12:38:05 GMT",
        "created_by": new_commit["created_by"],
        "dataset_id": DATASET_ID,
        "id": "311851c4-88d3-474f-9e06-13380d72e508",
        "is_latest_commit": True,
        "message": f"Rollback dataset to commit: {original_commit['id']}",
        "metadata_s3_file_version": original_commit["metadata_s3_file_version"],
        "parent_commit": new_commit["id"],
    }

    # sync to local
    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        setup_resp_for_sync(resp, None, commit_history[0], manifest_file)

        gantry_dataset_obj.pull(forced=True)

    # try the rollback
    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/commits/{original_commit['id']}",
            json={
                "response": "ok",
                "data": original_commit,
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/commits",
            json={"response": "ok", "data": rollback_commit},
            headers={"Content-Type": "application/json"},
            match=[
                matchers.json_params_matcher(
                    {
                        "message": f"Rollback dataset to version: {original_commit['id']}",
                        "metadata_s3_file_version": original_commit["metadata_s3_file_version"],
                        "parent_commit_id": new_commit["id"],
                    }
                )
            ],
        )
        setup_resp_for_sync(
            resp,
            rollback_commit["id"],
            rollback_commit,
            manifest_file,
            do_fake_presigned=False,
        )

        gantry_dataset_obj.rollback(original_commit["id"], forced=True)

        with open(datadir / f"{DATASET_NAME}/.dataset_metadata/HEAD") as f:
            assert json.load(f) == rollback_commit  # verify rollback has been successful


def test_rollback_local_changes(datadir, gantry_dataset_obj):
    """
    Test trying to pull when local changes exist without forced=True
    """
    with open(datadir / "show_diff_dataset/.dataset_metadata/HEAD") as f:
        original_head = json.load(f)

    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        commit = gantry_dataset_obj.rollback("fake-uuid")

        assert commit is None

        with open(datadir / "show_diff_dataset/.dataset_metadata/HEAD") as f:
            assert original_head == json.load(f)


@pytest.mark.parametrize("function", ["push_version", "pull", "rollback"])
def test_function_on_deleted_dataset(datadir, gantry_dataset_obj, function):
    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp, is_deleted=True)

        with pytest.raises(GantryException):
            if function == "push_version":
                gantry_dataset_obj.push_version("fake commit message")
            elif function == "pull":
                gantry_dataset_obj.pull()
            elif function == "rollback":
                gantry_dataset_obj.rollback("eb2e7242-3340-4edf-8366-90d4fce897ce")


def test_delete_dataset(gantry_dataset_obj):
    with responses.RequestsMock() as resp:
        resp.add(
            resp.DELETE,
            f"{HOST}/api/v1/datasets/{DATASET_ID}",
            json={
                "response": "ok",
            },
            headers={"Content-Type": "application/json"},
        )

        gantry_dataset_obj.delete()


@patch("uuid.uuid4", return_value="test-uuid-1")
@pytest.mark.parametrize(
    ("filename", "expected_filename"),
    [
        (None, "test_file.txt"),
        ("myfile.txt", "myfile.txt"),
    ],
)
@pytest.mark.parametrize("commit_message", [None, "test commit message"])
@pytest.mark.parametrize("read_method", ["rt", "rb"])
def test_add_file(
    mock_uuid, datadir, gantry_dataset_obj, filename, expected_filename, commit_message, read_method
):
    expected_commit_message = commit_message or f"Uploaded {expected_filename} to dataset"

    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        setup_resp_for_add_file(
            resp,
            expected_commit_message,
            expected_filename,
        )

        gantry_dataset_obj.push_file(
            open(datadir / "test_file.txt", read_method), filename, commit_message
        )


@patch("uuid.uuid4", return_value="test-uuid-1")
@pytest.mark.parametrize(
    ("real_filename", "provided_filename", "expected_filename"),
    [
        ("test_file.csv", None, "test_file.csv"),
        ("test_file.csv", "mycsv.csv", "mycsv.csv"),
        ("bad_filename.txt", "mycsv.csv", "mycsv.csv"),
    ],
)
@pytest.mark.parametrize("commit_message", [None, "test commit message"])
def test_add_tabular_file(
    mock_uuid,
    gantry_dataset_obj,
    real_filename,
    provided_filename,
    expected_filename,
    commit_message,
):
    expected_commit_message = commit_message or f"Uploaded {expected_filename} to dataset"

    csvfile = StringIO()
    pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_csv(csvfile)
    csvfile.seek(0)
    csvfile.name = real_filename

    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        setup_resp_for_add_file(
            resp,
            expected_commit_message,
            expected_filename,
        )

        csvfile.seek(0)
        gantry_dataset_obj.push_tabular_file(csvfile, provided_filename, commit_message)


@pytest.mark.parametrize(
    ("real_filename", "provided_filename"),
    [
        ("bad_filename.txt", None),
        ("test_file.csv", "mybadfilename.txt"),
    ],
)
def test_add_tabular_file_bad_name(gantry_dataset_obj, real_filename, provided_filename):
    csvfile = StringIO()
    pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_csv(csvfile)
    csvfile.name = real_filename

    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)

        with pytest.raises(ValueError):
            gantry_dataset_obj.push_tabular_file(csvfile, provided_filename)


@patch("uuid.uuid4", return_value="test-uuid-1")
@pytest.mark.parametrize(
    ("filename", "expected_filename"),
    [
        (None, "dataframe-34dbe12d2b6000ce7875188f426df47d.csv"),
        ("myfile1", "myfile1.csv"),
        ("myfile2.csv", "myfile2.csv"),
    ],
)
@pytest.mark.parametrize("commit_message", [None, "test commit message"])
def test_add_dataframe(mock_uuid, gantry_dataset_obj, filename, expected_filename, commit_message):
    expected_commit_message = commit_message or f"Uploaded {expected_filename} to dataset"

    df = pd.DataFrame({"A": [100, 101], "B": [200, 202]})

    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        setup_resp_for_add_file(
            resp,
            expected_commit_message,
            expected_filename,
        )

        gantry_dataset_obj.push_dataframe(df, filename, commit_message)


@patch("uuid.uuid4", return_value="uuid-uuid-uuid")
@pytest.mark.parametrize("filename", ["", "mock_filename"])
def test_push_gantry_dataframe(mock_uuid, gantry_dataset_obj, test_api_client, filename):
    start_time = datetime.datetime.now()
    end_time = datetime.datetime.now()
    final_filename_prefixes = {
        "": f"GantryDataAutoSave__{uuid.uuid4()}_{start_time.strftime('%Y-%m-%d_%H:%M')}_to_{end_time.strftime('%Y-%m-%d_%H:%M')}",  # noqa: E501
        "mock_filename": "mock_filename",
    }
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/models/foobar/schemas",
            json={
                "response": "ok",
                "data": {"id": "app_model_node_id"},
            },
            headers={"Content-Type": "application/json"},
        )
        gantrydf = GantryDataFrame(
            api_client=test_api_client,
            application="foobar",
            version="1.2.3",
            env="pytest",
            start_time=start_time,
            end_time=end_time,
            filters=[],
        )
    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/raw_data",
            json={
                "response": "ok",
                "data": {
                    "id": "default-version-id",
                    "message": "default-message",
                    "created_at": "creation-timestamp",
                    "created_by": "gantry",
                    "is_latest_commit": True,
                },
            },
            headers={"Content-Type": "application/json"},
            match=[
                matchers.json_params_matcher(
                    {
                        "model_id": "app_model_node_id",
                        "raw_data_query_parameters": {
                            "filters": gantrydf.filters,
                            "tags": gantrydf.tags,
                            "include_join_id": True,
                            "hidden_columns": None,
                            "start_time": str(start_time.isoformat()) + "Z",
                            "end_time": str(end_time.isoformat()) + "Z",
                        },
                        "raw_data_csv_prefix": final_filename_prefixes[filename],
                    }
                )
            ],
        )
        gantry_dataset_obj.push_gantry_dataframe(gantrydf, filename)


def update_manifest_with_checksums(datadir, dataset):
    """
    Updates the gantry manifest so that there is no local dif
    """
    local_files = get_files_checksum(datadir / dataset.dataset_name)

    with open(dataset._get_file_path(DATASET_MANIFEST_FILE), "w") as gantry_manifest:
        for file_name, checksum in local_files.items():
            file_info = {
                "file_name": file_name,
                "url": f"{S3_PREFIX}/{DATASET_NAME}/{file_name}",
                "sha256": checksum,
                "version_id": "01234567-89ab-cdef-0123-456789abcdef",
            }
            gantry_manifest.write(f"{json.dumps(file_info)}\n")


def test_stash_files(gantry_dataset_obj, datadir, commit_history):
    file_content = [{"test": "json"}, {"tomato": "fruit"}, {"oh no": "my file"}]
    file_names = ["newfile.json", "modfile.json", "delfile.json"]
    modified_file_content = {"tomato": "vegetable"}

    # prepare files
    with open(datadir / f"{DATASET_NAME}/{file_names[1]}", "w+") as f:
        json.dump(file_content[1], f)
    with open(datadir / f"{DATASET_NAME}/{file_names[2]}", "w+") as f:
        json.dump(file_content[2], f)
    # set dataset diff to be none
    update_manifest_with_checksums(datadir, gantry_dataset_obj)

    # modify files
    with open(datadir / f"{DATASET_NAME}/{file_names[0]}", "w+") as f:
        json.dump(file_content[0], f)
    with open(datadir / f"{DATASET_NAME}/{file_names[1]}", "w+") as f:
        json.dump(modified_file_content, f)
    os.remove(datadir / f"{DATASET_NAME}/{file_names[2]}")

    # check that pull fails
    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        assert gantry_dataset_obj.pull() is None

    # stash
    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/datasets/{gantry_dataset_obj._dataset_id}/presign/getobject",
            json={
                "response": "ok",
                "data": {
                    f"datasets/v1/{DATASET_NAME}/{file_names[1]}": f"{HOST}/file1",
                    f"datasets/v1/{DATASET_NAME}/{file_names[2]}": f"{HOST}/file2",
                },
            },
            headers={"Content-Type": "application/json"},
        )

        # adding responses for the fake download urls
        req_kwargs = {
            "stream": True,
        }
        resp.add(
            resp.GET,
            f"{HOST}/file1",
            body=json.dumps(file_content[1]),
            match=[matchers.request_kwargs_matcher(req_kwargs)],
        )
        resp.add(
            resp.GET,
            f"{HOST}/file2",
            body=json.dumps(file_content[2]),
            match=[matchers.request_kwargs_matcher(req_kwargs)],
        )

        gantry_dataset_obj.stash()

    # check that stash was successful
    # check that relevant files are stashed
    with open(datadir / f"{DATASET_NAME}/{STASH_FOLDER}/{file_names[0]}") as f:
        assert json.load(f) == file_content[0]
    with open(datadir / f"{DATASET_NAME}/{STASH_FOLDER}/{file_names[1]}") as f:
        assert json.load(f) == modified_file_content
    # check that the stash file is updated
    with open(datadir / f"{DATASET_NAME}/{DATASET_STASH_FILE}") as f:
        assert json.load(f) == {
            DELETED_FILES: [file_names[2]],
            MODIFIED_FILES: [file_names[1]],
            NEW_FILES: [file_names[0]],
        }
    # check that the local files are in the correct state
    assert not os.path.exists(datadir / f"{DATASET_NAME}/{file_names[0]}")
    for i in [1, 2]:
        with open(datadir / f"{DATASET_NAME}/{file_names[i]}") as f:
            assert json.load(f) == file_content[i]

    # check that pull now succeeds
    manifest_file, commit_json = create_mock_manifest(commit_history)
    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        setup_resp_for_sync(resp, None, commit_json, manifest_file)
        assert gantry_dataset_obj.pull() == gantry_dataset_obj._prune_commit_info(commit_json)

    # add back file 2 since pulling deletes it
    with open(datadir / f"{DATASET_NAME}/{file_names[2]}", "w+") as f:
        json.dump(file_content[2], f)

    # retrieve stash
    gantry_dataset_obj.restore()

    # check that restore was successful
    # check that local files are in the correct state
    with open(datadir / f"{DATASET_NAME}/{file_names[0]}") as f:
        assert json.load(f) == file_content[0]
    with open(datadir / f"{DATASET_NAME}/{file_names[1]}") as f:
        assert json.load(f) == modified_file_content
    assert not os.path.exists(datadir / f"{DATASET_NAME}/{file_names[2]}")
    # check stash files are gone
    assert not os.path.exists(datadir / f"{DATASET_NAME}/{DATASET_STASH_FILE}")
    for i in [0, 1, 2]:
        assert not os.path.exists(datadir / f"{DATASET_NAME}/{STASH_FOLDER}/{file_names[i]}")


def test_double_stash(gantry_dataset_obj, datadir):
    file_content = [{"test": "json"}, {"test": "different json"}]
    file_names = ["newfile.json", "otherfile.json"]

    # set dataset diff to be none
    update_manifest_with_checksums(datadir, gantry_dataset_obj)

    # modify files and stash
    with open(datadir / f"{DATASET_NAME}/{file_names[0]}", "w+") as f:
        json.dump(file_content[0], f)
    gantry_dataset_obj.stash()

    # check that stash was successful
    with open(datadir / f"{DATASET_NAME}/{STASH_FOLDER}/{file_names[0]}") as f:
        assert json.load(f) == file_content[0]
    with open(datadir / f"{DATASET_NAME}/{DATASET_STASH_FILE}") as f:
        assert json.load(f) == {NEW_FILES: [file_names[0]], MODIFIED_FILES: [], DELETED_FILES: []}
    assert not os.path.exists(datadir / f"{DATASET_NAME}/{file_names[0]}")

    # modify files and stash again
    with open(datadir / f"{DATASET_NAME}/{file_names[1]}", "w+") as f:
        json.dump(file_content[1], f)
    gantry_dataset_obj.stash()

    # check that stash was again successful
    with open(datadir / f"{DATASET_NAME}/{STASH_FOLDER}/{file_names[1]}") as f:
        assert json.load(f) == file_content[1]
    with open(datadir / f"{DATASET_NAME}/{DATASET_STASH_FILE}") as f:
        assert json.load(f) == {NEW_FILES: [file_names[1]], MODIFIED_FILES: [], DELETED_FILES: []}
    assert not os.path.exists(datadir / f"{DATASET_NAME}/{file_names[1]}")


def test_load_nonexistent_stash(gantry_dataset_obj, caplog):
    with caplog.at_level(logging.WARNING):
        gantry_dataset_obj.restore()
    assert "No stashed files were found!" in caplog.text


@pytest.mark.parametrize(("function"), [("push_file"), ("push_tabular_file"), ("push_dataframe")])
def test_add_item_bad_parent(gantry_dataset_obj, function, commit_history):
    parent_commit_id = uuid.UUID("01234567-89ab-cdef-0123-456789abcdef")

    if function == "push_dataframe":
        input = pd.DataFrame()
    else:
        input = StringIO()
        input.name = "file.csv"

    with pytest.raises(DatasetHeadOutOfDateException):
        with responses.RequestsMock() as resp:
            setup_resp_for_deleted_check(resp)
            resp.add(
                resp.GET,
                f"{HOST}/api/v1/datasets/{DATASET_ID}/commits",
                json={
                    "response": "ok",
                    "data": commit_history,
                },
                headers={"Content-Type": "application/json"},
            )

            if function == "push_file":
                gantry_dataset_obj.push_file(input, parent_version_id=parent_commit_id)
            elif function == "push_tabular_file":
                gantry_dataset_obj.push_tabular_file(input, parent_version_id=parent_commit_id)
            elif function == "push_dataframe":
                gantry_dataset_obj.push_dataframe(input, parent_version_id=parent_commit_id)


@patch("uuid.uuid4", return_value="test-uuid-1")
@pytest.mark.parametrize(("function"), [("push_file"), ("push_tabular_file"), ("push_dataframe")])
def test_add_item_good_parent(mock_uuid, gantry_dataset_obj, function, commit_history):
    parent_commit_id = commit_history[0]["id"]
    filename = "test-file.csv"

    if function == "push_dataframe":
        input = pd.DataFrame()
    else:
        input = StringIO()
        input.name = filename

    with responses.RequestsMock() as resp:
        setup_resp_for_deleted_check(resp)
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/datasets/{DATASET_ID}/commits",
            json={
                "response": "ok",
                "data": commit_history,
            },
            headers={"Content-Type": "application/json"},
        )
        setup_resp_for_add_file(
            resp, f"Uploaded {filename} to dataset", filename, parent_commit_id=parent_commit_id
        )

        if function == "push_file":
            new_commit = gantry_dataset_obj.push_file(
                input, filename=filename, parent_version_id=parent_commit_id
            )
        elif function == "push_tabular_file":
            new_commit = gantry_dataset_obj.push_tabular_file(
                input, filename=filename, parent_version_id=parent_commit_id
            )
        elif function == "push_dataframe":
            new_commit = gantry_dataset_obj.push_dataframe(
                input, filename=filename, parent_version_id=parent_commit_id
            )

        assert new_commit["version_id"] == "add-file-commit-id"
        assert new_commit["dataset"] == gantry_dataset_obj.dataset_name
        assert new_commit["message"] == f"Uploaded {filename} to dataset"

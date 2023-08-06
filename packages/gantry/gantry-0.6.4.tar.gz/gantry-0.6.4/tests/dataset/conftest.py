import pytest

HOST = "https://test-api"
DATASET_NAME = "show_diff_dataset"
USER_EMAIL = "test@gantry.dev"
DATASET_ID = "77494dac-be4d-4c55-81bd-b16cf19f1297"
BUCKET_NAME = "test-bucket"
AWS_REGION = "us-west-2"
COMMIT_MSG = "test commit message"
MANIFEST_VERSION_ID = "mock_version_id"
S3_PREFIX = "org_id/datasets/v1"
CONF_OBJ_KEY = f"{S3_PREFIX}/{DATASET_NAME}/test-uuid-1/dataset_config.yaml"
README_OBJ_KEY = f"{S3_PREFIX}/{DATASET_NAME}/test-uuid-1/README.md"
IMG_OBJ_KEY = f"{S3_PREFIX}/{DATASET_NAME}/test-uuid-1/artifacts/kitten.png"
CSV_OBJ_KEY = f"{S3_PREFIX}/{DATASET_NAME}/test-uuid-1/tabular_manifests/feedback.csv"
MANIFEST_OBJ_KEY = f"{S3_PREFIX}/{DATASET_NAME}/.dataset_metadata/.gantry_manifest.jsonl"


@pytest.fixture(scope="function")
def test_dataset():
    return {
        "id": DATASET_ID,
        "name": DATASET_NAME,
        "organization_id": "org_id",
        "created_at": "Tue, 04 Oct 2022 22:15:25 GMT",
        "bucket_name": BUCKET_NAME,
        "aws_region": AWS_REGION,
        "s3_prefix": S3_PREFIX,
        "disabled": False,
    }


@pytest.fixture(scope="function")
def commit_history():
    return [
        {
            "created_at": "Wed, 05 Oct 2022 05:42:13 GMT",
            "created_by": "db459d6d-c83b-496d-b659-e48bca971156",
            "dataset_id": DATASET_ID,
            "id": "8ee0f6d5-c84c-473a-931a-5148b2e704d7",
            "is_latest_commit": True,
            "message": COMMIT_MSG,
            "metadata_s3_file_version": MANIFEST_VERSION_ID,
            "parent_commit": "eb2e7242-3340-4edf-8366-90d4fce897ce",
        },
        {
            "created_at": "Tue, 04 Oct 2022 22:15:25 GMT",
            "created_by": "db459d6d-c83b-496d-b659-e48bca971156",
            "dataset_id": DATASET_ID,
            "id": "eb2e7242-3340-4edf-8366-90d4fce897ce",
            "is_latest_commit": False,
            "message": "initial dataset commit",
            "metadata_s3_file_version": "PHHV3BI3euX_LbOiV5EjAouxHuX3ZBFh",
            "parent_commit": None,
        },
    ]

import concurrent
import contextlib
import csv
import functools
import hashlib
import io
import json
import logging
import os
import re
import shutil
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass
from keyword import iskeyword
from pathlib import Path
from typing import IO, Any, Callable, Dict, List, Optional, Union

import datasets
import jinja2
import pandas as pd
import requests
import yaml
from typeguard import typechecked

from gantry.api_client import APIClient
from gantry.dataset import constants
from gantry.exceptions import (
    DataSchemaMismatchError,
    DatasetCommitNotFoundError,
    DatasetDeletedException,
    DatasetHeadOutOfDateException,
    DatasetNotFoundError,
    GantryRequestException,
    NoTabularDataError,
)
from gantry.query.core.dataframe import GantryDataFrame
from gantry.utils import (
    _download_file_to_IO,
    _upload_file_from_IO,
    download_file_from_url,
    get_files_checksum,
    get_s3_sha256_checksum,
    list_all_files,
    parse_s3_path,
    read_lines_from_url,
    upload_file_to_url,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 5


def _ensure_not_deleted(func: Callable) -> Callable:
    """
    Decorator to ensure we do not perform an operation on a deleted dataset, and instead warn the
    user that the dataset is deleted.
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        resp = self._api_client.request(
            "GET",
            f"/api/v1/datasets/{self.dataset_name}",
            raise_for_status=True,
        )
        dataset_info = resp["data"]

        if dataset_info["disabled"]:
            raise DatasetDeletedException("This dataset has been deleted!")

        return func(self, *args, **kwargs)

    return wrapper


def _ensure_dataset_exists_locally(func: Callable) -> Callable:
    """
    Decorator to ensure dataset exists locally, if not will warn the user to download the dataset.
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not Path(self._get_file_path(constants.DATASET_MANIFEST_FILE)).exists():
            raise DatasetNotFoundError(
                f"Can't find dataset {self.dataset_name} locally, please run pull()"
                f"to download the dataset into your local workspace."
            )

        return func(self, *args, **kwargs)

    return wrapper


def _warn_when_local_changes(func: Callable) -> Callable:
    """
    Decorator to ensure there are no local changes in the dataset. If there are, will return None
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # only do the following checking when HEAD file exist(dataset exists on local host)
        if os.path.exists(self._get_file_path(constants.DATASET_HEAD_FILE)):
            localdiff = self.get_diff()
            if (
                localdiff[constants.DELETED_FILES]
                or localdiff[constants.MODIFIED_FILES]
                or localdiff[constants.NEW_FILES]
            ) and not kwargs.get("forced", False):
                logger.warning(
                    "Local changes detected! Please run stash() to stash your local changes, "
                    "or run this function again with forced=True"
                )
                return None

        return func(self, *args, **kwargs)

    return wrapper


@dataclass
class DatasetFileInfo:
    file_name: str
    url: str
    version_id: Optional[str] = None
    sha256: Optional[str] = None

    def to_jsonl(self):
        if not self.file_name or not self.url or not self.version_id or not self.sha256:
            raise ValueError(
                f"Failed to create file info jsonl: {json.dumps(asdict(self))}. \
                    Incomplete dataset file info line! "
            )

        return f"{json.dumps(asdict(self))}\n"


class GantryDataset:
    """
    A class representing a lightweight container around your data that
    provides simple version control semantics for helping to make ML
    pipelines reproducible.
    """

    def __init__(
        self,
        api_client: APIClient,
        dataset_name: str,
        dataset_id: uuid.UUID,
        bucket_name: str,
        aws_region: str,
        dataset_s3_prefix: str,
        workspace: str,
    ):
        """
        :meta private:
        """
        self.dataset_name = dataset_name
        self.workspace = workspace
        self._api_client = api_client
        self._dataset_id = dataset_id
        self._bucket_name = bucket_name
        self._dataset_s3_prefix = dataset_s3_prefix
        self._aws_region = aws_region

    def list_versions(self) -> List[Dict[str, Any]]:
        """
        This method will list all the versions of the dataset. Each dataset version is a snapshot
        of the dataset at a particular point in time. The result will be sorted from latest
        to earliest.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            >>> dataset.list_versions()
            [{'version_id': '7f100fca-f080-4daf-82d1-575e34234930',
              'dataset': 'dataset_name',
              'message': 'version notes',
              'created_at': 'Thu, 16 Feb 2023 00:16:33 GMT',
              'created_by': '04c894c7-a853-4fec-a024-66f5aae07b06',
              'is_latest_version': True},
             {'version_id': '300cdb42-a8c9-4b6e-a16d-4f6c925eb25d',
              'dataset': 'dataset_name',
              'message': 'version notes',
              'created_at': 'Thu, 16 Feb 2023 00:16:18 GMT',
              'created_by': '04c894c7-a853-4fec-a024-66f5aae07b06',
              'is_latest_version': False},
             {'version_id': '51e7771d-5ba9-4bdf-ab61-6d6ec9f7e066',
              'dataset': 'dataset_name',
              'message': 'initial dataset commit',
              'created_at': 'Thu, 16 Feb 2023 00:14:34 GMT',
              'created_by': '04c894c7-a853-4fec-a024-66f5aae07b06',
              'is_latest_version': False}]

        Returns:
            ``List[Dict[str, Any]]``: dataset versions from latest to earliest.
        """
        response = self._api_client.request(
            "GET", f"/api/v1/datasets/{self._dataset_id}/commits", raise_for_status=True
        )
        return [self._prune_commit_info(commit_info) for commit_info in response["data"]]

    @typechecked
    @_ensure_not_deleted
    @_warn_when_local_changes
    def pull(
        self, version_id: Optional[Union[str, uuid.UUID]] = None, forced: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Pull a spicific version of the dataset from dataset server to local working directory.

        If version ID is provided, this method will pull the specific snapshot of your dataset
        based on the version id to working directory. If version ID is not provided, this method
        will pull the latest version. If forced is set to True, any local changes will be discarded.
        This method will only change the files in your local dataset folder, pull an older version
        will not affect the version history.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            # pull the latest version of your dataset
            >>> dataset.pull()
            # pull a specific version of your dataset
            >>> dataset.pull("b787034a-798b-4bb3-a726-0e197ddb8aff")


        Args:
            version_id (str, optional): target version ID, defaults to ``None`` which will pull the
                latest version.
            forced (bool): whether to discard local changes or not when pulling,
                defaults to ``False``.

        Returns:
            Optional[Dict[str, Any]]: A dictionary with metadata representing the versioned rolled
            back to if successful, ``None`` otherwise.
        """
        target_commit = (
            self._get_commit(commit_id=version_id) if version_id else self._get_latest_commit()
        )

        metadata_version_id = target_commit[constants.METADATA_S3_FILE_VERSION]

        self._download_files(
            [
                DatasetFileInfo(
                    file_name=constants.DATASET_MANIFEST_FILE,
                    url=self._get_s3_url(constants.DATASET_MANIFEST_FILE),
                    version_id=metadata_version_id,
                )
            ]
        )

        diff = self._get_diff_for_pull()
        self._download_files(diff[constants.MODIFIED_FILES])  # Overwrite modified files
        self._download_files(diff[constants.DELETED_FILES])  # redownload deleted files

        # delete new added files
        for f in diff[constants.NEW_FILES]:
            os.remove(self._get_file_path(f.file_name))

        self._update_head(target_commit)
        if not os.path.exists(self._get_file_path(constants.STASH_FOLDER)):
            os.mkdir(self._get_file_path(constants.STASH_FOLDER))

        # Create the tabular_manifests and artifact folder
        (Path(self.workspace) / self.dataset_name / constants.TABULAR_MANIFESTS).resolve().mkdir(
            parents=True, exist_ok=True
        )

        (Path(self.workspace) / self.dataset_name / constants.ARTIFACTS).resolve().mkdir(
            parents=True, exist_ok=True
        )

        return self._prune_commit_info(target_commit)

    @_ensure_dataset_exists_locally
    def get_diff(self) -> Dict[str, List[str]]:
        """
        Show the local changes that have not been pushed to the server yet. This method will return
        a dictionary with three keys: ``new_files``, ``modified_files``, and ``deleted_files``.
        Each key will have a list of files that have been added, modified, or deleted respectively.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            >>> dataset.pull()
            # make some changes to the dataset
            >>> dataset.get_diff()
            {'new_files': ['tabular_manifests/new_file.csv', 'artifacts/image.png'],
             'modified_files': ['tabular_manifests/modified_file_1.csv'],
             'deleted_files': ['tabular_manifests/deleted_file.csv']}

        Returns:
            ``dict``: a dictionary representing the diff, which looks like this:

            .. code-block:: json

                {
                    "new_files": List[str],
                    "modified_files": List[str],
                    "deleted_files": List[str],
                }
        """

        diff = self._get_diff()
        return {
            constants.NEW_FILES: [f for f, _ in diff[constants.NEW_FILES]],
            constants.MODIFIED_FILES: [f for f, _ in diff[constants.MODIFIED_FILES]],
            constants.DELETED_FILES: [f for f, _ in diff[constants.DELETED_FILES]],
        }

    @typechecked
    @_ensure_dataset_exists_locally
    @_ensure_not_deleted
    def push_version(self, message: str) -> Dict[str, Any]:
        """
        This method will create a new dataset version in the remote server with a version
        message. The new version will include all the local changes that have not been pushed.
        If there are no local changes, this method will return the current version.

        To avoid race conditions, this method will check that the HEAD of the dataset is up to date.
        If the HEAD is not up to date, this method will raise a ``DatasetHeadOutOfDateException``.
        In that case you could stash your local change and pull the latest version of the dataset
        and try again. Check out the documents for ``stash()``, ``pull()`` and ``restore()`` for
        more details.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            >>> dataset.pull()
            # make some changes to the dataset
            >>> dataset.get_diff()
            {'new_files': ['tabular_manifests/new_file.csv', 'artifacts/image.png'],
            'modified_files': ['tabular_manifests/modified_file_1.csv'],
            'deleted_files': ['tabular_manifests/deleted_file.csv']}
            >>> dataset.push_version("new version notes")
            {'version_id': '09575ee7-0407-44b8-ae88-765a8270b17a',
            'dataset': 'dataset_name',
            'message': 'new version notes',
            'created_at': 'Wed, 15 Feb 2023 22:17:55 GMT',
            'created_by': '04c894c7-a853-4fec-a024-66f5aae07b06',
            'is_latest_version': True}
            # After pushing the changes, the diff should be empty
            >>> dataset.get_diff()
            {'new_files':[],
            'modified_files':[],
            'deleted_files':[]}


        Args:
            message (str): a non-empty string representing a message to associate with
                the created version.
        Returns:
            ``Dict[str, Any]``: a dictionary with metadata representing the version created.
        """
        commit_id = uuid.uuid4()
        diff = self._get_diff_for_commit(commit_id)

        if (
            not diff[constants.NEW_FILES]
            and not diff[constants.MODIFIED_FILES]
            and not diff[constants.DELETED_FILES]
        ):
            logger.warning("No local changes to add!")
            return self._get_current_commit()

        # Check that HEAD is up to date
        resp = self._api_client.request(
            "GET", f"/api/v1/datasets/{self._dataset_id}/commits", raise_for_status=True
        )
        latest_commit_id = resp["data"][0]["id"]

        with open(self._get_file_path(constants.DATASET_HEAD_FILE), "r") as f:
            current_commit = json.load(f)

            if current_commit["id"] != latest_commit_id:
                raise DatasetHeadOutOfDateException

        diff[constants.NEW_FILES] = self._upload_files(diff[constants.NEW_FILES])
        diff[constants.MODIFIED_FILES] = self._upload_files(diff[constants.MODIFIED_FILES])

        self._backup_file(constants.DATASET_MANIFEST_FILE)
        self._update_manifest_file(diff)

        result = self._upload_files(
            [
                DatasetFileInfo(
                    file_name=constants.DATASET_MANIFEST_FILE,
                    url=self._get_s3_url(constants.DATASET_MANIFEST_FILE),
                )
            ]
        )
        version_id = result[0].version_id
        try:
            resp = self._api_client.request(
                "POST",
                f"/api/v1/datasets/{self._dataset_id}/commits",
                json={
                    "message": message,
                    "metadata_s3_file_version": version_id,
                    "parent_commit_id": self._get_current_commit()["id"],
                    "commit_id": commit_id,
                },
                raise_for_status=True,
            )
            os.remove(
                self._get_file_path(f"{constants.DATASET_MANIFEST_FILE}{constants.BACKUP_SUFFIX}")
            )
        except GantryRequestException as e:
            self._recover_file(constants.DATASET_MANIFEST_FILE)
            if (
                e.status_code == 400
                and 'Details: {"error":"Parent version out of date!","response":"error"}'
                in e.args[0]
            ):
                raise DatasetHeadOutOfDateException
            raise e

        commit_info = resp["data"]
        self._update_head(commit_info)

        return self._prune_commit_info(commit_info)

    def push_gantry_dataframe(self, gantrydf: GantryDataFrame, filename: str = ""):
        """
        This method will take a GantryDataFrame as input, and save its contents to a new file in
        your dataset's ``tabular_manifests`` folder, and create a new version. Note that all these
        operations happen in the remote server, if you have your dataset checked out locally,
        please make sure you call ``pull()`` after this operation to get the latest data.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            >>> dataset.pull()
            >>> os.listdir(workspace + dataset_name)
            ['.dataset_metadata', 'dataset_config.yaml', 'README.md', 'tabular_manifests']
            >>> os.listdir(workspace + dataset_name + '/tabular_manifests')
            []
            >>> gantrydf = gquery.query(
            ...   application=application,
            ...   start_time=start,
            ...   end_time=end,
            ...   version="1.1",
            ... )
            >>>
            >>> _ = dataset.push_gantry_dataframe(gantrydf)
            >>>
            >>> _ = dataset.pull()
            >>> os.listdir(workspace + dataset_name + '/tabular_manifests')
            ['GantryDataAutoSave__4390b343-b802-4add-ab51-f86e53979c73_2023-02-13_12:09_to_2023-02-13_17:09_rows_0_69.csv']

        Args:
            gantrydf (GantryDataFrame): the GantryDataFrame that needs to be added to the dataset.
            filename (str): the name to be given to the file with data from the GantryDataFrame.
        Returns:
            Latest commit info.
        """
        start_time = gantrydf.query_info.start_time
        end_time = gantrydf.query_info.end_time
        final_filename = filename
        if filename == "":
            final_filename = f"GantryDataAutoSave__{uuid.uuid4()}_{start_time.strftime('%Y-%m-%d_%H:%M')}_to_{end_time.strftime('%Y-%m-%d_%H:%M')}"  # noqa: E501
        app_node_id = gantrydf.query_info.application_node_id
        filters = gantrydf.filters
        tags = gantrydf.tags
        resp = self._api_client.request(
            "POST",
            f"/api/v1/datasets/{self._dataset_id}/raw_data",
            json={
                "model_id": app_node_id,
                "raw_data_query_parameters": {
                    "filters": filters,
                    "tags": tags,
                    "include_join_id": True,
                    "hidden_columns": None,
                    "start_time": start_time,
                    "end_time": end_time,
                },
                "raw_data_csv_prefix": final_filename,
            },
            raise_for_status=True,
        )
        commit_info = resp["data"]
        return self._prune_commit_info(commit_info)

    @typechecked
    @_ensure_not_deleted
    def push_file(
        self,
        file: IO,
        filename: Optional[str] = None,
        message: Optional[str] = None,
        parent_version_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> Dict[str, Any]:
        """
        This method will add a new file to the dataset in Gantry server and create a new version of
        the dataset. With this method you can easily add new files to the dataset without having to
        pull the dataset locally. If you have your dataset checked out locally, please make sure you
        call ``pull()`` after this operation to get the latest data. The difference between this
        method and ``push_tabular_file()`` is that this method can handle both tabular and
        non-tabular files. If you are uploading a tabular file, please use ``push_tabular_file()``
        instead.


        Args:
            file (IO): the file to be uploaded
            filename (str, Optional): the name of the file to be uploaded. Defaults to the
                name of the file passed in the ``file`` parameter.
            message (str, Optional): the version message that will be associated with the
                upload of the file. Defaults to a generic message if not set
            parent_version_id (uuid.UUID, Optional): If specified, SDK will check whether you are
                making changes on top of the latest version, if not the operation will fail.

        Returns:
            ``Dict[str, Any]``: A dictionary with metadata representing the version created.
        """
        if filename:
            name = filename
        else:
            name = os.path.basename(file.name)

        return self._add_single_file(file, name, message, parent_version_id)

    @typechecked
    @_ensure_not_deleted
    def push_tabular_file(
        self,
        file: IO,
        filename: Optional[str] = None,
        message: Optional[str] = None,
        parent_version_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> Dict[str, Any]:
        """
        This method will add a tabular file to the dataset's ``tabular_manifests`` folder and create
        a new version of the dataset on dataset server. With this method you can easily add new
        tabular files to an existing dataset without having to pull the dataset locally. If you
        have your dataset checked out locally, please make sure you call ``pull()`` after this
        operation to get the latest data. If you are trying to add a non-tabular file, please
        use ``push_file()`` instead. Note: the tabular filename must be postfixed with ``.csv``.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            >>> dataset.push_tabular_file(
            ...     open("{file_to_be_added}.csv"),
            ...     "{dataset_file_name}.csv",
            ...     "version info"
            ...    )
            {'version_id': '2b575ee7-0407-44b8-ae88-765a8270b17a',
            'dataset': 'dataset_name',
            'message': 'version info',
            'created_at': 'Wed, 15 Feb 2023 22:17:55 GMT',
            'created_by': '04c894c7-a853-4fec-a024-66f5aae07b06',
            'is_latest_version': True}

        Args:
            file (IO): the csv file to be uploaded
            filename (str, Optional): the name of the file to be uploaded. Defaults to the local
                file name of the file. Name must end with ``.csv``.
            message (str, optional): the version message that will be associated with the
                upload of the file. Defaults to a generic message if not set
            parent_version_id (uuid.UUID, optional): If specified, SDK will check whether you are
                making changes on top of the latest version, if not the operation will fail.

        Returns:
            ``Dict[str, Any]``: A dictionary with metadata representing the version created.
        """
        if filename:
            name = filename
        else:
            name = os.path.basename(file.name)

        if name[-4:] != constants.CSV_SUFFIX:
            raise ValueError(f"filename must end with '.csv'! Got filename: {name}")

        return self._add_single_file(file, name, message, parent_version_id)

    @typechecked
    @_ensure_not_deleted
    def push_dataframe(
        self,
        dataframe: pd.DataFrame,
        filename: Optional[str] = None,
        message: Optional[str] = None,
        parent_version_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> Dict[str, Any]:
        """
        Add a dataframe to the dataset's ``tabular_manifests`` folder as a csv file and create a new
        version of the dataset on the dataset server. With this method you can easily add new a
        dataframe to an existing dataset without having to pull the dataset locally. If you have
        your dataset checked out locally, please make sure you call ``pull()`` after this operation.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            >>> dataset.push_dataframe(
            ...     pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]}),
            ...     "dataframe.csv",
            ...     "version info"
            ... )
            {'version_id': 'fa575ee7-0407-44b8-ae88-765a8270b17a',
            'dataset': 'dataset_name',
            'message': 'version info',
            'created_at': 'Wed, 15 Feb 2023 22:17:55 GMT',
            'created_by': '04c894c7-a853-4fec-a024-66f5aae07b06',
            'is_latest_version': True}

        Args:
            dataframe (pd.DataFrame): the dataframe to be uploaded
            filename (str, Optional): the name for the csv that will be uploaded. Defaults to
                dataframe-<random-hash>.csv
            message (str, Optional): the version message that will be associated with the
                upload of the file. Defaults to a generic message if not set
            parent_version_id (uuid.UUID, Optional): If specified, SDK will check whether you are
                making changes on top of the latest version, if not the operation will fail.

        Returns:
            ``Dict[str, Any]``: A dictionary with metadata representing the version created.
        """
        if filename:
            if filename[-4:] == constants.CSV_SUFFIX:
                name = filename
            else:
                name = f"{filename}{constants.CSV_SUFFIX}"
        else:
            hash = hashlib.md5(pd.util.hash_pandas_object(dataframe).values).hexdigest()
            name = f"dataframe-{hash}{constants.CSV_SUFFIX}"

        file = io.StringIO()
        dataframe.to_csv(file, index=False)
        file.seek(0)

        return self._add_single_file(file, name, message, parent_version_id)

    @typechecked
    @_ensure_not_deleted
    @_warn_when_local_changes
    def rollback(
        self, version_id: Union[str, uuid.UUID], forced: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Rollback the dataset data to a previous version and create a new dataset version based on
        the target version id. With this method you can easily rollback to any previous version of
        your dataset and continue working on top of it. Note that to do this, you must have your
        local dataset folder up to date. Also this method will automatically pull the latest version
        to local dataset folder after the rollback. If forced is set to True, any local changes
        will be discarded.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            >>> dataset.pull()
            >>> dataset.list_versions()
            [{'version_id': 'd6f42bd0-b7a9-4089-88fb-be7cee6d4a83',
            'dataset': 'dataset_name',
            'message': 'version info',
            'created_at': 'Wed, 08 Feb 2023 22:02:02 GMT',
            'created_by': 'db459d6d-c83b-496d-b659-e48bca971156',
            'is_latest_version': True},
            {'version_id': 'b787034a-798b-4bb3-a726-0e197ddb8aff',
            'dataset': 'dataset_name',
            'message': 'initial dataset commit',
            'created_at': 'Wed, 08 Feb 2023 22:00:26 GMT',
            'created_by': 'db459d6d-c83b-496d-b659-e48bca971156',
            'is_latest_version': False}]
            >>> dataset.rollback("b787034a-798b-4bb3-a726-0e197ddb8aff")
            {'version_id': '23bc4d35-0df2-424c-9156-d5ca105eb4c1',
            'dataset': 'dataset_name',
            'message': 'Rollback dataset to version: b787034a-798b-4bb3-a726-0e197ddb8aff',
            'created_at': 'Thu, 09 Feb 2023 00:36:07 GMT',
            'created_by': 'db459d6d-c83b-496d-b659-e48bca971156',
            'is_latest_version': True}
            >>> dataset.list_versions()
            [{'version_id': '23bc4d35-0df2-424c-9156-d5ca105eb4c1',
            'dataset': 'dataset_name',
            'message': 'Rollback dataset to version: b787034a-798b-4bb3-a726-0e197ddb8aff',
            'created_at': 'Thu, 09 Feb 2023 00:36:07 GMT',
            'created_by': 'db459d6d-c83b-496d-b659-e48bca971156',
            'is_latest_version': True},
            {'version_id': 'd6f42bd0-b7a9-4089-88fb-be7cee6d4a83',
            'dataset': 'dataset_name',
            'message': 'version info',
            'created_at': 'Wed, 08 Feb 2023 22:02:02 GMT',
            'created_by': 'db459d6d-c83b-496d-b659-e48bca971156',
            'is_latest_version': False},
            {'version_id': 'b787034a-798b-4bb3-a726-0e197ddb8aff',
            'dataset': 'dataset_name',
            'message': 'initial dataset commit',
            'created_at': 'Wed, 08 Feb 2023 22:00:26 GMT',
            'created_by': 'db459d6d-c83b-496d-b659-e48bca971156',
            'is_latest_version': False}]

        Args:
            version_id (str): ID of the version to rollback to.
            forced (bool): whether to discard local changes when rolling back.

        Returns:
            Optional[Dict[str, Any]]: A dictionary with metadata representing the versioned
            rolled back to if successful, ``None`` otherwise.
        """
        target_commit = self._get_commit(version_id)

        resp = self._api_client.request(
            "POST",
            f"/api/v1/datasets/{self._dataset_id}/commits",
            json={
                "message": f"Rollback dataset to version: {target_commit['id']}",
                "metadata_s3_file_version": target_commit["metadata_s3_file_version"],
                "parent_commit_id": self._get_current_commit()["id"],
            },
            raise_for_status=True,
        )

        commit_info = resp["data"]
        self.pull(commit_info["id"], forced=forced)

        return self._prune_commit_info(commit_info)

    def stash(self) -> None:
        """
        This method will stash all the changes in your local dataset folder to a temporary folder.
        You can use this method to save your changes before the ``pull()`` method. Later on you can
        use the ``restore()`` method to restore your changes. Note that if you run ``stash()``
        multiple times, the changes will be overwritten and only the latest stash will be kept.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            >>> dataset.pull()
            # make some changes to your dataset
            >>> dataset.get_diff()
            {'new_files': ['tabular_manifests/new_file.csv', 'artifacts/image.png'],
            'modified_files': ['tabular_manifests/modified_file_1.csv'],
            'deleted_files': ['tabular_manifests/deleted_file.csv']}
            >>> dataset.stash()
            >>> dataset.get_diff()
            {'new_files': [],
            'modified_files': [],
            'deleted_files': []}

        Returns:
            ``None``
        """
        # deletes existing stash
        if os.path.exists(self._get_file_path(constants.DATASET_STASH_FILE)):
            with open(self._get_file_path(constants.DATASET_STASH_FILE)) as stashfile:
                old_stash = json.load(stashfile)
            for file in old_stash[constants.MODIFIED_FILES] + old_stash[constants.NEW_FILES]:
                with contextlib.suppress(FileNotFoundError):  # file not exist is OK
                    os.remove(self._get_file_path(f"{constants.STASH_FOLDER}/{file}"))

        # creates new stash
        local_diff = self.get_diff()
        with open(self._get_file_path(constants.DATASET_STASH_FILE), "w+") as stashfile:
            json.dump(local_diff, stashfile)

        # stash files
        for file in local_diff[constants.MODIFIED_FILES]:
            self._stash_file(file)
        for file in local_diff[constants.NEW_FILES]:
            self._stash_file(file)

        # re-sync to current commit
        diff = self._get_diff_for_pull()
        logger.warning(diff)
        self._download_files(diff[constants.MODIFIED_FILES])  # overwrite modified files
        self._download_files(diff[constants.DELETED_FILES])  # redownload deleted files

        # delete new added files
        for file in diff[constants.NEW_FILES]:
            os.remove(self._get_file_path(file.file_name))

    def restore(self) -> None:
        """
        This method will restore the changes from the stash to your local dataset folder. Note that
        if you have made changes to your local dataset folder after the ``stash()`` method, those
        changes could be overwritten by this method.

        Example usage:

            >>> import gantry.dataset as gdataset
            >>> dataset = gdataset.get_dataset(dataset_name)
            >>> dataset.pull()
            # make some changes to your local dataset folder
            >>> dataset.get_diff()
            {'new_files': ['tabular_manifests/new_file.csv', 'artifacts/image.png'],
            'modified_files': ['tabular_manifests/modified_file_1.csv'],
            'deleted_files': ['tabular_manifests/deleted_file.csv']}
            >>> dataset.stash()
            >>> dataset.get_diff()
            {'new_files': [],
            'modified_files': [],
            'deleted_files': []}
            >>> dataset.restore()
            >>> dataset.get_diff()
            {'new_files': ['tabular_manifests/new_file.csv', 'artifacts/image.png'],
            'modified_files': ['tabular_manifests/modified_file_1.csv'],
            'deleted_files': ['tabular_manifests/deleted_file.csv']}

        Returns:
            ``None``
        """
        if not os.path.exists(self._get_file_path(constants.DATASET_STASH_FILE)):
            logger.warning("No stashed files were found!")
            return

        diff = {}
        with open(self._get_file_path(constants.DATASET_STASH_FILE)) as stashfile:
            diff = json.load(stashfile)
        os.remove(self._get_file_path(constants.DATASET_STASH_FILE))
        if not diff:
            return

        for file in diff[constants.MODIFIED_FILES]:
            self._restore_stash_file(file)
        for file in diff[constants.NEW_FILES]:
            self._restore_stash_file(file)
        for file in diff[constants.DELETED_FILES]:
            os.remove(self._get_file_path(file))

    def delete(self) -> None:
        """
        Mark the dataset as deleted. As for now this will only hide dataset from the list_datasets
        API results, it will not delete the dataset data from the server, we are working on
        implementing the hard delete feature.

        Returns:
            ``None``
        """
        self._api_client.request(
            "DELETE",
            f"/api/v1/datasets/{self._dataset_id}",
            raise_for_status=True,
        )
        logger.info(f"Dataset {self.dataset_name} has been deleted")
        return

    @typechecked
    def _get_commit(self, commit_id: Union[str, uuid.UUID]) -> Dict[str, Any]:
        """
        Get commit details

        Args:
            commit_id (str): commit id
        Returns:
            Commit information
        """
        try:
            resp = self._api_client.request(
                "GET",
                f"/api/v1/datasets/{self._dataset_id}/commits/{commit_id}",
                raise_for_status=True,
            )
        except GantryRequestException as e:
            if e.status_code == 404:
                raise DatasetCommitNotFoundError(
                    f"Could not find dataset commit with id {commit_id}"
                ) from e
            raise
        return resp["data"]

    def _get_latest_commit(self) -> Dict[str, Any]:
        """
        Get latest commit details

        Returns:
            Commit information
        """
        resp = self._api_client.request(
            "GET", f"/api/v1/datasets/{self._dataset_id}/commits", raise_for_status=True
        )
        return resp["data"][0]  # return latest commit

    def _update_manifest_file(self, diff: Dict[str, List[DatasetFileInfo]]):
        new_files = {f.file_name: f for f in diff[constants.NEW_FILES]}
        modified_files = {f.file_name: f for f in diff[constants.MODIFIED_FILES]}
        deleted_files = {f.file_name: f for f in diff[constants.DELETED_FILES]}

        with open(
            self._get_file_path(f"{constants.DATASET_MANIFEST_FILE}{constants.NEW_SUFFIX}"), "w"
        ) as new_gantry_manifest:
            with open(
                self._get_file_path(constants.DATASET_MANIFEST_FILE), "r"
            ) as cur_gantry_manifest:
                for line in cur_gantry_manifest:
                    cur_file_info = json.loads(line)
                    cur_file_name = cur_file_info[constants.FILE_NAME]

                    if cur_file_name in modified_files:  # update modified files
                        new_gantry_manifest.write(modified_files[cur_file_name].to_jsonl())
                    elif cur_file_name in deleted_files:  # remove deleted files
                        continue
                    else:  # keep unchanged files
                        new_gantry_manifest.write(line)

            for _, file_info in new_files.items():
                new_gantry_manifest.write(file_info.to_jsonl())  # add new added files

        os.replace(
            self._get_file_path(f"{constants.DATASET_MANIFEST_FILE}{constants.NEW_SUFFIX}"),
            self._get_file_path(constants.DATASET_MANIFEST_FILE),
        )

    def _get_diff_for_commit(self, commit_id: uuid.UUID):
        repo_diff = self._get_diff()
        commit_diff = {}

        # generate new url for new files
        commit_diff[constants.NEW_FILES] = [
            DatasetFileInfo(
                file_name=file_name,
                url=self._get_s3_url(file_name, commit_id),
                sha256=checksum,
            )
            for file_name, checksum in repo_diff[constants.NEW_FILES]
        ]
        # generate new url for modified files
        commit_diff[constants.MODIFIED_FILES] = [
            DatasetFileInfo(
                file_name=file_name,
                url=self._get_s3_url(file_name, commit_id),
                sha256=checksum,
            )
            for file_name, checksum in repo_diff[constants.MODIFIED_FILES]
        ]
        # don't need url for deleted files
        commit_diff[constants.DELETED_FILES] = [
            DatasetFileInfo(
                file_name=file_name,
                url="",
                sha256=checksum,
            )
            for file_name, checksum in repo_diff[constants.DELETED_FILES]
        ]

        return commit_diff

    def _get_diff_for_pull(self):
        repo_diff = self._get_diff()
        sync_diff = {}

        commit_snapshot = {}
        with open(self._get_file_path(constants.DATASET_MANIFEST_FILE)) as cur_gantry_manifest:
            for line in cur_gantry_manifest:
                file_info = json.loads(line)
                commit_snapshot[file_info[constants.FILE_NAME]] = file_info

        # don't need url for new files and use checksum for empty string
        sync_diff[constants.NEW_FILES] = [
            DatasetFileInfo(
                file_name=file_name,
                url="",
                sha256=constants.EMPTY_STR_SHA256,
            )
            for file_name, _ in repo_diff[constants.NEW_FILES]
        ]
        # retrieve url for modified files
        sync_diff[constants.MODIFIED_FILES] = [
            DatasetFileInfo(
                file_name=file_name,
                url=commit_snapshot[file_name][constants.URL],
                sha256=commit_snapshot[file_name][constants.SHA256],
                version_id=commit_snapshot[file_name][constants.VERSION_ID],
            )
            for file_name, _ in repo_diff[constants.MODIFIED_FILES]
        ]
        # retrieve url for deleted files
        sync_diff[constants.DELETED_FILES] = [
            DatasetFileInfo(
                file_name=file_name,
                url=commit_snapshot[file_name][constants.URL],
                sha256=commit_snapshot[file_name][constants.SHA256],
                version_id=commit_snapshot[file_name][constants.VERSION_ID],
            )
            for file_name, _ in repo_diff[constants.DELETED_FILES]
        ]

        return sync_diff

    def _get_diff(self):
        """
        Generate local diff.

        Args:
            return_local_info (bool): if true return local file info for modified files else
            return file info in dataset repo

        Returns:
            {
                "new_files": List[Tuple(str,str)],
                "modified_files": List[Tuple(str,str)],
                "deleted_files": List[Tuple(str,str)],
            }
        """
        repo_diff = defaultdict(list)

        commit_snapshot = {}
        with open(self._get_file_path(constants.DATASET_MANIFEST_FILE)) as cur_gantry_manifest:
            for line in cur_gantry_manifest:
                file_info = json.loads(line)
                commit_snapshot[file_info[constants.FILE_NAME]] = file_info

        local_files = get_files_checksum(Path(self.workspace) / self.dataset_name)

        # TODO:// Simplify the following logic to make it easier to maintain
        for file_name, checksum in local_files.items():
            if file_name.startswith(constants.GANTRY_FOLDER):  # skip .dataset_metadata folder
                continue
            elif file_name.startswith(constants.STASH_FOLDER):  # skip stash folder
                continue
            elif file_name not in commit_snapshot:  # new added file
                repo_diff[constants.NEW_FILES].append((file_name, checksum))
            elif checksum != commit_snapshot[file_name].get(
                constants.SHA256
            ):  # if file_name in current_snapshot --> check if it has been modified
                repo_diff[constants.MODIFIED_FILES].append((file_name, checksum))

        for file_name in commit_snapshot:
            if file_name not in local_files:
                repo_diff[constants.DELETED_FILES].append((file_name, constants.EMPTY_STR_SHA256))

        return repo_diff

    def _add_single_file(
        self,
        file: IO,
        filename: str,
        commit_msg: Optional[str],
        parent_commit_id: Optional[Union[uuid.UUID, str]],
    ):
        # check if parent commit is out of date
        if parent_commit_id is not None:
            if str(parent_commit_id) != self._get_latest_commit()["id"]:
                raise DatasetHeadOutOfDateException()

        if commit_msg is None:
            commit_msg = f"Uploaded {filename} to dataset"
        commit_id = uuid.uuid4()

        # get sha256 checksum
        try:
            file.seek(0)
            file_sha256 = get_s3_sha256_checksum(file.read())
        except TypeError:
            file.seek(0)
            file_sha256 = get_s3_sha256_checksum(bytes(file.read(), encoding="utf-8"))
        file.seek(0)

        # get file directory
        file_dir = constants.ARTIFACTS
        if len(filename) > 4 and filename[-4:] == constants.CSV_SUFFIX:
            file_dir = constants.TABULAR_MANIFESTS

        # get put urls:
        upload_file_info = DatasetFileInfo(
            file_name=f"{file_dir}/{filename}",
            url=self._get_s3_url(f"{file_dir}/{filename}", commit_id),
            sha256=file_sha256,
        )
        manifest_file_info = DatasetFileInfo(
            file_name=constants.DATASET_MANIFEST_FILE,
            url=self._get_s3_url(constants.DATASET_MANIFEST_FILE),
        )
        urls = self._generate_put_presign_url([upload_file_info, manifest_file_info])

        # upload added file to s3
        upload_file_info.version_id = _upload_file_from_IO(
            urls[self._get_obj_key(upload_file_info.url)], file
        )

        # download manifest file
        url = self._generate_get_presign_url([manifest_file_info])[
            self._get_obj_key(manifest_file_info.url)
        ]
        manifest_file = io.BytesIO()
        _download_file_to_IO(url, manifest_file)
        # update manifest file
        manifest_file.write(bytes(upload_file_info.to_jsonl(), encoding="utf-8"))
        manifest_file.seek(0)
        # upload new manifest file
        version_id = _upload_file_from_IO(
            urls[self._get_obj_key(manifest_file_info.url)], manifest_file
        )

        # create dataset commit
        try:
            resp = self._api_client.request(
                "POST",
                f"/api/v1/datasets/{self._dataset_id}/commits",
                json={
                    "message": commit_msg,
                    "metadata_s3_file_version": version_id,
                    "parent_commit_id": (
                        self._get_latest_commit()["id"]
                        if parent_commit_id is None
                        else parent_commit_id
                    ),
                    "commit_id": commit_id,
                },
                raise_for_status=True,
            )
        except GantryRequestException as e:
            if (
                e.status_code == 400
                and 'Details: {"error":"Parent version out of date!","response":"error"}'
                in e.args[0]
            ):
                raise DatasetHeadOutOfDateException
            raise e

        commit_info = resp["data"]
        return self._prune_commit_info(commit_info)

    def _get_file_path(self, file_name: str) -> str:
        return os.path.join(self.workspace, self.dataset_name, file_name)

    def _get_s3_url(self, file_name: str, commit_id: Optional[uuid.UUID] = None) -> str:
        if commit_id:
            return (
                f"s3://{self._bucket_name}/{self._dataset_s3_prefix}/"
                f"{self.dataset_name}/{commit_id}/{file_name}"
            )
        else:
            return (
                f"s3://{self._bucket_name}/{self._dataset_s3_prefix}/"
                f"{self.dataset_name}/{file_name}"
            )

    def _get_obj_key(self, s3_url: str) -> str:
        _, obj_key = parse_s3_path(s3_url)
        return obj_key

    def _update_head(self, commit_info: Dict[str, Any]):
        with open(self._get_file_path(constants.DATASET_HEAD_FILE), "w") as f:
            json.dump(commit_info, f)

    def _get_current_commit(self) -> Dict[str, Any]:
        with open(self._get_file_path(constants.DATASET_HEAD_FILE), "r") as f:
            return json.load(f)

    def _backup_file(self, file_path: str):
        # make a copy of the original file
        shutil.copyfile(
            self._get_file_path(file_path),
            self._get_file_path(f"{file_path}{constants.BACKUP_SUFFIX}"),
        )

    def _recover_file(self, file_path: str):
        # recover the file from a backup copy
        os.replace(
            self._get_file_path(f"{file_path}{constants.BACKUP_SUFFIX}"),
            self._get_file_path(file_path),
        )

    def _stash_file(self, file_path: str):
        # move file to stash folder
        dest_path = self._get_file_path(f"{constants.STASH_FOLDER}/{file_path}")
        os.makedirs(Path(dest_path).parent, exist_ok=True)
        os.replace(
            self._get_file_path(file_path),
            dest_path,
        )

    def _restore_stash_file(self, file_path: str):
        # recover file from stash folder
        dest_path = self._get_file_path(file_path)
        os.makedirs(Path(dest_path).parent, exist_ok=True)
        os.replace(
            self._get_file_path(f"{constants.STASH_FOLDER}/{file_path}"),
            dest_path,
        )

    def _download_files(self, file_list: List[DatasetFileInfo]):
        """
        download file to the specific path

        Args:
            file_list (List[DatasetFileInfo]):
        """
        if len(file_list) == 0:
            logger.info("No files to download")
            return
        url_args = []
        path_args = []
        presigned_urls = {}
        for i in range(0, len(file_list), BATCH_SIZE):
            presigned_urls.update(
                self._generate_get_presign_url(batch=file_list[i : i + BATCH_SIZE])
            )
        for item in file_list:
            local_path = Path(self._get_file_path(item.file_name))
            presigned_url = presigned_urls[self._get_obj_key(item.url)]
            path_args.append(local_path)
            url_args.append(presigned_url)

        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            logger.info("Starting multipart dataset file download")
            futures = [
                executor.submit(download_file_from_url, url, path)
                for url, path in zip(url_args, path_args)
            ]
            parts = [f.result() for f in concurrent.futures.as_completed(futures)]
            logger.info(f"Multipart dataset file download completed: {parts}")

    def _generate_get_presign_url(self, batch: List[DatasetFileInfo], expiration: int = 3600):
        resp = self._api_client.request(
            "POST",
            f"/api/v1/datasets/{self._dataset_id}/presign/getobject",
            json={
                "expiration": expiration,
                "obj_infos": [
                    {
                        constants.OBJ_KEY: self._get_obj_key(item.url),
                        constants.VERSION_ID: item.version_id,
                    }
                    for item in batch
                ],
            },
            raise_for_status=True,
        )
        return resp["data"]

    def _upload_files(self, file_list: List[DatasetFileInfo]):
        """
        upload file to the specific path

        Args:
            file_list (List[DatasetFileInfo]):
        Returns:
            List[DatasetFileInfo]
        """
        if len(file_list) == 0:
            logger.info("No files to upload")
            return file_list
        url_args = []
        path_args = []
        presigned_urls = {}
        for i in range(0, len(file_list), BATCH_SIZE):
            resp = self._api_client.request(
                "POST",
                f"/api/v1/datasets/{self._dataset_id}/presign/putobject",
                json={
                    "obj_keys": [self._get_obj_key(f.url) for f in file_list[i : i + BATCH_SIZE]]
                },
                raise_for_status=True,
            )
            presigned_urls.update(resp["data"])
        for item in file_list:
            url_args.append(presigned_urls[self._get_obj_key(item.url)])
            path_args.append(Path(self._get_file_path(item.file_name)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            logger.info("Starting multipart dataset file upload")
            futures = [
                executor.submit(GantryDataset._multipart_upload_helper, url, path, item)
                for url, path, item in zip(url_args, path_args, file_list)
            ]
            parts = [f.result() for f in concurrent.futures.as_completed(futures)]
            logger.info(f"Multipart dataset file upload completed: {parts}")
        return file_list

    @staticmethod
    def _multipart_upload_helper(url: str, path: Path, item: DatasetFileInfo):
        version_id = upload_file_to_url(presigned_url=url, local_path=path)
        item.version_id = version_id
        return item.file_name

    def _generate_put_presign_url(self, batch: List[DatasetFileInfo]):
        resp = self._api_client.request(
            "POST",
            f"/api/v1/datasets/{self._dataset_id}/presign/putobject",
            json={"obj_keys": [self._get_obj_key(f.url) for f in batch]},
            raise_for_status=True,
        )
        return resp["data"]

    def _extract_feature_type(self) -> Dict[str, Any]:
        """
        Read feature type from dataset_config and convert them to huggingface feature type
        Returns:
            A key value pair of Dict where key is the column name and value is huggingface
            feature type
        """
        config = yaml.safe_load(
            (Path(self.workspace) / self.dataset_name / constants.DATASET_CONFIG_FILE).open(
                mode="r"
            )
        )
        return self._get_feature_map_from_config(config=config)

    def pull_huggingface_dataset_by_version(
        self,
        version_id: Optional[str] = None,
        hf_dataset_name: Optional[str] = None,
        streaming=False,
    ):
        """
        This function will pull the dataset tabular files from gantry server and convert it
        to huggingface dataset. This method will not pull data to your local dataset folder, it
        will only load dataset tabular data from a remote server into a huggingface dataset object.
        If there is no version_id specified, it will load the latest version of the dataset.
        If streaming set to True, it will return an IterableDataset or IterableDatasetDict instead
        of a Dataset or DatasetDict. refer to https://huggingface.co/docs/datasets/stream for more
        details about streaming.

        Example usage:

        .. code-block:: python

            import gantry.dataset as gdataset

            dataset = gdataset.get_dataset(dataset_name)

            # download your dataset as huggingface dataset
            hf_dataset = dataset.pull_huggingface_dataset_by_version(version_id="version_id")

            # pull the dataset as IterableDataset with streaming
            hf_dataset = dataset.pull_huggingface_dataset_by_version(version_id="version_id", streaming=True) # noqa: E501

        Args:
            version_id (Optional[str], optional): dataset version id to load. Defaults to latest.
            hf_dataset_name (Optional[str], optional): param to overwrite the huggingface
                                                dataset name. Note this param must be a valid
                                                python identifier.
            streaming (bool, default ``False``): If set to True, don't download the data files.
                                                 Instead, it streams the data progressively while
                                                 iterating on the dataset. An IterableDataset or
                                                 IterableDatasetDict is returned instead
                                                 in this case.
        """
        if not hf_dataset_name:
            hf_dataset_name = self._clean_variable_name(self.dataset_name)

        if not GantryDataset._is_valid_python_identifier(hf_dataset_name=hf_dataset_name):
            return

        manifest_presign_url = self._get_manifest_presign_url(version_id=version_id)
        tabular_files = self._get_tabular_files(manifest_presign_url=manifest_presign_url)
        features = self._extract_feature_schema_from_s3(manifest_presign_url=manifest_presign_url)
        if not features:
            raise DataSchemaMismatchError()
        training_files = []
        expiration = 604800 if streaming else 7200  # 7 days if streaming, 2 hours otherwise
        for i in range(0, len(tabular_files), BATCH_SIZE):
            batch = tabular_files[i : i + BATCH_SIZE]
            presigned_urls = self._generate_get_presign_url(batch=batch, expiration=expiration)
            training_files.extend(presigned_urls.values())

        if not training_files:
            raise NoTabularDataError()

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")
            )
        )

        template = env.get_template("load_script_template.py.jinja")

        content = template.render(
            training_file_list=training_files,
            dataset_version="1.0.0",  # Format should be x.y.z with {{x,y,z}} being digits
            dataset_name=hf_dataset_name,
            features=features,
        )
        hf_loading_script = (
            Path(self.workspace) / self.dataset_name / constants.HF_FOLDER / f"{hf_dataset_name}.py"
        )
        hf_loading_script.parent.mkdir(parents=True, exist_ok=True)
        with hf_loading_script.open("w") as f:
            f.write(content)

        try:
            hf_dataset = datasets.load_dataset(
                str(hf_loading_script), streaming=streaming, split="train"
            )
        except datasets.builder.DatasetGenerationError as e:
            raise DataSchemaMismatchError from e

        return hf_dataset

    def _get_manifest_presign_url(self, version_id: Optional[str] = None) -> str:
        target_commit = (
            self._get_commit(commit_id=version_id) if version_id else self._get_latest_commit()
        )

        metadata_version_id = target_commit[constants.METADATA_S3_FILE_VERSION]
        manifest_s3_url = self._get_s3_url(constants.DATASET_MANIFEST_FILE)

        return self._generate_get_presign_url(
            [
                DatasetFileInfo(
                    file_name=constants.DATASET_MANIFEST_FILE,
                    url=manifest_s3_url,
                    version_id=metadata_version_id,
                )
            ]
        )[self._get_obj_key(manifest_s3_url)]

    def _get_tabular_files(self, manifest_presign_url: str) -> List[DatasetFileInfo]:
        """
        Get tabular file list based on the version id

        Args:
            version_id (Optional[str], optional): dataset version. Defaults to None.

        Returns:
            List[DatasetFileInfo]: tabular file list
        """
        tabular_files = []
        for line in read_lines_from_url(manifest_presign_url):
            file_info = json.loads(line)
            if file_info[constants.FILE_NAME].startswith(constants.TABULAR_MANIFESTS) and file_info[
                constants.FILE_NAME
            ].endswith(constants.CSV_SUFFIX):
                tabular_files.append(
                    DatasetFileInfo(
                        file_name=file_info[constants.FILE_NAME],
                        url=file_info[constants.URL],
                        version_id=file_info[constants.VERSION_ID],
                    )
                )
        return tabular_files

    def _extract_feature_schema_from_s3(self, manifest_presign_url: str):
        for line in read_lines_from_url(manifest_presign_url):
            file_info = json.loads(line)
            if file_info[constants.FILE_NAME] == constants.DATASET_CONFIG_FILE:
                # read config file
                # generate the feature map
                config_presign_url = self._generate_get_presign_url(
                    [
                        DatasetFileInfo(
                            file_name=file_info[constants.FILE_NAME],
                            url=file_info[constants.URL],
                            version_id=file_info[constants.VERSION_ID],
                        )
                    ]
                )[self._get_obj_key(file_info[constants.URL])]

                # generate presign url for config file
                response = requests.get(config_presign_url)
                config = yaml.safe_load(response.text)

                return GantryDataset._get_feature_map_from_config(config=config)

    @staticmethod
    def _get_feature_map_from_config(config):
        columns = dict()
        if constants.DATASET_FEATURES_KEY in config:
            for feature_name, feature_dtype in config[constants.DATASET_FEATURES_KEY].items():
                columns[feature_name] = constants.GANTRY_2_HF_DTYPE[feature_dtype]

        if constants.DATASET_FEEDBACK_KEY in config:
            for feature_name, feature_dtype in config[constants.DATASET_FEEDBACK_KEY].items():
                columns[feature_name] = constants.GANTRY_2_HF_DTYPE[feature_dtype]

        return columns

    def get_huggingface_dataset(
        self, hf_dataset_name: Optional[str] = None, streaming: bool = False
    ):
        """
        This function will convert your local dataset folder to a huggingface dataset. Internally
        Gantry SDK will create a huggingface load script based on the dataset config and then load
        the dataset into huggingface pyarrow dataset. If streaming set to True, it will return
        an IterableDataset or IterableDatasetDict instead of a Dataset or DatasetDict. refer to
        https://huggingface.co/docs/datasets/stream for more details about streaming.

        Example usage:

        .. code-block:: python

            import gantry.dataset as gdataset

            dataset = gdataset.get_dataset(dataset_name)
            dataset.pull()

            # load the dataset into huggingface dataset
            hf_dataset = dataset.get_huggingface_dataset()

            # load the dataset into huggingface dataset with streaming
            hf_dataset = dataset.get_huggingface_dataset(streaming=True)

        Args:
            versoion_id (Optional[str], optional): dataset version id to load. Defaults to latest.
            hf_dataset_name (Optional[str], optional): param to overwrite the huggingface
                                                dataset name. Note this param must be a valid
                                                python identifier.
            streaming (bool, default ``False``): If set to True, don't download the data files.
                                                 Instead, it streams the data progressively while
                                                 iterating on the dataset. An IterableDataset or
                                                 IterableDatasetDict is returned instead
                                                 in this case.
        """

        if not hf_dataset_name:
            hf_dataset_name = GantryDataset._clean_variable_name(self.dataset_name)

        if not GantryDataset._is_valid_python_identifier(hf_dataset_name=hf_dataset_name):
            return

        tabular_manifests_path = (
            Path(self.workspace) / self.dataset_name / constants.TABULAR_MANIFESTS
        ).resolve()

        if not os.path.exists(tabular_manifests_path) or not any(
            Path(tabular_manifests_path).iterdir()
        ):
            raise NoTabularDataError()

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")
            )
        )

        template = env.get_template("load_script_template.py.jinja")

        training_files = [str(p) for p in list_all_files(tabular_manifests_path.resolve())]
        features = self._extract_feature_type()

        # verify the csvs agree with the schema
        for csv_path in training_files:
            with open(csv_path) as data_csv:
                cols = next(csv.reader(data_csv))

                if set(cols) != set(features):
                    raise DataSchemaMismatchError()

        content = template.render(
            training_file_list=training_files,
            dataset_version="1.0.0",  # Format should be x.y.z with {{x,y,z}} being digits
            dataset_name=hf_dataset_name,
            features=features,
        )
        hf_loading_script = (
            Path(self.workspace) / self.dataset_name / constants.HF_FOLDER / f"{hf_dataset_name}.py"
        )
        os.makedirs(hf_loading_script.parent, exist_ok=True)
        with hf_loading_script.open("w") as f:
            f.write(content)

        try:
            hf_dataset = datasets.load_dataset(
                str(hf_loading_script), streaming=streaming, split="train"
            )
        except datasets.builder.DatasetGenerationError as e:
            raise DataSchemaMismatchError from e

        return hf_dataset

    @staticmethod
    def _is_valid_python_identifier(hf_dataset_name):
        if (
            (not hf_dataset_name)
            or (not hf_dataset_name.isidentifier())
            or iskeyword(hf_dataset_name)
        ):
            logger.error(
                "Can't get a valid hugging face dataset name, the name has to be a valid python"
                + "identifier. Please use hf_dataset_name param to set a valid name and try again."
            )
            return False
        else:
            return True

    def _prune_commit_info(self, commit_info):
        return {
            "version_id": commit_info["id"],
            "dataset": self.dataset_name,
            "message": commit_info["message"],
            # TODO:// uncomment the following line once we add sdk support for user version
            # "version_name": commit_info["user_version"],
            "created_at": commit_info["created_at"],
            "created_by": commit_info["created_by"],
            "is_latest_version": commit_info["is_latest_commit"],
        }

    @staticmethod
    def _clean_variable_name(ds_name):
        # Remove invalid characters
        ds_name = re.sub("[^0-9a-zA-Z_]", "", ds_name)
        # Remove leading characters until we find a letter or underscore
        ds_name = re.sub("^[^a-zA-Z_]+", "", ds_name)
        return ds_name

import logging
from pathlib import Path, PurePath
from typing import Any, Dict, List, Optional

from typeguard import typechecked

from gantry.api_client import APIClient
from gantry.dataset.gantry_dataset import GantryDataset
from gantry.exceptions import DatasetNotFoundError, GantryRequestException

logger = logging.getLogger(__name__)


class GantryDatasetClient:
    def __init__(
        self,
        api_client: APIClient,
        working_directory: str = str(Path().absolute()),
    ):
        self._api_client = api_client
        self._workspace = working_directory

    @property
    def working_directory(self) -> str:
        return self._workspace  # type: ignore

    @working_directory.setter
    def working_directory(self, value: str):
        if not PurePath(value).is_absolute():
            logger.warning(
                f"{value} is not an absolute path, will use {Path(value).resolve()} instead."
            )
        else:
            logger.info(f"Set dataset working directory to {value}")
        self._workspace = str(Path(value).resolve())
        Path(self._workspace).mkdir(exist_ok=True)

    def set_working_directory(self, working_dir: str) -> None:
        """
        Set the working directory for the dataset client. This is the directory where the local
        copy of the dataset will be stored.

        Example usage:

        .. code-block:: python

            import gantry.dataset as gdataset
            gdataset.set_working_directory("your working directory")

        Args:
            working_dir (str): absolute path of the directory used to store local copy of datasets.

        Returns:
            ``None``
        """
        self.working_directory = working_dir

    @typechecked
    def create_dataset(
        self, name: str, bucket_name: Optional[str] = None, app_name: Optional[str] = None
    ) -> GantryDataset:
        """
        Create a dataset with the provided name. If ``app_name`` is provided, we will use the
        application schema to set the dataset schema. ``bucket_name`` can be provided if you want
        to store data in your own bucket, please contact Gantry support if you want to use
        this feature. If not provided, we will use a gantry managed bucket.

        Example usage:

        .. code-block:: python

            import gantry.dataset as gdataset
            # Create an empty dataset with the name "dataset_name"
            gdataset.create_dataset("dataset_name")
            # Create a dataset with the name "dataset_name" and set the schema to the schema of the
            # application "app_name"
            gdataset.create_dataset("dataset_with_app", app_name="app_name")


        Args:
            name (str): dataset name
            bucket_name (str): Provide bucket name if you want to use your own bucket. If not
                provided we will use a gantry managed bucket.
            app_name (Optional[str], optional): gantry application name which will be used to set
                dataset schema if provided.

        Returns:
            :class:`gantry.dataset.GantryDataset`: an object representing the created dataset.
        """
        data = {
            "name": name,
        }

        if app_name:
            res = self._api_client.request(
                "GET", f"/api/v1/applications/{app_name}/schemas", raise_for_status=True
            )
            data["model_id"] = res["data"]["id"]

        if bucket_name:
            data.update(
                {
                    "bucket_name": bucket_name,
                }
            )

        res = self._api_client.request("POST", "/api/v1/datasets", json=data, raise_for_status=True)

        return GantryDataset(
            api_client=self._api_client,
            dataset_name=res["data"]["name"],
            dataset_id=res["data"]["id"],
            bucket_name=res["data"]["bucket_name"],
            aws_region=res["data"]["aws_region"],
            dataset_s3_prefix=f"{res['data']['organization_id']}/{res['data']['s3_prefix']}",
            workspace=self._workspace,
        )

    @typechecked
    def get_dataset(self, name: str) -> GantryDataset:
        """
        Get a dataset object by name. If the dataset is marked as deleted, a warning will be
        logged. If the dataset does not exist, a :class:`gantry.exceptions.DatasetNotFoundError`
        will be raised.

        Example usage:

        .. code-block:: python

            import gantry.dataset as gdataset
            dataset = gdataset.get_dataset("dataset_name")

        Args:
            name (str): the name of the dataset.

        Returns:
            :class:`gantry.dataset.GantryDataset`: An object representing the dataset name.
        """
        try:
            res = self._api_client.request("GET", f"/api/v1/datasets/{name}", raise_for_status=True)
        except GantryRequestException as e:
            if e.status_code == 404:
                raise DatasetNotFoundError(f'Could not find dataset with name "{name}"') from e
            raise

        if res["data"]["disabled"]:
            logger.warning("This dataset is marked as deleted")

        return GantryDataset(
            api_client=self._api_client,
            dataset_name=res["data"]["name"],
            dataset_id=res["data"]["id"],
            bucket_name=res["data"]["bucket_name"],
            aws_region=res["data"]["aws_region"],
            dataset_s3_prefix=f"{res['data']['organization_id']}/{res['data']['s3_prefix']}",
            workspace=self._workspace,
        )

    @typechecked
    def list_dataset_versions(self, dataset_name: str) -> List[Dict[str, Any]]:
        """
        List all versions of a dataset. Each dataset version is a snapshot of the dataset at a
        particular point in time. The result will be sorted from latest to earliest.

        Example usage:

        .. code-block:: python

            import gantry.dataset as gdataset
            gdataset.list_dataset_versions("dataset_name")

        Output example:

        .. code-block:: text

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

        Args:
            name (str): the name of the dataset.

        Returns:
            ``List[Dict[str, Any]]``: list of dictionaries with metadata.
        """
        dataset = self.get_dataset(dataset_name)

        return dataset.list_versions()

    @typechecked
    def list_datasets(
        self, include_deleted: bool = False, model_node_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all datasets. If ``include_deleted`` is set to ``True``, deleted datasets will be
        included in the result list.

        Example usage:

        .. code-block:: python

            import gantry.dataset as gdataset
            gdataset.list_datasets()

        Output example:

        .. code-block:: text

            [{'name': 'dataset_0',
            'dataset_id': '44e8dff0-1e4c-4484-843c-ca3c585d405d',
            'created_at': 'Sun, 12 Feb 2023 00:08:12 GMT'},
            {'name': 'dataset_1',
            'dataset_id': '3adb66fa-9dc7-4a60-86b6-83389f567186',
            'created_at': 'Sun, 12 Feb 2023 00:05:15 GMT'},
            {'name': 'dataset_2',
            'dataset_id': '0a5b5706-2060-4601-8c5c-22900f06d54a',
            'created_at': 'Wed, 08 Feb 2023 22:00:26 GMT'},

        Args:
            include_deleted (bool): whether include deleted datasets in the result, defaults
                to ``False``.

        Returns:
            ``List[Dict[str, Any]]``: List of dictionaries, each representing one
            dataset and associated metadata.
        """
        res = self._api_client.request(
            "GET",
            "/api/v1/datasets",
            raise_for_status=True,
            params={"include_deleted": include_deleted, "model_node_id": model_node_id},
        )

        return [self._prune_dataset_info(dataset_info) for dataset_info in res["data"]]

    @typechecked
    def delete_dataset(self, name: str) -> None:
        """
        Mark the dataset as deleted. As for now this will only hide dataset from the list_datasets
        API results, it will not delete the dataset data from the server, we will release the
        hard deletion feature later.

        Example usage:

        .. code-block:: python

            import gantry.dataset as gdataset
            gdataset.delete_dataset("dataset_name")

        Args:
            name (str): the name of the dataset to be deleted.

        Returns:
            ``None``
        """
        dataset = self.get_dataset(name)

        return dataset.delete()

    def ping(self) -> bool:
        """
        Pings the API client server to check if it is alive.
        Returns ``True`` if alive, ``False`` if there is an error during ping process.

        Returns
            ``bool``: flag indicating liveness.
        """
        try:
            # Cannot use /healthz/* endpoints as those will be answered by nginx
            # need to use /.
            # See https://linear.app/gantry/issue/ENG-2978/revisit-ping-in-sdk
            self._api_client.request("GET", "/api/ping", raise_for_status=True)
            return True
        except Exception as e:
            logger.error(f"Error during ping: {e}")
            return False

    def ready(self) -> bool:
        """
        Checks whether the API is ready to receive traffic with the provided API Key.
        """
        try:
            self._api_client.request("GET", "/api/v1/auth-ping", raise_for_status=True)
            return True
        except Exception as e:
            logger.error(f"Error during api key check: {e}")
            return False

    @staticmethod
    def _prune_dataset_info(dataset_info):
        return {
            "name": dataset_info["name"],
            "dataset_id": dataset_info["id"],
            "created_at": dataset_info["created_at"],
        }

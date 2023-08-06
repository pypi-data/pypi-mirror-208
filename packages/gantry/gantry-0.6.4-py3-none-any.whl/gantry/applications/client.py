import logging
import uuid
from typing import Optional

from typeguard import typechecked

from gantry.api_client import APIClient
from gantry.applications.core import Application
from gantry.applications.llm import CompletionApplication

logger = logging.getLogger(__name__)


class ApplicationClient:
    def __init__(self, api_client: APIClient) -> None:
        self._api_client = api_client

    @typechecked
    def create_application(
        self, application_name: str, application_type: Optional[str] = None
    ) -> Application:
        """
        Create an Application object by name and type. If the application already exists,
        an exception will be raised. If your organization does not allow you to create
        an application of a certain type, there will be an exception raised as well.

        Example usage:

        .. code-block:: python

            import gantry
            application = gantry.create_application("demo", "Custom")

        Args:
            application_name (str): the name of the application.
            application_type (str, optional): the type of the application. Defaults to Custom.
            You have the following options for application type:
                Custom
                Chat
                Completion
        Returns:
            :class:`gantry.Application`: An object representing the application.
        """
        data = {
            "model_name": application_name,
        }
        if application_type:
            data["model_type"] = application_type

        res = self._api_client.request(
            "POST",
            "/api/v1/applications",
            json=data,
            raise_for_status=True,
        )

        return self._get_application(
            name=application_name,
            id=uuid.UUID(res["data"]["id"]),
            type=application_type,
        )

    @typechecked
    def get_application(self, application_name: str) -> Application:
        """
        Get an Application object by name.

        Example usage:

        .. code-block:: python

            import gantry
            application = gantry.get_application("demo")

        Args:
            application_name (str): the name of the application.
        Returns:
            :class:`gantry.Application`: An object representing the application.
        """
        res1 = self._api_client.request(
            "GET",
            "/api/v1/applications/{}".format(application_name),
            raise_for_status=True,
        )
        res2 = self._api_client.request(
            "GET",
            "/api/v1/applications/{}/schemas".format(application_name),
            raise_for_status=True,
        )

        return self._get_application(
            name=res1["data"]["func_name"],
            id=uuid.UUID(res1["data"]["versions"][0]["application_id"]),
            type=res2["data"]["model_type"],
        )

    @typechecked
    def archive_application(self, application_name: str) -> None:
        """
        Archive an Application.

        Example usage:

        .. code-block:: python

            import gantry
            application = gantry.archive_application("demo")

        Args:
            application_name (str): the name of the application.
        Returns:
            None
        """
        model_id = self.get_application(application_name)._id
        self._api_client.request(
            "DELETE",
            "/api/v1/applications/{}".format(model_id),
            raise_for_status=True,
        )

    @typechecked
    def delete_application(self, application_name: str) -> None:
        """
        Hard delete an Application.

        Example usage:

        .. code-block:: python

            import gantry
            application = gantry.delete_application("demo")

        Args:
            application_name (str): the name of the application.
        Returns:
            None
        """
        model_id = self.get_application(application_name)._id
        self._api_client.request(
            "POST",
            "/api/v1/applications/{}/hard_delete".format(model_id),
            raise_for_status=True,
        )

    def _get_application(self, name: str, id: uuid.UUID, type: Optional[str]) -> Application:
        if type == "Completion":
            return CompletionApplication(
                name=name,
                api_client=self._api_client,
                id=id,
            )
        elif type == "Custom":
            return Application(
                name=name,
                api_client=self._api_client,
                id=id,
            )
        else:
            return Application(
                name=name,
                api_client=self._api_client,
                id=id,
            )

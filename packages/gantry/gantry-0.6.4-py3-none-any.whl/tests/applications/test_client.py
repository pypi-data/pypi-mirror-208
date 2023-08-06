import uuid

import responses
from responses import matchers

from .conftest import HOST


def test_create_application(test_client):
    test_id = uuid.uuid4()
    application_name = "test_application_name"
    application_type = "test_application_type"

    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/applications",
            json={
                "response": "ok",
                "data": {
                    "id": str(test_id),
                    "model_name": application_name,
                },
            },
            headers={"Content-Type": "application/json"},
            match=[
                matchers.json_params_matcher(
                    {"model_name": application_name, "model_type": application_type}
                )
            ],
        )
        test_application = test_client.create_application(application_name, application_type)

    assert test_application._name == application_name
    assert test_application._id == test_id


def test_get_application(test_client):
    test_id = uuid.uuid4()
    application_name = "test_application_name"

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/{application_name}",
            json={
                "response": "ok",
                "data": {
                    "versions": [
                        {
                            "internal_version": "1",
                            "version": "first model",
                            "application_id": str(test_id),
                        },
                    ],
                    "func_name": application_name,
                },
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/{application_name}/schemas",
            json={
                "response": "ok",
                "data": {
                    "model_type": "test_model_type",
                },
            },
        )
        test_application = test_client.get_application(application_name)

    assert test_application._name == application_name
    assert test_application._id == test_id

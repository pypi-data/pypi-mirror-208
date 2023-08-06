import logging
import uuid

import pytest
import responses
from responses import matchers

from gantry.applications.llm import (
    CompletionAPILogStore,
    CompletionApplication,
    OpenAIParams,
)
from gantry.logger.stores import BaseLogStore

from ..conftest import TestingBatchConsumer
from .conftest import HOST


class TestingCompletionLogStore(BaseLogStore):
    def __init__(self, *args, **kwargs):
        self._store = []

    def log(self, application: str, event: dict) -> None:
        self._store.append((application, event))


@pytest.fixture
def test_llm_application(test_api_client):
    return CompletionApplication(
        name="test_llm_application",
        api_client=test_api_client,
        id=uuid.uuid4(),
        log_store_factory=TestingCompletionLogStore,
    )


def test_get_llm_application(test_client):
    with responses.RequestsMock() as resp:
        test_id = uuid.uuid4()
        application_name = "test_application_name"
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
                    "model_type": "Completion",
                },
            },
        )
        test_application = test_client.get_application(application_name)
        assert test_application._name == application_name
        assert test_application._id == test_id

        assert isinstance(test_application, CompletionApplication)


@pytest.mark.parametrize(
    ("version_kwargs", "configuration_data"),
    [
        (
            {"prompt_template": "test prompt template", "model": "text-davinci-001"},
            {
                "prompt": "test prompt template",
                "prompt_inputs": [],
                "model": "text-davinci-001",
                "params": OpenAIParams().dict(),
            },
        ),
        (
            {"prompt_template": "test prompt {{template}}", "model": "text-davinci-001"},
            {
                "prompt": "test prompt {{template}}",
                "prompt_inputs": ["template"],
                "model": "text-davinci-001",
                "params": OpenAIParams().dict(),
            },
        ),
        (
            {
                "prompt_template": "x",
                "model": "text-davinci-001",
                "model_params": {"temperature": 0.5, "max_tokens": 10},
            },
            {
                "prompt": "x",
                "prompt_inputs": [],
                "model": "text-davinci-001",
                "params": OpenAIParams(temperature=0.5, max_tokens=10).dict(),
            },
        ),
        (
            {"prompt_template": "x", "model": "text-davinci-001", "prompt_inputs": ["test"]},
            {
                "prompt": "x",
                "prompt_inputs": ["test"],
                "model": "text-davinci-001",
                "params": OpenAIParams().dict(),
            },
        ),
    ],
)
def test_create_version(
    test_llm_application: CompletionApplication, version_kwargs: dict, configuration_data: dict
):
    version_id = uuid.uuid4()
    description = "test description"
    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            (
                f"{HOST}/api/v1/cms/{test_llm_application._name}/configurations/"
                f"{test_llm_application._configuration_name}/versions"
            ),
            json={
                "response": "ok",
                "data": {
                    "id": str(version_id),
                    "configuration_id": str(uuid.uuid4()),
                    "version": 1,
                    "checksum": "1234",
                    "s3_paths": ["s3://test_bucket/test_path"],
                    "notes": description,
                    "created_at": "2020-01-01T00:00:00.000000Z",
                },
            },
            headers={"Content-Type": "application/json"},
            match=[
                matchers.json_params_matcher(
                    {
                        "configuration_data": configuration_data,
                        "description": description,
                    },
                )
            ],
        )

        version = test_llm_application.create_version(
            description=description,
            **version_kwargs,
        )

    assert version.version_id == version_id
    assert version.config == configuration_data


def test_create_version_invalid_model(test_llm_application: CompletionApplication):
    with pytest.raises(ValueError):
        test_llm_application.create_version(
            description="test description",
            prompt_template="test prompt template",
            model="invalid model",
        )


@pytest.mark.parametrize(
    "params",
    [
        {"temperature": "hot"},
    ],
)
def test_create_version_invalid_params(test_llm_application: CompletionApplication, params):
    with pytest.raises(ValueError):
        test_llm_application.create_version(
            description="test description",
            prompt_template="test prompt template",
            model="text-davinci-001",
            model_params=params,
        )


@pytest.mark.parametrize("version", ["latest", "prod", "test"])
def test_get_version(test_llm_application: CompletionApplication, version: str):
    version_id = uuid.uuid4()
    configuration_id = uuid.uuid4()
    configuration_data = {"test": "test"}
    description = "test description"
    version_data = {
        "id": str(version_id),
        "configuration_id": str(configuration_id),
        "version": 1,
        "checksum": "1234",
        "s3_paths": ["s3://test_bucket/test_path"],
        "notes": description,
        "created_at": "2020-01-01T00:00:00.000000Z",
    }

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            (
                f"{HOST}/api/v1/cms/{test_llm_application._name}/configurations/"
                f"{test_llm_application._configuration_name}/versions/{version_id}/data"
            ),
            json={"response": "ok", "data": [configuration_data]},
            headers={"Content-Type": "application/json"},
        )

        if version == "latest":
            resp.add(
                resp.GET,
                (
                    f"{HOST}/api/v1/cms/{test_llm_application._name}/configurations/"
                    f"{test_llm_application._configuration_name}/versions"
                ),
                json={"response": "ok", "data": [version_data, {"fake": "data"}]},
                headers={"Content-Type": "application/json"},
            )
        else:
            resp.add(
                resp.GET,
                (
                    f"{HOST}/api/v1/cms/{test_llm_application._name}/configurations/"
                    f"{test_llm_application._configuration_name}/releases?latest=True&env={version}"
                ),
                json={
                    "response": "ok",
                    "data": [
                        {
                            "id": str(uuid.uuid4()),
                            "configuration_id": str(configuration_id),
                            "description": "test release",
                            "version": version_data,
                            "env": None,
                        }
                    ],
                },
                headers={"Content-Type": "application/json"},
            )

        test_version = test_llm_application.get_version(version)  # type: ignore

    assert test_version is not None
    assert test_version.version_id == version_id
    assert test_version.config == configuration_data


@pytest.mark.parametrize("version", ["latest", "prod", "test"])
def test_get_version_not_found(test_llm_application: CompletionApplication, version: str, caplog):
    with responses.RequestsMock() as resp:
        if version == "latest":
            resp.add(
                resp.GET,
                (
                    f"{HOST}/api/v1/cms/{test_llm_application._name}/configurations/"
                    f"{test_llm_application._configuration_name}/versions"
                ),
                json={"response": "ok", "data": []},
                headers={"Content-Type": "application/json"},
            )
        else:
            resp.add(
                resp.GET,
                (
                    f"{HOST}/api/v1/cms/{test_llm_application._name}/configurations/"
                    f"{test_llm_application._configuration_name}/releases?latest=True&env={version}"
                ),
                json={"response": "ok", "data": []},
                headers={"Content-Type": "application/json"},
            )

        with caplog.at_level(logging.WARNING):
            test_version = test_llm_application.get_version(version)  # type: ignore

    assert "No version found" in caplog.text
    assert test_version is None


def test_log_completion(test_llm_application: CompletionApplication, caplog):
    test_llm_application.log_completion(
        open_ai_api_request={"request": "foo"},
        open_ai_api_response={"response": "bar"},
        request_attributes={"foo": "bar"},
        response_attributes={"bar": "baz"},
        selected_choice_index=1,
        session_id="12345",
        tags={"a": "b"},
        version=100,
    )

    assert test_llm_application._log_store._store == [
        (
            "test_llm_application",
            {
                "application": "test_llm_application",
                "open_ai_api_request": {"request": "foo"},
                "open_ai_api_response": {"response": "bar"},
                "request_attributes": {"foo": "bar"},
                "response_attributes": {"bar": "baz"},
                "selected_choice_index": 1,
                "session_id": "12345",
                "tags": {"a": "b", "version_number": 100},
            },
        ),
    ]


def test_completion_api_log_store_log_batch(test_api_client):
    log_store = CompletionAPILogStore(test_api_client, consumer_factory=TestingBatchConsumer)
    event = {"foo": "bar"}
    with pytest.raises(NotImplementedError):
        log_store.log_batch("test_llm_application", [event])


def test_completion_api_log_store_log(test_api_client):
    log_store = CompletionAPILogStore(test_api_client, consumer_factory=TestingBatchConsumer)
    event = {"foo": "bar"}
    log_store.log("test_llm_application", event)

    assert log_store.queue.get() == {"foo": "bar"}
    assert log_store.queue.empty()
    assert log_store.consumers[0].running
    assert log_store.consumers[0].func == log_store.consumer_func


def test_completion_api_log_store_consumer_func(test_api_client):
    log_store = CompletionAPILogStore(test_api_client, consumer_factory=TestingBatchConsumer)
    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/logging/completions",
            json={"response": "ok"},
            headers={"Content-Type": "application/json"},
            match=[matchers.json_params_matcher({"foo": "bar"})],
        )
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/logging/completions",
            json={"response": "ok"},
            headers={"Content-Type": "application/json"},
            match=[matchers.json_params_matcher({"bar": "baz"})],
        )

        log_store.consumer_func([b'{"foo": "bar"}', b'{"bar": "baz"}'])


def test_completion_api_log_store_send_completion_event(test_api_client):
    log_store = CompletionAPILogStore(test_api_client, consumer_factory=TestingBatchConsumer)
    event = {"foo": "bar"}
    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/logging/completions",
            json={"response": "ok"},
            headers={"Content-Type": "application/json"},
            match=[matchers.json_params_matcher({"foo": "bar"})],
        )

        log_store.send_completion_event(event)

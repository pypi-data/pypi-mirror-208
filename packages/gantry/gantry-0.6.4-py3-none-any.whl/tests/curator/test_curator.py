import datetime

import pytest
import responses
from responses import matchers

from gantry.api_client import APIClient
from gantry.automations.curators import Curator
from gantry.automations.curators.curators import CuratorClient
from gantry.automations.curators.selectors import Selector

from .conftest import HOST


@pytest.fixture
def test_api_client():
    return APIClient(origin=HOST)


@pytest.fixture
def test_client(test_api_client):
    return CuratorClient(api_client=test_api_client)


@pytest.mark.parametrize(
    ("application_name", "expected_len"),
    [(None, 2), ("test_curator_app", 1), ("different_app_name", 0)],
)
def test_get_curators(test_client, test_curators, application_name, expected_len):
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/curator",
            json={
                "response": "ok",
                "data": test_curators,
            },
            headers={"Content-Type": "application/json"},
        )
        curators = test_client.get_all_curators(application_name=application_name)
        assert len(curators) == expected_len


@pytest.mark.parametrize(
    ("application_name", "expected_len"),
    [(None, 2), ("test_curator_app", 1), ("different_app_name", 0)],
)
def test_list_curators(test_client, test_curators, application_name, expected_len):
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/curator",
            json={
                "response": "ok",
                "data": test_curators,
            },
            headers={"Content-Type": "application/json"},
        )
        curator_names = test_client.list_curators(application_name=application_name)
        assert len(curator_names) == expected_len


def test_get_curator(test_client, test_curator):
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/curator/test_curator_name",
            json={
                "response": "ok",
                "data": test_curator,
            },
            headers={"Content-Type": "application/json"},
        )
        _ = test_client.get_curator(name="test_curator_name")


def test_create_curator_disabled(test_api_client, test_curators):
    curator = Curator(**test_curators[0], api_client=test_api_client)

    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/curator",
            json={
                "response": "ok",
                "data": test_curators[1],
            },
            headers={"Content-Type": "application/json"},
        )
        assert curator.create(enable=False) is curator

    assert str(curator.id) == test_curators[1]["id"]
    assert curator.name == test_curators[1]["name"]
    assert curator.curated_dataset_name == test_curators[1]["curated_dataset_name"]
    assert curator.application_name == test_curators[1]["application_name"]
    assert curator.start_on.isoformat() == test_curators[1]["start_on"]
    assert str(curator.curation_interval) == test_curators[1]["curation_interval"]
    assert curator.curate_past_intervals == test_curators[1]["curate_past_intervals"]
    assert curator.created_at.isoformat() == test_curators[1]["created_at"]
    assert curator.selectors == [Selector(**info) for info in test_curators[1]["selectors"]]


def test_update_curator(test_api_client, test_curator):
    curator = Curator(**test_curator, api_client=test_api_client)

    update_info = {
        "name": "updated_name",
        "curated_dataset_name": "updated_dataset_name",
        "curation_interval": str(datetime.timedelta(hours=5)),
        "selectors": [Selector(limit=123).dict()],
    }

    updated_json = {
        key: test_curator[key] if key not in update_info else update_info[key]
        for key in test_curator
    }

    with responses.RequestsMock() as resp:
        resp.add(
            resp.PATCH,
            f"{HOST}/api/v1/curator",
            json={
                "response": "ok",
                "data": updated_json,
            },
            headers={"Content-Type": "application/json"},
        )

        assert (
            curator.update(
                new_curator_name=update_info["name"],
                new_curated_dataset_name=update_info["curated_dataset_name"],
                new_curation_interval=update_info["curation_interval"],
                new_selectors=update_info["selectors"],
            )
            is curator
        )

    assert curator.name == update_info["name"]
    assert str(curator.curation_interval) == update_info["curation_interval"]
    assert curator.selectors == update_info["selectors"]
    assert curator.curated_dataset_name == update_info["curated_dataset_name"]


def test_delete_curator(test_api_client, test_curator):
    curator = Curator(**test_curator, api_client=test_api_client)

    with responses.RequestsMock() as resp:
        resp.add(
            resp.DELETE,
            f"{HOST}/api/v1/curator/{test_curator['id']}",
            json={
                "response": "ok",
                "data": {
                    "curated_dataset_name": test_curator["name"],
                    "id": test_curator["id"],
                    "application_name": test_curator["application_name"],
                    "deleted_at": str(datetime.datetime(2022, 1, 1)),
                },
            },
            headers={"Content-Type": "application/json"},
        )

        curator_info = f"{test_curator['name']} ({test_curator['id']})"
        assert curator.delete() == f"Curator {curator_info} deleted at 2022-01-01 00:00:00"

    with pytest.raises(ValueError):
        _ = curator.id
    with pytest.raises(ValueError):
        _ = curator.created_at


def test_enable(test_api_client, test_curator):
    curator = Curator(**test_curator, api_client=test_api_client)

    with responses.RequestsMock() as resp:
        resp.add(
            resp.PATCH,
            f"{HOST}/api/v1/curator/enable",
            json={
                "response": "ok",
                "data": "response_data",
            },
            headers={"Content-Type": "application/json"},
            match=[matchers.json_params_matcher({"name": curator.name, "enable": True})],
        )
        assert curator.enable() == "response_data"


def test_disable(test_api_client, test_curator):
    curator = Curator(**test_curator, api_client=test_api_client)

    with responses.RequestsMock() as resp:
        resp.add(
            resp.PATCH,
            f"{HOST}/api/v1/curator/enable",
            json={
                "response": "ok",
                "data": "response_data",
            },
            headers={"Content-Type": "application/json"},
            match=[matchers.json_params_matcher({"name": curator.name, "enable": False})],
        )
        assert curator.disable() == "response_data"


def test_create_curator_default_enabled(test_api_client, test_curators):
    curator = Curator(**test_curators[0], api_client=test_api_client)

    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/curator",
            json={
                "response": "ok",
                "data": test_curators[1],
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.PATCH,
            f"{HOST}/api/v1/curator/enable",
            json={
                "response": "ok",
                "data": "response_data",
            },
            headers={"Content-Type": "application/json"},
            match=[
                matchers.json_params_matcher({"name": test_curators[1]["name"], "enable": True})
            ],
        )
        assert curator.create() is curator

    assert str(curator.id) == test_curators[1]["id"]
    assert curator.name == test_curators[1]["name"]

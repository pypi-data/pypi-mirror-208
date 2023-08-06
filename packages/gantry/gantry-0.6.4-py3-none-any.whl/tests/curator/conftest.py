import pytest

HOST = "https://test-api"


@pytest.fixture(scope="function")
def test_curators():
    return [
        {
            "id": "01234567-89ab-cdef-0123-456789abcdef",
            "application_name": "test_curator_app",
            "name": "test_curator_name",
            "curated_dataset_name": "test_dataset",
            "start_on": "2023-01-20T22:36:47+00:00",
            "curation_interval": "12:00:00",
            "curation_delay": "00:00:00",
            "curate_past_intervals": False,
            "created_at": "2024-01-20T22:36:47+00:00",
            "selectors": [],
        },
        {
            "id": "6d4e42bc-ff43-4fe4-8625-e368c07b7f08",
            "application_name": "test_selector_app",
            "name": "test_selector_name",
            "curated_dataset_name": "test_dataset_selector",
            "start_on": "2023-01-01T23:12:41+00:00",
            "curation_interval": "20:00:00",
            "curation_delay": "05:00:00",
            "curate_past_intervals": True,
            "created_at": "2020-05-08T01:12:51+00:00",
            "selectors": [
                {
                    "limit": 10,
                    "method": {"field": "inputs.input1", "sample": "ordered", "sort": "ascending"},
                },
                {
                    "limit": 10,
                    "method": {"sample": "uniform"},
                    "filters": [
                        {"field": "inputs.input1", "upper": 70, "lower": 30},
                        {"field": "inputs.input2", "contains": "text"},
                    ],
                },
            ],
        },
    ]


@pytest.fixture(scope="function")
def test_curator(test_curators):
    return test_curators[0]

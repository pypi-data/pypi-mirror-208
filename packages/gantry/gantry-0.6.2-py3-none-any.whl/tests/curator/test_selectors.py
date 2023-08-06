import mock
import pydantic
import pytest

from gantry.automations.curators import (
    AscendedSortCurator,
    BalancedStratificationCurator,
    BoundedRangeCurator,
    Curator,
    DescendedSortCurator,
    EqualityCurator,
    NewestCurator,
    OldestCurator,
    ProportionalStratificationCurator,
    StrictStratificationCurator,
    UniformCurator,
)
from gantry.automations.curators.selectors import (
    BoundsFilter,
    ContainsFilter,
    DruidDimensionOrderingDirections,
    EqualsFilter,
    OrderedSampler,
    Selector,
    StratificationMode,
    StratifiedSampler,
    UniformSampler,
)


@pytest.mark.parametrize(
    ("curator_class", "curator_kwargs", "expected_selector"),
    [
        (
            AscendedSortCurator,
            {"sort_field": "ascending_field"},
            Selector(
                method=OrderedSampler(
                    field="ascending_field", sort=DruidDimensionOrderingDirections.ASCENDING
                ),
                limit=10,
            ),
        ),
        (
            DescendedSortCurator,
            {"sort_field": "ascending_field"},
            Selector(
                method=OrderedSampler(
                    field="ascending_field", sort=DruidDimensionOrderingDirections.DESCENDING
                ),
                limit=10,
            ),
        ),
        (
            EqualityCurator,
            {"field": "string_field", "equals": "string"},
            Selector(
                method=UniformSampler(),
                limit=10,
                filters=[EqualsFilter(field="string_field", equals="string")],
            ),
        ),
        (
            NewestCurator,
            {},
            Selector(
                method=OrderedSampler(
                    field="__time", sort=DruidDimensionOrderingDirections.DESCENDING
                ),
                limit=10,
            ),
        ),
        (
            OldestCurator,
            {},
            Selector(
                method=OrderedSampler(
                    field="__time", sort=DruidDimensionOrderingDirections.ASCENDING
                ),
                limit=10,
            ),
        ),
        (
            UniformCurator,
            {},
            Selector(
                method=UniformSampler(),
                limit=10,
            ),
        ),
        (
            StrictStratificationCurator,
            {"stratify_field": "category"},
            Selector(
                method=StratifiedSampler(field="category", mode=StratificationMode.strict),
                limit=10,
            ),
        ),
        (
            BalancedStratificationCurator,
            {"stratify_field": "category"},
            Selector(
                method=StratifiedSampler(field="category", mode=StratificationMode.balanced),
                limit=10,
            ),
        ),
        (
            ProportionalStratificationCurator,
            {"stratify_field": "category"},
            Selector(
                method=StratifiedSampler(field="category", mode=StratificationMode.proportional),
                limit=10,
            ),
        ),
        (
            BoundedRangeCurator,
            {"bound_field": "float_field", "lower_bound": 0.0, "upper_bound": 1.0},
            Selector(
                method=OrderedSampler(
                    field="float_field", sort=DruidDimensionOrderingDirections.ASCENDING
                ),
                limit=10,
                filters=[BoundsFilter(field="float_field", lower=0.0, upper=1.0)],
            ),
        ),
    ],
)
@mock.patch("gantry.automations.curators.globals._API_CLIENT", "fake-api-client")
def test_selectors_preset_curator(curator_class, curator_kwargs, expected_selector):
    curator_kwargs.update(
        {"name": "test_curator_name", "application_name": "test_application_name", "limit": 10}
    )
    curator = curator_class(**curator_kwargs)

    assert curator._selectors[0] == expected_selector


@mock.patch("gantry.automations.curators.globals._API_CLIENT", "fake-api-client")
def test_curator_properties(test_curator):
    curator = Curator(**test_curator)

    assert curator.id == test_curator["id"]
    assert curator.application_name == test_curator["application_name"]
    assert curator.name == test_curator["name"]
    assert curator.curated_dataset_name == test_curator["curated_dataset_name"]
    assert curator.start_on == test_curator["start_on"]
    assert curator.curation_interval == test_curator["curation_interval"]
    assert curator.curate_past_intervals == test_curator["curate_past_intervals"]
    assert curator.created_at == test_curator["created_at"]
    assert curator.selectors == test_curator["selectors"]


@pytest.mark.parametrize(
    ("description", "kwargs"),
    [
        ("negative limit", {"limit": -1}),
        ("too high limit", {"limit": 10001}),
        ("bad filters", {"filters": [1]}),
        ("bad method", {"method": "ascending"}),
    ],
)
def test_invalid_selectors(description, kwargs):
    base_kwargs = {
        "limit": 1,
    }
    base_kwargs.update(kwargs)

    with pytest.raises(pydantic.ValidationError):
        _ = Selector(**base_kwargs)


@pytest.mark.parametrize(
    ("filter_class", "kwargs"),
    [
        (BoundsFilter, {"upper": 10}),
        (EqualsFilter, {"equals": "text"}),
        (EqualsFilter, {"equals": 123.4}),
        (EqualsFilter, {"equals": 5}),
        (EqualsFilter, {"equals": True}),
        (ContainsFilter, {"contains": "test_string"}),
        (BoundsFilter, {"upper": 10, "lower": 0}),
        (BoundsFilter, {"inclusive_upper": 10, "inclusive_lower": 0}),
        (BoundsFilter, {"upper": 10, "inclusive_lower": 0}),
        (BoundsFilter, {"inclusive_upper": 10, "lower": 0}),
    ],
)
def test_valid_filters(filter_class, kwargs):
    base_kwargs = {
        "field": "testfield",
    }
    base_kwargs.update(kwargs)

    constructed_filter = filter_class(**base_kwargs)

    for k, v in base_kwargs.items():
        assert constructed_filter.dict()[k] == v


@pytest.mark.parametrize(
    ("description", "filter_class", "kwargs"),
    [
        ("no bounds", BoundsFilter, {}),
        ("no equals value", EqualsFilter, {}),
        ("no contains value", ContainsFilter, {}),
        ("too many upper bounds", BoundsFilter, {"upper": 10, "inclusive_upper": 10}),
        ("too many lower bounds", BoundsFilter, {"lower": 10, "inclusive_lower": 10}),
    ],
)
def test_invalid_filters(description, filter_class, kwargs):
    base_kwargs = {
        "field": "testfield",
    }
    base_kwargs.update(kwargs)

    with pytest.raises(pydantic.ValidationError):
        _ = filter_class(**base_kwargs)

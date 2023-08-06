import json

import mock
import pandas as pd
import pytest
import responses
from pandas.testing import assert_frame_equal
from responses import matchers

from gantry.exceptions import GantryException, QueryError
from gantry.query.core import dataframe
from gantry.query.core.queryframe import QueryInfo

from ..conftest import END_TIME, MULTIPLE_FEATURES_INT_DATA, ORIGIN, START_TIME


def test_series_filters_property_getter(series_obj_factory, api_client_obj, query_info_obj):
    filters = ["filter-1", "filter-2", "filter-3"]
    parent_dataframe = mock.Mock(api_client=api_client_obj, query_info=query_info_obj)
    parent_dataframe.filters = filters

    series_obj = series_obj_factory("str", parent_dataframe=parent_dataframe)
    assert series_obj.filters == filters


@pytest.mark.parametrize("num_points_kwargs", [{}, {"num_points": 1}, {"num_points": 10}])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_mean(mock_query, num_points_kwargs, series_obj):
    mock_query.return_value = 0.5
    assert series_obj.mean(**num_points_kwargs) == 0.5
    mock_query.assert_called_once_with(
        "mean", num_points=num_points_kwargs.get("num_points", 1), group_by=None
    )


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_mean_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.mean()
    mock_query.assert_called_once_with("mean", num_points=1, group_by=None)


@pytest.mark.parametrize("num_points_kwargs", [{}, {"num_points": 1}, {"num_points": 10}])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_std(mock_query, num_points_kwargs, series_obj):
    mock_query.return_value = 0.6
    assert series_obj.std(**num_points_kwargs) == 0.6
    mock_query.assert_called_once_with(
        "stddev", num_points=num_points_kwargs.get("num_points", 1), group_by=None
    )


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_std_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.std()
    mock_query.assert_called_once_with("stddev", num_points=1, group_by=None)


@pytest.mark.parametrize("num_points_kwargs", [{}, {"num_points": 1}, {"num_points": 10}])
@mock.patch("gantry.query.core.dataframe.GantrySeries.quantile")
def test_median(mock_query, num_points_kwargs, series_obj):
    mock_query.return_value = {0.5: 0.7}
    assert series_obj.median(**num_points_kwargs) == 0.7
    mock_query.assert_called_once_with([0.5], num_points=num_points_kwargs.get("num_points", 1))


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries.quantile")
def test_median_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.median()
    mock_query.assert_called_once_with([0.5], num_points=1)


@pytest.mark.parametrize("num_points_kwargs", [{}, {"num_points": 1}, {"num_points": 10}])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_count(mock_query, num_points_kwargs, series_obj):
    mock_query.return_value = 100
    assert series_obj.count(**num_points_kwargs) == 100
    mock_query.assert_called_once_with(
        "total", num_points=num_points_kwargs.get("num_points", 1), group_by=None
    )


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_len(mock_query, series_obj):
    mock_query.return_value = 100
    assert len(series_obj) == 100
    mock_query.assert_called_once_with("total", num_points=1, group_by=None)


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_count_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.count()
    mock_query.assert_called_once_with("total", num_points=1, group_by=None)


@pytest.mark.parametrize("num_points_kwargs", [{}, {"num_points": 1}, {"num_points": 10}])
@pytest.mark.parametrize("datatype", ["int", "float"])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_min(mock_query, datatype, num_points_kwargs, series_obj_factory):
    series_obj = series_obj_factory(datatype)
    mock_query.return_value = 1
    assert series_obj.min(**num_points_kwargs) == 1
    mock_query.assert_called_once_with(
        "minimum", num_points=num_points_kwargs.get("num_points", 1), group_by=None
    )


@pytest.mark.parametrize("invalid_datatype", ["str", "bool", "category"])
def test_min_invalid_datatype(invalid_datatype, series_obj_factory):
    with pytest.raises(ValueError):
        series_obj = series_obj_factory(invalid_datatype)
        _ = series_obj.min()


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_min_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.min()
    mock_query.assert_called_once_with("minimum", num_points=1, group_by=None)


@pytest.mark.parametrize("num_points_kwargs", [{}, {"num_points": 1}, {"num_points": 10}])
@pytest.mark.parametrize("datatype", ["int", "float"])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_max(mock_query, datatype, num_points_kwargs, series_obj_factory):
    series_obj = series_obj_factory(datatype)
    mock_query.return_value = 1000
    assert series_obj.max(**num_points_kwargs) == 1000
    mock_query.assert_called_once_with(
        "maximum", num_points=num_points_kwargs.get("num_points", 1), group_by=None
    )


@pytest.mark.parametrize("invalid_datatype", ["str", "bool", "category"])
def test_max_invalid_datatype(invalid_datatype, series_obj_factory):
    with pytest.raises(ValueError):
        series_obj = series_obj_factory(invalid_datatype)
        _ = series_obj.max()


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_max_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.max()
    mock_query.assert_called_once_with("maximum", num_points=1, group_by=None)


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_histogram(mock_query, series_obj):
    mock_query.return_value = {"a": 10}
    assert series_obj.histogram() == {"a": 10}
    mock_query.assert_called_once_with("category_percents")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_histogram_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.histogram()
    mock_query.assert_called_once_with("category_percents")


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_unique(mock_query, series_obj_str):
    mock_query.return_value = {"a": 10, "b": -10, "c": None}
    assert series_obj_str.unique() == set(["a", "b", "c"])
    mock_query.assert_called_once_with("category_percents")


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_unique_b(mock_query, series_obj_bool):
    mock_query.return_value = {"t": 10, "f": -10}
    assert series_obj_bool.unique() == set(["t", "f"])
    mock_query.assert_called_once_with("category_percents")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_unique_error(mock_query, error, series_obj_bool):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj_bool.unique()
    mock_query.assert_called_once_with("category_percents")


@pytest.mark.parametrize("vals", [[0.5], [1, 2, 3], []])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_quantile(mock_query, vals, series_obj):
    mock_query.return_value = {1: 10}
    assert series_obj.quantile(vals) == {1.0: 10}
    mock_query.assert_called_once_with("quantiles", quantile_vals=vals)


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_quantile_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.quantile()


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_pdf(mock_query, series_obj):
    mock_query.return_value = [1, 2, 3]
    pd.testing.assert_frame_equal(series_obj.pdf(), pd.DataFrame([1, 2, 3]))
    mock_query.assert_called_once_with("pdf")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_pdf_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.pdf()
    mock_query.assert_called_once_with("pdf")


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_cdf(mock_query, series_obj):
    mock_query.return_value = [1, 2, 3]
    pd.testing.assert_frame_equal(series_obj.cdf(), pd.DataFrame([1, 2, 3]))
    mock_query.assert_called_once_with("cdf")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_cdf_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.cdf()
    mock_query.assert_called_once_with("cdf")


def test_dtype(series_obj):
    assert series_obj._dtype() == "int"


@pytest.mark.parametrize("tags", [{}, {"foo": "bar"}])
@pytest.mark.parametrize("filters", [[], [{"some": "filter"}]])
@pytest.mark.parametrize(
    "group_by_info",
    [
        (None, "str"),
        ("proj_datanode", "intC"),
        ("feed_datanode", "intB"),
        ("column-missing-from-schema", None),
    ],
)
@mock.patch("gantry.query.core.dataframe._raw_query_cached_request")
def test_aggregate_query(
    mock_query_data, series_obj_factory_with_filters_and_tags, filters, tags, group_by_info
):
    group_by = group_by_info[0]
    group_by_type = group_by_info[1]
    content_dict = {
        "start_time": "2008-09-03T20:56:35",
        "end_time": "2008-09-10T23:58:23",
        "version": "1.2.3",
        "num_points": 1,
        "queries": {
            "query": {
                "query_type": "feature",
                "model_node_id": "ABCD1234",
                "stat": "some-attribute",
                "stat_kwargs": {"some-attribute": {"a": 10}},
                "feature": "series_name",
                "filters": filters,
                "tags": tags,
            }
        },
    }
    if group_by is not None:
        content_dict["queries"]["query"]["group_by"] = [
            {"feature_name": group_by, "dtype": group_by_type}
        ]
        mock_query_data.return_value = {
            "response": "ok",
            "data": {
                "query": [
                    {
                        "group": [{"feature_name": group_by, "value": "group_by_unique_val1"}],
                        "some-attribute": 9,
                    },
                    {
                        "group": [{"feature_name": group_by, "value": "group_by_unique_val2"}],
                        "some-attribute": 11,
                    },
                ]
            },
        }
    else:
        mock_query_data.return_value = {"response": "ok", "data": {"query": {"some-attribute": 10}}}
    content = json.dumps(content_dict, default=lambda x: x.isoformat())

    series_obj = series_obj_factory_with_filters_and_tags("int", filters=filters, tags=tags)

    if group_by_type is not None:
        result = series_obj._aggregate_query("some-attribute", a=10, group_by=group_by)
        mock_query_data.assert_called_with(series_obj.api_client, content, resource="aggregate")
        if group_by is None:
            assert result == 10
        else:
            assert result["some-attribute"].sum() == 20
            assert len(result) == 2
    else:
        with pytest.raises(ValueError, match=f"Cannot find column {group_by} in dataframe."):
            result = series_obj._aggregate_query("some-attribute", a=10, group_by=group_by)


@pytest.mark.parametrize("num_points", [2, 5, 10])
@pytest.mark.parametrize("tags", [{}, {"foo": "bar"}])
@pytest.mark.parametrize("filters", [[], [{"some": "filter"}]])
@mock.patch("gantry.query.core.dataframe._raw_query_cached_request")
def test_aggregate_query_num_points(
    mock_query_data, series_obj_factory_with_filters_and_tags, filters, tags, num_points
):
    content = json.dumps(
        {
            "start_time": "2008-09-03T20:56:35",
            "end_time": "2008-09-10T23:58:23",
            "version": "1.2.3",
            "num_points": num_points,
            "queries": {
                "query": {
                    "query_type": "feature",
                    "model_node_id": "ABCD1234",
                    "stat": "some-attribute",
                    "stat_kwargs": {"some-attribute": {"a": 10}},
                    "feature": "series_name",
                    "filters": filters,
                    "tags": tags,
                }
            },
        },
        default=lambda x: x.isoformat(),
    )
    series_obj = series_obj_factory_with_filters_and_tags("int", filters=filters, tags=tags)
    mock_query_data.return_value = {
        "response": "ok",
        "data": {"query": {"points": [{"A": 10, "B": 10}, {"A": 20, "B": 20}]}},
    }

    res = series_obj._aggregate_query("some-attribute", num_points=num_points, a=10)
    assert_frame_equal(res, pd.DataFrame([{"A": 10, "B": 10}, {"A": 20, "B": 20}]))

    mock_query_data.assert_called_with(series_obj.api_client, content, resource="time_series")


@pytest.mark.parametrize("tags", [{}, {"foo": "bar"}])
@pytest.mark.parametrize("filters", [[], [{"some": "filter"}]])
def test_aggregate_query_error(series_obj_factory_with_filters_and_tags, filters, tags):
    series_obj = series_obj_factory_with_filters_and_tags("int", filters=filters, tags=tags)

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/aggregate/query".format(ORIGIN),
            json={"response": "bad", "data": {"query": {"some-attribute": 10}}},
            status=400,
        )
        with pytest.raises(
            GantryException,
            match=r"Aggregation query \[some-attribute\] failed: .+",
        ):
            _ = series_obj._aggregate_query("some-attribute", a=10)


@pytest.mark.parametrize("invalid_num_points", [0, -1, -100])
def test_aggregate_query_error_num_points(invalid_num_points, series_obj_factory):
    series_obj = series_obj_factory("int")
    with pytest.raises(
        ValueError,
    ):
        _ = series_obj._aggregate_query("some-attribute", num_points=invalid_num_points, a=10)


def test_raw_query_cached_request_default_resource(api_client_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/aggregate/query".format(ORIGIN),
            json={"response": "ok", "data": "100"},
            match=[matchers.json_params_matcher({"foo": "bar"})],
        )
        assert dataframe._raw_query_cached_request(api_client_obj, '{"foo": "bar"}') == {
            "response": "ok",
            "data": "100",
        }


def test_raw_query_cached_request_provided_resource(api_client_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/foobar/query".format(ORIGIN),
            json={"response": "ok", "data": "100"},
            match=[matchers.json_params_matcher({"foo": "bar"})],
        )
        assert dataframe._raw_query_cached_request(
            api_client_obj, '{"foo": "bar"}', resource="foobar"
        ) == {
            "response": "ok",
            "data": "100",
        }


@pytest.mark.parametrize("op", ["__eq__", "__gt__", "__lt__", "__ge__", "__le__"])
@pytest.mark.parametrize("invalid_filter", [[1, 2, 3], {"foo": "bar"}, object()])
def test_comparator_invalid_filter(invalid_filter, op, series_obj):
    with pytest.raises(TypeError):
        getattr(series_obj, op)(invalid_filter)


@pytest.mark.parametrize("op", ["__eq__", "__gt__", "__lt__", "__ge__", "__le__"])
def test_comparator_invalid_filter_special_case_series(op, series_obj):
    with pytest.raises(TypeError, match=r"Series cannot be compared to each other directly*"):
        getattr(series_obj, op)(series_obj)


@pytest.mark.parametrize(
    ["method", "invalid_dtypes"],
    [
        ("__gt__", ["bool", "str"]),
        ("__ge__", ["bool", "str"]),
        ("__lt__", ["bool", "str"]),
        ("__le__", ["bool", "str"]),
        ("isin", ["bool"]),
        ("contains", ["bool"]),
    ],
)
def test_comparator_invalid_type(method, invalid_dtypes, series_obj_factory):
    for invalid_dtype in invalid_dtypes:
        series_obj = series_obj_factory(invalid_dtype)
        with pytest.raises(ValueError):
            getattr(series_obj, method)(mock.Mock())


@pytest.mark.parametrize(
    ["method", "expected_filter"],
    [
        ("__gt__", "lower_bound"),
        ("__ge__", "inclusive_lower_bound"),
        ("__lt__", "upper_bound"),
        ("__le__", "inclusive_upper_bound"),
    ],
)
def test_valid_sortable_comparators(method, expected_filter, series_obj_factory):
    series_obj = series_obj_factory(
        "int", parent_dataframe=mock.Mock(filters=[], tags={"foo": "bar"})
    )
    value = 10
    result = getattr(series_obj, method)(value)
    assert [f.filter_ for f in result.filter_objs] == [
        {expected_filter: value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]
    assert [f.series.parent_dataframe.tags for f in result.filter_objs] == [{"foo": "bar"}]


def test_isin(series_obj_factory):
    series_obj = series_obj_factory(
        "str", parent_dataframe=mock.Mock(filters=[], tags={"foo": "bar"})
    )
    value = ["foo"]
    result = series_obj.isin(value)
    assert [f.filter_ for f in result.filter_objs] == [
        {"category_query": value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]
    assert [f.series.parent_dataframe.tags for f in result.filter_objs] == [{"foo": "bar"}]


def test_contains(series_obj_factory):
    series_obj = series_obj_factory(
        "str", parent_dataframe=mock.Mock(filters=[], tags={"foo": "bar"})
    )
    value = "foo"
    result = series_obj.contains(value)
    assert [f.filter_ for f in result.filter_objs] == [
        {"string_query": value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]
    assert [f.series.parent_dataframe.tags for f in result.filter_objs] == [{"foo": "bar"}]


@pytest.mark.parametrize("invalid_key", [object(), 1.2, 123, "some-value"])
def test_getitem_invalid_key(invalid_key, series_obj):
    with pytest.raises(ValueError):
        series_obj[invalid_key]


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def test_getitem(get_application_node_id_mock, metadata, series_obj_factory, api_client_obj):
    get_application_node_id_mock.return_value = "12345"
    df = dataframe.GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
        tags={"foo": "bar"},
    )

    series_obj = series_obj_factory("int", df, name="A")
    assert series_obj.parent_dataframe.tags == {"foo": "bar"}

    filters = dataframe.Filters._from_single_filter({"foo": "bar"}, series_obj)

    new_series = series_obj[filters]
    assert new_series.name == "A"
    assert new_series.parent_dataframe.tags == {"foo": "bar"}


@pytest.mark.parametrize(
    ["type_", "expected"],
    [
        ("bool", "boolean_query"),
        ("str", "string_query"),
        ("uuid", "string_query"),
        ("int", "equals"),
        ("float", "equals"),
    ],
)
def test_eq(type_, expected, series_obj_factory):
    series_obj = series_obj_factory(
        type_, parent_dataframe=mock.Mock(filters=[], tags={"foo" "bar"})
    )
    value = 10
    result = series_obj == value
    assert [f.filter_ for f in result.filter_objs] == [
        {expected: value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]


@pytest.mark.parametrize(
    ["type_", "expected", "other", "value"],
    [
        ("bool", "boolean_query", True, False),
        ("str", "string_query", "str", "^(?!(str)$).*$"),
        ("uuid", "string_query", "str", "^(?!(str)$).*$"),
        ("int", "not_number_query", "not_none", "not_none"),
        ("float", "not_number_query", "not_none", "not_none"),
    ],
)
def test_ne(type_, expected, other, value, series_obj_factory):
    series_obj = series_obj_factory(
        type_, parent_dataframe=mock.Mock(filters=[], tags={"foo": "bar"})
    )
    result = series_obj != other
    assert [f.filter_ for f in result.filter_objs] == [
        {expected: value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]


@pytest.mark.parametrize(
    ["method", "dtype", "query_type", "value"],
    [
        ("__invert__", "bool", "boolean_query", False),
        ("notnull", "any", "null_value", False),
        ("isnull", "any", "null_value", True),
    ],
)
def test_unary(method, dtype, query_type, value, series_obj_factory):
    series_obj = series_obj_factory(
        dtype, parent_dataframe=mock.Mock(filters=[], tags={"foo": "bar"})
    )
    result = getattr(series_obj, method)()
    assert [f.filter_ for f in result.filter_objs] == [
        {query_type: value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]


@pytest.mark.parametrize("dtype", ["str", "int", "float", "other"])
def test_invalid__invert__(dtype, series_obj_factory):
    series_obj = series_obj_factory(dtype)
    with pytest.raises(ValueError):
        series_obj.__invert__()


@pytest.mark.parametrize(["method", "other"], [("__eq__", None), ("__ne__", None)])
def test_other_is_none__eq___and__ne__(method, other, series_obj_factory):
    series_obj = series_obj_factory("any")
    with pytest.raises(ValueError):
        getattr(series_obj, method)(other)


@pytest.mark.parametrize("method", ["__eq__", "__ne__"])
def test_cannot_compare_type__eq___and__ne__(method, series_obj_factory):
    series_obj = series_obj_factory("any")
    with pytest.raises(ValueError):
        getattr(series_obj, method)("not_none")


def test_filter_builder(series_obj_factory):
    series_obj = series_obj_factory(
        "int", parent_dataframe=mock.Mock(filters=[{"bar": "baz"}], tags={"foo": "bar"})
    )
    res = series_obj._filter_builder("foo", "bar")
    assert [f.filter_ for f in res.filter_objs] == [{"feature_name": "series_name", "foo": "bar"}]
    assert [f.series.parent_dataframe for f in res.filter_objs] == [series_obj.parent_dataframe]
    assert series_obj.parent_dataframe.filters == [{"bar": "baz"}]
    assert series_obj.parent_dataframe.tags == {"foo": "bar"}


@pytest.mark.parametrize("n", [1, 5, 10, 11])
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._prepare_pandas_dataframe")
def test_head(mock_df, mock_data, n, series_obj_factory):
    series_obj = series_obj_factory(
        "int", parent_dataframe=mock.Mock(filters=[], tags={"foo": "bar"})
    )
    total_num_events = 10
    all_events = list(range(total_num_events))
    mock_data.return_value = all_events[:n]
    mock_df.return_value = pd.DataFrame({"foo": mock_data.return_value})
    pd.testing.assert_frame_equal(series_obj.head(n), mock_df.return_value)
    mock_data.assert_called_with(query_filters=[], ascending=True, n=n, tags={"foo": "bar"})


@pytest.mark.parametrize("n", [1, 5, 10, 11])
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._prepare_pandas_dataframe")
def test_tail(mock_df, mock_data, n, series_obj_factory):
    series_obj = series_obj_factory(
        "int", parent_dataframe=mock.Mock(filters=[], tags={"foo": "bar"})
    )
    total_num_events = 10
    all_events = list(range(total_num_events))
    mock_data.return_value = all_events[-n:]
    mock_df.return_value = pd.DataFrame({"foo": mock_data.return_value})
    pd.testing.assert_frame_equal(series_obj.tail(n), mock_df.return_value)
    mock_data.assert_called_with(query_filters=[], ascending=False, n=n, tags={"foo": "bar"})


@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._prepare_pandas_dataframe")
def test_fetch(mock_df, mock_data, series_obj_factory):
    series_obj = series_obj_factory(
        "int", parent_dataframe=mock.Mock(filters=[], tags={"foo": "bar"})
    )
    total_num_events = 10
    all_events = list(range(total_num_events))
    mock_data.return_value = all_events
    mock_df.return_value = pd.DataFrame({"foo": mock_data.return_value})
    pd.testing.assert_frame_equal(series_obj.fetch(), mock_df.return_value)
    mock_data.assert_called_with(query_filters=[], ascending=True, n=None, tags={"foo": "bar"})


@mock.patch("gantry.query.core.dataframe.GantrySeries._describe")
def test_describe(mock_series_describe, series_obj_factory):
    series_obj = series_obj_factory(
        "int",
        parent_dataframe=mock.Mock(
            query_info=QueryInfo("123", "foo", "0", "dev", START_TIME, END_TIME)
        ),
    )
    mock_series_describe.return_value = {"foo": "bar"}

    df = pd.DataFrame(
        ["foo", START_TIME, END_TIME, "bar"],
        index=["application", "from", "to", "foo"],
        columns=["series_name"],
    )
    assert_frame_equal(series_obj.describe(), df)


@pytest.mark.parametrize("dtype", ["int", "float"])
@mock.patch("gantry.query.core.dataframe.GantrySeries.__getitem__")
@mock.patch("gantry.query.core.dataframe.GantrySeries.mean")
@mock.patch("gantry.query.core.dataframe.GantrySeries.max")
@mock.patch("gantry.query.core.dataframe.GantrySeries.min")
@mock.patch("gantry.query.core.dataframe.GantrySeries.quantile")
def test_private_describe_number(
    mock_quantile,
    mock_min,
    mock_max,
    mock_mean,
    mock_get_item,
    dtype,
    series_obj_factory,
):
    series_obj = series_obj_factory(dtype, parent_dataframe=mock.Mock(filters=[]))

    mock_quantile.return_value = {0.25: 0.24, 0.5: 0.4, 0.75: 0.7}
    mock_get_item.return_value = series_obj
    mock_min.return_value = 1
    mock_max.return_value = 10
    mock_mean.return_value = 5

    series_obj.count.side_effect = [100, 1000, 10000]

    assert series_obj._describe() == {
        "count": 100,
        "max": 10,
        "mean": 5,
        "min": 1,
        "not null count": 1000,
        "null count": 10000,
        "q25": 0.24,
        "q50": 0.4,
        "q75": 0.7,
        "series type": "prediction",
        "type": dtype,
    }


@mock.patch("gantry.query.core.dataframe.GantrySeries.__getitem__")
def test_private_describe_bool(
    mock_get_item,
    series_obj_factory,
):
    series_obj = series_obj_factory("bool", parent_dataframe=mock.Mock(filters=[]))

    mock_get_item.return_value = series_obj
    series_obj.count.side_effect = [100, 1000, 10000, 50000]

    assert series_obj._describe() == {
        "count": 100,
        "not null count": 1000,
        "null count": 10000,
        "series type": "prediction",
        "type": "bool",
        "True rate": 500,
    }


@mock.patch("gantry.query.core.dataframe.GantrySeries.__getitem__")
def test_private_describe_str(
    mock_get_item,
    series_obj_factory,
):
    series_obj = series_obj_factory("str", parent_dataframe=mock.Mock(filters=[]))

    mock_get_item.return_value = series_obj
    series_obj.count.side_effect = [100, 1000, 10000]

    assert series_obj._describe() == {
        "count": 100,
        "not null count": 1000,
        "null count": 10000,
        "series type": "prediction",
        "type": "str",
    }


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def test_mix_filtering(get_application_node_id_mock, metadata, series_obj_factory, api_client_obj):
    get_application_node_id_mock.return_value = "12345"
    df = dataframe.GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
        tags={"foo": "bar"},
    )
    s1 = series_obj_factory("int", df, name="A")
    s2 = series_obj_factory("int", df, name="B")

    series = s1[s2 > 20]
    assert series.name == "A"
    assert series.parent_dataframe.filters == [{"feature_name": "B", "lower_bound": 20}]
    assert series.parent_dataframe.tags == {"foo": "bar"}


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def test_compose_filtering(
    get_application_node_id_mock, metadata, series_obj_factory, api_client_obj
):
    get_application_node_id_mock.return_value = "12345"
    df = dataframe.GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
        tags={"foo": "bar"},
    )

    s1 = series_obj_factory("int", parent_dataframe=df, name="A")
    s2 = s1[s1 > 20]
    s3 = s2[s2 < 10]

    # < 20 and < 10 filters
    assert s3.parent_dataframe.filters == [
        {"feature_name": "A", "lower_bound": 20},
        {"feature_name": "A", "upper_bound": 10},
    ]
    assert s3.parent_dataframe.tags == {"foo": "bar"}


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_percent_null(mock_query, series_obj_bool):
    mock_query.return_value = 50.0
    assert series_obj_bool.percent_null() == 50.0
    mock_query.assert_called_once_with("percent_null", num_points=1, group_by=None)


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_percent_null_error(mock_query, error, series_obj_bool):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj_bool.percent_null()
    mock_query.assert_called_once_with("percent_null", num_points=1, group_by=None)


@mock.patch("gantry.query.core.dataframe.GantrySeries._filter_builder")
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@pytest.mark.parametrize("dropna", [True, False])
def test_percent_true(
    metadata,
    get_application_node_id_mock,
    mock_query,
    mock_na,
    series_obj_bool,
    dropna,
    api_client_obj,
):
    get_application_node_id_mock.return_value = "12345"
    df = dataframe.GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
        tags={"foo": "bar"},
    )

    series_obj_bool.parent_dataframe = df

    filters = dataframe.Filters._from_single_filter({"foo": "bar"}, series_obj_bool)
    mock_query.return_value = 50.0
    mock_na.return_value = filters
    assert series_obj_bool.percent_true(dropna=dropna) == 50.0
    mock_query.assert_called_once_with("percent_true", num_points=1, group_by=None)
    if dropna:
        mock_na.assert_called_once_with("null_value", False)


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_percent_true_error(mock_query, error, series_obj_bool):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj_bool.percent_true()
    mock_query.assert_called_once_with("percent_true", num_points=1, group_by=None)


@mock.patch("gantry.query.core.dataframe.GantrySeries._filter_builder")
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@pytest.mark.parametrize("dropna", [True, False])
def test_percent_false(
    metadata,
    get_application_node_id_mock,
    mock_query,
    mock_na,
    series_obj_bool,
    dropna,
    api_client_obj,
):
    get_application_node_id_mock.return_value = "12345"
    df = dataframe.GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
        tags={"foo": "bar"},
    )

    series_obj_bool.parent_dataframe = df

    filters = dataframe.Filters._from_single_filter({"foo": "bar"}, series_obj_bool)
    mock_query.return_value = 50.0
    mock_na.return_value = filters
    assert series_obj_bool.percent_false(dropna=dropna) == 50.0
    mock_query.assert_called_once_with("percent_false", num_points=1, group_by=None)
    if dropna:
        mock_na.assert_called_once_with("null_value", False)


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_percent_false_error(mock_query, error, series_obj_bool):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj_bool.percent_false()
    mock_query.assert_called_once_with("percent_false", num_points=1, group_by=None)

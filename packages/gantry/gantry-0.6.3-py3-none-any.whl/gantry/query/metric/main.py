from gantry.query import globals
from gantry.query.client import GantryQuery
from gantry.query.globals import _query_alias, validate_init


@_query_alias
def accuracy_score(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.accuracy_score(*args, **kwargs)


@_query_alias
def mean_squared_error(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.mean_squared_error(*args, **kwargs)


@_query_alias
def confusion_matrix(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.confusion_matrix(*args, **kwargs)


@_query_alias
def f1_score(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.f1_score(*args, **kwargs)


@_query_alias
def r2_score(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.r2_score(*args, **kwargs)


@_query_alias
def precision_score(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.precision_score(*args, **kwargs)


@_query_alias
def recall_score(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.recall_score(*args, **kwargs)


@_query_alias
def roc_auc_score(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.roc_auc_score(*args, **kwargs)


@_query_alias
def percent_null(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.percent_null(*args, **kwargs)


@_query_alias
def percent_true(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.percent_true(*args, **kwargs)


@_query_alias
def percent_false(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.percent_false(*args, **kwargs)

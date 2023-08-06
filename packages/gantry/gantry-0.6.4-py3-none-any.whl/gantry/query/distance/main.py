from gantry.query import globals
from gantry.query.client import GantryQuery
from gantry.query.globals import _query_alias, validate_init


@_query_alias
def d1(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.distance.d1(*args, **kwargs)


@_query_alias
def dinf(*args, **kwargs):
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.distance.dinf(*args, **kwargs)


@_query_alias
def ks(*args, **kwargs) -> float:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.distance.ks(*args, **kwargs)


@_query_alias
def kl(*args, **kwargs) -> float:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.distance.kl(*args, **kwargs)

from enum import Enum
from typing import List, Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

from pydantic import BaseModel, root_validator, validator

# Database constraint
MAX_NAME_LEN = 255
TIME_COLUMN_NAME = "__time"


class DruidDimensionOrderingDirections(str, Enum):
    """
    Direction specifiying how to order a dimension in a Druid query.

    https://druid.apache.org/docs/latest/querying/limitspec.html
    """

    ASCENDING = "ascending"
    DESCENDING = "descending"


class SamplingMethod(str, Enum):
    """
    Sampling method to use when selecting a subset of data.

    Selected data will be sampled using one of the methods enumerated here.
    """

    uniform = "uniform"
    ordered = "ordered"
    stratified = "stratified"


class StratificationMode(str, Enum):
    """
    Stratification mode to use when selecting a subset of data. Currently,
    stratification is only supported for categorical data.

    Selected data will be stratified using one of the modes enumerated here.

    In "strict" mode, the limit of records per curation is respected, but the proportion of records
    in each stratum may be violated, unlike the ProportionalStratificationCurator, which will
    respect the proportion at the (potential) cost of violating the limit per curation.

    Additionally, it is worth noting that the number of records to be added to each stratum
    is calulated exactly, leading to poentially fractional assignments. The integer part
    of the assignment is taken, and the total remainder is added, up to the limit, randomly.

    Example:
        Let's say there are 100 records: 51 records with the value "A" for the field, 15
        records with the value "B" for the field, and 16 records with the value "C" for the
        field, 17 records with the value "D" for the field, and 1 record with the value "E".

        If the limit is 10, then the curator will return 10 records, with 5 records with the
        value "A" for the field, 1 record with "B" for the field, 1 record with "C" for the
        field, 1 record with "D" for the field, 0 records with "E" for the field, and the
        remaining 2 records will be randomly selected from the remaining records.

    In "proportional" mode, the proportion of records in each stratum is respected,
    but the limit per curation may be violated, unlike the StrictStratificationCurator,
    which will respect the limit at the (potential) cost of violating the proportion of
    records in each stratum.

    Additionally, it is worth noting that proportions are rounded to even numbers, so
    1.5 will be rounded to 2, and 0.5 will be rounded to 0.

    Example:
        Let's say there are 100 records: 51 records with the value "A" for the field, 15
        records with the value "B" for the field, and 16 records with the value "C" for the
        field, 17 records with the value "D" for the field, and 1 record with the value "E".

        If the limit is 10, then the curator will return 11 records, with 5 records with the
        value "A" for the field, 2 records with the value "B" for the field, 2 records with
        the value "C" for the field, 2 records with the value "D" for the field, and 0 records
        with the value "E".

    In "balanced" mode, the number of records per stratum is balanced with respect to the
    least represented stratum.
    """

    strict = "strict"
    proportional = "proportional"
    balanced = "balanced"


class TagFilter(BaseModel):
    """Filter for tags"""

    name: str
    value: str


class Filter(BaseModel):
    """Base class for filters. All filters must have a field."""

    field: str


class BoundsFilter(Filter):
    """
    Filter for bounds. Must have either an upper or lower bound; both
    can be specified. Default bounds are exclusive, but inclusive bounds
    can be given instead.
    """

    upper: Optional[Union[float, int]] = None
    inclusive_upper: Optional[Union[float, int]] = None
    lower: Optional[Union[float, int]] = None
    inclusive_lower: Optional[Union[float, int]] = None

    @root_validator
    def validate_bounds(cls, values):
        if (
            values["upper"] is None
            and values["lower"] is None
            and values["inclusive_upper"] is None
            and values["inclusive_lower"] is None
        ):
            raise ValueError("Must have either an upper or lower bound")
        if values["upper"] is not None and values["inclusive_upper"] is not None:
            raise ValueError("Cannot have inclusive and exclusive upper bound")
        if values["lower"] is not None and values["inclusive_lower"] is not None:
            raise ValueError("Cannot have inclusive and exclusive lower bound")

        return values


class EqualsFilter(Filter):
    """
    Filter for equality. Must have an equals field.

    The equals field can be a boolean, string, float, or int.
    """

    equals: Union[bool, float, int, str]


class ContainsFilter(Filter):
    """
    Filter for string containment. The specified field
    must be a string.
    """

    contains: str


ALL_FILTERS_T = Union[BoundsFilter, EqualsFilter, ContainsFilter]


class Sampler(BaseModel):
    """Base class for samplers."""

    pass


class UniformSampler(Sampler):
    """
    Sampler for uniform sampling.

    This sampler will select a subset of the data uniformly at random.
    """

    sample: Literal[SamplingMethod.uniform] = SamplingMethod.uniform


class OrderedSampler(Sampler):
    """
    Sampler for ordered sampling.

    This sampler will select a subset of the data ordered by the specified field.
    Fields can be ordered in ascending or descending order.
    """

    sample: Literal[SamplingMethod.ordered] = SamplingMethod.ordered
    field: str
    sort: Literal[
        DruidDimensionOrderingDirections.ASCENDING, DruidDimensionOrderingDirections.DESCENDING
    ]


class StratifiedSampler(Sampler):
    """
    Sampler for stratified sampling.

    This sampler will select a subset of the data stratified by the specified field.
    Stratification is only supported for categorical data. The mode specifies how to
    stratify the data. See the documentation for StratificationMode for more details.
    """

    field: str
    sample: Literal[SamplingMethod.stratified] = SamplingMethod.stratified
    mode: Literal[
        StratificationMode.strict, StratificationMode.proportional, StratificationMode.balanced
    ] = StratificationMode.proportional


ALL_METHODS_T = Union[OrderedSampler, UniformSampler, StratifiedSampler]


class Selector(BaseModel):
    """
    Base class for selectors. All selectors must have a method and a limit. The
    method specifies how to select a subset of the data, and the limit specifies
    the number of records to select. The filters field specifies any filters to
    apply to the data before selecting a subset.
    """

    method: ALL_METHODS_T = OrderedSampler(
        sample=SamplingMethod.ordered,
        field=TIME_COLUMN_NAME,
        sort=DruidDimensionOrderingDirections.DESCENDING,
    )
    limit: int
    filters: List[ALL_FILTERS_T] = []
    tags: List[TagFilter] = []

    @validator("limit")
    def validate_limit(cls, value):
        if value <= 0:
            raise ValueError("Limit must be strictly positive")
        if value > 10_000:
            raise ValueError(
                "Currently, curation limit must not exceed 10,000 records per interval"
            )

        return value

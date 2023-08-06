import datetime
from typing import Optional, Union

from gantry.automations.curators.curators import Curator
from gantry.automations.curators.selectors import (
    TIME_COLUMN_NAME,
    BoundsFilter,
    DruidDimensionOrderingDirections,
    EqualsFilter,
    OrderedSampler,
    Selector,
    StratificationMode,
    StratifiedSampler,
    UniformSampler,
)


class UniformCurator(Curator):
    """
    Stock Curator that uniformly samples application records and adds up to the
    top limit results to curated_dataset_name every curation_interval.
    """

    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
    ):
        """

        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[Selector(method=UniformSampler(), limit=limit)],
        )


class NewestCurator(Curator):
    """
    Stock Curator that sorts the application records in descending time-order according
    to the internally logged Gantry timestamp, `__TIME`, and adds up to the top limit
    results to curated_dataset_name every curation_interval.
    """

    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
    ):
        """

        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[
                Selector(
                    method=OrderedSampler(
                        field=TIME_COLUMN_NAME,
                        sort=DruidDimensionOrderingDirections.DESCENDING,
                    ),
                    limit=limit,
                )
            ],
        )


class OldestCurator(Curator):
    """
    Stock Curator that sorts the application records in ascending time-order according
    to the internally logged Gantry timestamp, `__TIME`, and adds up to the top limit
    results to curated_dataset_name every curation_interval.

    """

    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
    ):
        """

        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[
                Selector(
                    method=OrderedSampler(
                        field=TIME_COLUMN_NAME,
                        sort=DruidDimensionOrderingDirections.ASCENDING,
                    ),
                    limit=limit,
                )
            ],
        )


class BalancedStratificationCurator(Curator):
    """
    Stock Curator that builds a balanced stratification of application records according
    to the field stratify_field and adds up to limit results to curated_dataset_name.

    Currently, this curator only supports stratification of categorical fields. And the limit
    per stratum is determineed by the stratum with the fewest records in the current
    curation_interval.

    """

    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        stratify_field: str,
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
    ):
        """
        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            stratify_field (str): The field to stratify.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[
                Selector(
                    method=StratifiedSampler(
                        field=stratify_field,
                        mode=StratificationMode.balanced,
                    ),
                    limit=limit,
                ),
            ],
        )


class ProportionalStratificationCurator(Curator):
    """
    Stock Curator that builds a proportional stratification of application records
    according to the field stratify_field and adds up to limit results to
    curated_dataset_name.

    The proportion of records in each stratum is respected, but the limit per curation
    may be violated, unlike the StrictStratificationCurator, which will respect the limit
    at the (potential) cost of violating the proportion of records in each stratum.

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

    """

    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        stratify_field: str,
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
    ):
        """
        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            stratify_field (str): The field to stratify.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[
                Selector(
                    method=StratifiedSampler(
                        field=stratify_field,
                        mode=StratificationMode.proportional,
                    ),
                    limit=limit,
                ),
            ],
        )


class StrictStratificationCurator(Curator):
    """
    Stock Curator that builds a strict stratification of application records
    according to the field stratify_field and adds up to limit results to
    curated_dataset_name.

    The limit of records per curation is respected, but the proportion of records in each
    stratum may be violated, unlike the ProportionalStratificationCurator, which will
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

    """

    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        stratify_field: str,
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
    ):
        """
        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            stratify_field (str): The field to stratify.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[
                Selector(
                    method=StratifiedSampler(
                        field=stratify_field,
                        mode=StratificationMode.strict,
                    ),
                    limit=limit,
                ),
            ],
        )


class AscendedSortCurator(Curator):
    """
    Stock Curator that sorts the application field specified by sort_field in ascending order
    and adds up to the top limit results to curated_dataset_name every curation_interval.

    """

    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        sort_field: str,
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
    ):
        """
        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            sort_field (str): The field to sort.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[
                Selector(
                    method=OrderedSampler(
                        field=sort_field,
                        sort=DruidDimensionOrderingDirections.ASCENDING,
                    ),
                    limit=limit,
                ),
            ],
        )


class DescendedSortCurator(Curator):
    """
    Stock Curator that sorts the application field specified by sort_field in descending order
    and adds up to the top limit results to curated_dataset_name every curation_interval.

    """

    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        sort_field: str,
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
    ):
        """
        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            sort_field (str): The field to sort.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[
                Selector(
                    method=OrderedSampler(
                        field=sort_field,
                        sort=DruidDimensionOrderingDirections.DESCENDING,
                    ),
                    limit=limit,
                ),
            ],
        )


class BoundedRangeCurator(Curator):
    """
    Stock Curator that strictly bounds the application field specified by bound_field between
    upper_bound and lower_bound and adds up to limit results to curated_dataset_name
    every curation_interval. If the curation returns more results than limit, the results are
    sorted in ascending order by bound_field when sort_ascending is True (default) and in
    descending order when sort_ascending is False.

    """

    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        bound_field: str,
        upper_bound: float,
        lower_bound: float,
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
        sort_ascending: bool = True,
    ):
        """
        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            bound_field (str): The field to bound.
            upper_bound (float): Upper bound on the field.
            lower_bound (float): Lower bound on the field.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
            sort_ascending (bool, optional): Whether or not to sort the results in ascending order.
                Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[
                Selector(
                    method=OrderedSampler(
                        field=bound_field,
                        sort=DruidDimensionOrderingDirections.ASCENDING
                        if sort_ascending
                        else DruidDimensionOrderingDirections.DESCENDING,
                    ),
                    limit=limit,
                    filters=[BoundsFilter(field=bound_field, upper=upper_bound, lower=lower_bound)],
                ),
            ],
        )


class EqualityCurator(Curator):
    def __init__(
        self,
        name: str,
        application_name: str,
        limit: int,
        field: str,
        equals: Union[bool, str, int, float],
        curated_dataset_name: Optional[str] = None,
        start_on: Optional[datetime.datetime] = None,
        curation_interval: datetime.timedelta = datetime.timedelta(days=1),
        curate_past_intervals: bool = True,
    ):
        """
        Stock Curator that selects all results where the field specified by field is equal to
        equals and adds up to limit results to curated_dataset_name every curation_interval.

        If the curation returns more results than limit, the results are sampled uniformly at
        random.

        Args:
            name (str): The name of the curator.
            application_name (str): The name of the application that the curator is running in.
            limit (int): The maximum number of results to return.
            field (str): The field to equate.
            equals (Union[bool, str, int, float]): The value to equate the field to. String values
                "true" and "false" are validated as bool types.
            curated_dataset_name (Optional[str], optional): The name of the curated dataset that
                the curator will write to. Defaults to None, in which case the name of the curator
                will be used.
            start_on (Optional[datetime.datetime], optional): The datetime to start the
                curator. Defaults to None, in which case the curator will start now, looking back
                one curation_interval.
            curation_interval (datetime.timedelta, optional): The interval of time considered
            during each run of the curator. Defaults to datetime.timedelta(days=1).
            curate_past_intervals (bool, optional): Whether or not to curate past intervals when
            start_on is in the past. Defaults to True.
        """
        super().__init__(
            name=name,
            curated_dataset_name=curated_dataset_name,
            application_name=application_name,
            start_on=start_on,
            curation_interval=curation_interval,
            curate_past_intervals=curate_past_intervals,
            selectors=[
                Selector(
                    method=UniformSampler(),
                    limit=limit,
                    filters=[EqualsFilter(field=field, equals=equals)],
                ),
            ],
        )

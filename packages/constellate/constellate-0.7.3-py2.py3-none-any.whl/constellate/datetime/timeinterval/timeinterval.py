import itertools
import operator
import sys
from functools import reduce
from typing import Generator, Any, Union, Tuple, List, Iterator

import pandas
import pendulum
import portion
import portion as P
from numpy import int64
from pendulum import Period
from portion import Interval, Bound, empty, IntervalDict

UTCTimestampMilliSec = int


def __utctimestamp_millisec_converter(
    in_value: Union[int, int64, pendulum.DateTime, pendulum.Date, pandas.Timestamp]
):
    if isinstance(in_value, int) or isinstance(in_value, int64):
        return in_value
    elif isinstance(in_value, pendulum.DateTime) or isinstance(in_value, pendulum.Date):
        return int(in_value.float_timestamp * 1000)
    elif isinstance(in_value, pandas.Timestamp):
        return pendulum.instance(in_value.to_pydatetime()).int_timestamp * 1000
    raise Exception(f"{in_value} not convertible to {type(UTCTimestampMilliSec)}")


class TimeInterval(Interval):
    def __init__(
        self,
        *obj: Union[Interval, Tuple],  # Tuple==Tuple[Union[Interval, TimeInterval]]
    ):
        super().__init__(*obj)

    @property
    def start(self):
        return self.lower

    @property
    def end(self):
        return self.upper

    # Conversion utilities
    def to_pendulum_period(self, adjust_bounds: bool = False) -> Period:
        if self.start in [portion.inf, -portion.inf] or self.end in [portion.inf, -portion.inf]:
            raise ValueError("Infinite period cannot be computed")

        start = self.start - 1 if adjust_bounds and self.left is Bound.OPEN else self.start
        start = pendulum.from_timestamp(timestamp=start / 1000.0, tz="UTC")
        end = self.end + 1 if adjust_bounds and self.right is Bound.OPEN else self.end
        end = pendulum.from_timestamp(timestamp=end / 1000.0, tz="UTC")

        return end - start

    # Set theory utilities
    def rightmost_intersected_complement(self, other):
        """rightmost_complement([-5, 5], [1,3]) => [3,5]

        :param other:

        """
        if not self.intersection(other):
            raise ValueError()

        # )1,inf(
        inv_other = (~other)._intervals[-1]
        # [3, inf]
        inv_other = P.closed(inv_other.lower, inv_other.upper)
        # [-5, 5] & [3, inf] => [3, 5]
        return TimeInterval(self & inv_other)

    def leftmost_intersected_complement(self, other):
        """leftmost_complement([-5, 5], [1,3]) => [-5,1]

        :param other:

        """
        if not self.intersection(other):
            raise ValueError()
        # -inf,1(
        inv_other = (~other)._intervals[0]
        # [-inf, 1]
        inv_other = P.closed(inv_other.lower, inv_other.upper)
        # [-5, 5] & [-inf, 1] => [-5, 1]
        return TimeInterval(self & inv_other)

    # Sub range generators utilities
    def range(self, *args) -> Generator[Any, None, None]:
        for period in self.range_pendulum_period(*args):
            yield to_time_interval(
                left=Bound.CLOSED, start=period.start, end=period.end, right=Bound.CLOSED
            )

    def range_pendulum_period(self, *args) -> Generator[Period, None, None]:
        period = self.to_pendulum_period()
        range_start = None
        for range_end in period.range(*args):
            if range_start is not None:
                yield range_end - range_start
            range_start = range_end

        # For loop only loops over whole range. If the period/range_unit is a real number (eg: 2.5),
        # then the last range (0.5) is not looped over. Bug in pendulum ? I don't know
        range_end = period.end
        if range_start < range_end:
            yield range_end - range_start

    def __and__(self, other):
        """Return intersection(self, other)"""
        # https://docs.python.org/3/library/operator.html
        # https://medium.com/better-programming/mathematical-set-operations-in-python-e065aac07413
        return TimeInterval(super().__and__(other))

    def __or__(self, other):
        """Return union(self, other)"""
        if other is None:
            return self

        return TimeInterval(super().__or__(other))

    def __sub__(self, other):
        """Return difference(self, other)"""
        return TimeInterval(super().__sub__(other))

    def intersection(self, other):
        return self & other

    def union(self, other):
        return self | other

    def difference(self, other):
        return self - other

    def overlaps(self, other):
        return super().overlaps(other)

    def __eq__(self, other):
        return super().__eq__(other)

    def __lt__(self, other):
        return super().__lt__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __le__(self, other):
        return super().__le__(other)

    def __ge__(self, other):
        return super().__ge__(other)

    def __str__(self):
        def to_str(i):
            if i.empty:
                return "Period []"
            return str(TimeInterval(i).to_pendulum_period())

        value = ",".join([to_str(i) for i in self])
        return f"{super().__str__()} ({value})"

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)


def to_time_interval(
    left: Bound = None,
    start: UTCTimestampMilliSec = None,
    end: UTCTimestampMilliSec = None,
    right: Bound = None,
):
    interval = Interval.from_atomic(
        left=left,
        lower=__utctimestamp_millisec_converter(start),
        upper=__utctimestamp_millisec_converter(end),
        right=right,
    )
    return TimeInterval(interval)


def to_time_interval_from_period(period: Period, left: Bound = None, right: Bound = None):
    interval = Interval.from_atomic(
        left=left,
        lower=__utctimestamp_millisec_converter(period.start),
        upper=__utctimestamp_millisec_converter(period.end),
        right=right,
    )
    return TimeInterval(interval)


def time_interval_empty() -> TimeInterval:
    return TimeInterval(empty())


def to_time_interval_simplified(
    intervals: Iterator[Union[Interval, TimeInterval]] = []
) -> Union[Interval, TimeInterval]:
    atomic_intervals = itertools.chain.from_iterable(
        [list(non_atomic_interval) for non_atomic_interval in intervals]
    )
    atomic_intervals = list(atomic_intervals)
    return reduce(operator.__or__, atomic_intervals) if len(atomic_intervals) > 0 else empty()


def discretize_atomic_intervals(intervals: List[Interval], incr=1):
    raise NotImplementedError()
    # Turn [[0,1] | [2,3]] into [[0,3]]
    # return i.apply(first_step).apply(second_step)


def time_interval_iterate(
    time_interval: TimeInterval = None, step: int = 1, backward: bool = False
) -> Generator[TimeInterval, None, None]:
    """range_time_interval2([10,40], step=10, backward=False) -> [[10,20), [20, 30), [30,40), [40,40???]]
    range_time_interval2([10,40], step=10, backward=True) -> [[40,30), [30, 20), [20,10), [10,10????]]

    :param time_interval: TimeInterval:  (Default value = None)
    :param step: int:  (Default value = 1)
    :param backward: bool:  (Default value = False)

    """
    if time_interval.empty:
        return
        yield

    if not backward:

        def ending(start, step, max_end):
            last = False
            end = start + step
            if end > max_end:
                end = max_end
                last = True

            return end, last

        end = time_interval.start
        max_end = time_interval.end
        last = end > max_end
        while not last:
            start = end
            end, last = ending(start, step, max_end)
            sub_time_interval = to_time_interval(
                left=Bound.CLOSED, start=start, end=end, right=Bound.OPEN
            )
            if not sub_time_interval.empty:
                yield sub_time_interval
    else:

        def starting(end, step, max_start):
            last = False
            start = end - step
            if start < max_start:
                start = max_start
                last = True

            return start, last

        start = time_interval.end
        max_start = time_interval.start
        last = max_start > start
        while not last:
            end = start
            start, last = starting(end, step, max_start)
            sub_time_interval = to_time_interval(
                left=Bound.CLOSED, start=start, end=end, right=Bound.OPEN
            )
            if not sub_time_interval.empty:
                yield sub_time_interval


def to_sorted_atomic_intervals(intervals: Iterator[Interval] = []) -> List[Interval]:
    return [i for i in to_time_interval_simplified(intervals)]


def to_sorted_time_intervals_from_intervals(
    intervals: Iterator[Interval] = [],
) -> List[TimeInterval]:
    intervals = to_sorted_atomic_intervals(intervals)
    return [TimeInterval(interval) for interval in intervals]


def discretize_atomic_interval(i: Interval, incr=1):
    # Turn [0,1] | [2,3] into [0,3]
    # src: https://github.com/AlexandreDecan/portion/issues/24#issuecomment-604456362
    def first_step(s):
        return (
            portion.OPEN,
            (s.lower - incr if s.left is portion.CLOSED else s.lower),
            (s.upper + incr if s.right is portion.CLOSED else s.upper),
            portion.OPEN,
        )

    def second_step(s):
        return (
            portion.CLOSED,
            (s.lower + incr if s.left is portion.OPEN and s.lower != -portion.inf else s.lower),
            (s.upper - incr if s.right is portion.OPEN and s.upper != portion.inf else s.upper),
            portion.CLOSED,
        )

    if i.empty:
        return i

    if not i.atomic:
        raise ValueError("Interval not atomic")

    def discretize(interval: Interval):
        return interval.apply(first_step).apply(second_step)

    t = Interval(i)
    return discretize(i) if not discretize(t).empty else i


def flatten_intervals(intervals: List[Interval] = []) -> Iterator[Interval]:
    atomic_intervals = itertools.chain.from_iterable(
        [list(non_atomic_interval) for non_atomic_interval in intervals]
    )
    return atomic_intervals


def sort_intervals(intervals: List[Interval] = []) -> List[Interval]:
    """Sorted from earliest to latest

    :param intervals: List[Interval]:  (Default value = [])

    """
    sequence = enumerate(range(-sys.maxsize, sys.maxsize, 1), start=0)

    def to_tuple(interval: Interval):
        assert interval.atomic
        # sequence value must be unique for each interval, otherwise the intervals
        # are merged together
        return (interval, next(sequence))

    mapped = IntervalDict(map(to_tuple, intervals))
    return list(mapped.keys())


def to_sorted_atomic_intervals_from_time_intervals(
    instrument_time_intervals: List[TimeInterval] = [],
) -> List[Interval]:
    intervals = [time_interval for time_interval in instrument_time_intervals]
    return to_sorted_atomic_intervals(intervals)

from __future__ import annotations

import datetime
import functools
import operator
import typing as t


_F_START = "start"
_F_END = "end"
_F__DURATION = "_duration"
_T_FACTORY = t.Callable[[datetime.datetime, datetime.datetime], t.Any]
_T_DT_PAIR = tuple[datetime.datetime, datetime.datetime]
_SEP = "/"
_DT_SEP = "T"
_TIMESPEC = "auto"

_sort_key_start = operator.attrgetter(_F_START)
_sort_key_end = operator.attrgetter(_F_END)


def _jumping_sequence(length: int) -> t.Generator[int, None, None]:
    middle, tail = divmod(length, 2)
    for left, right in zip(range(middle - 1, -1, -1),
                           range(middle, length)):
        yield left
        yield right
    if tail:
        yield length - 1


def Tuple(start: datetime.datetime, end: datetime.datetime,
          ) -> _T_DT_PAIR:
    return start, end


# base proto

class PeriodProto(t.Protocol):
    start: datetime.datetime
    end: datetime.datetime


class Period:

    start: datetime.datetime
    end: datetime.datetime

    __slots__ = (_F_START, _F_END, _F__DURATION)

    def __init__(self,
                 start: datetime.datetime,
                 end: datetime.datetime,
                 validate: bool = True):
        if validate:
            validate_edges(start, end)
        object.__setattr__(self, _F_START, start)
        object.__setattr__(self, _F_END, end)
        # TODO(d.burmistrov): if eval_duration: self.__set_duration()

    def __set_duration(self) -> datetime.timedelta:
        duration = self.end - self.start
        object.__setattr__(self, _F__DURATION, duration)
        return duration

    @property
    def duration(self) -> datetime.timedelta:
        try:
            return getattr(self, _F__DURATION)
        except AttributeError:
            return self.__set_duration()

    @classmethod
    def from_edge(cls,
                  edge: datetime.datetime,
                  duration: datetime.timedelta,
                  end: bool = False,
                  validate: bool = True,
                  ) -> Period:
        """Make a Period from duration and one of edges."""

        if end:
            new_start = edge - duration
            new_end = edge
        else:
            new_start = edge
            new_end = edge + duration
        return cls(new_start, new_end, validate=validate)

    def __setattr__(self, key: str, value: t.Any) -> None:
        raise NotImplementedError("method not allowed")

    def __delattr__(self, item: str) -> None:
        raise NotImplementedError("method not allowed")

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Period):
            return self.start == other.start and self.end == other.end
        elif hasattr(other, _F_START) and hasattr(other, _F_END):
            return False
        else:
            raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.start!r}, {self.end!r})"

    def copy(self) -> Period:
        """Return a copy of Period."""

        return Period(self.start, self.end, False)

    def __copy__(self) -> Period:
        return self.copy()

    def __deepcopy__(self, memo):
        if self not in memo:
            memo[self] = self.copy()
        return memo[self]

    def replace(self,
                start: t.Optional[datetime.datetime] = None,
                end: t.Optional[datetime.datetime] = None,
                validate: bool = True,
                ) -> Period:
        """Return Period with new specified fields."""

        if start is None:
            start = self.start
        if end is None:
            end = self.end
        return self.__class__(start=start, end=end, validate=validate)

    def as_dict(self) -> dict[str, datetime.datetime | datetime.timedelta]:
        """Return a dictionary of edges and durations"""

        return dict(start=self.start, end=self.end, duration=self.duration)

# base entity

    def __add__(self, other):
        return add(self, other, factory=self.__class__)

    __radd__ = __add__

    def __sub__(self, other):
        return sub(self, other, factory=self.__class__)

    __rsub__ = __sub__

    # "p1 & p2"
    def __and__(self, other):
        return intersection(self, other, factory=self.__class__)

    __rand__ = __and__

    # "p1 | p2"
    def __or__(self, other):
        return union(self, other, factory=self.__class__)

    __ror__ = __or__

    def __lshift__(self, other):
        return lshift(self, other, factory=self.__class__)

    def __rshift__(self, other):
        return rshift(self, other, factory=self.__class__)

    def __contains__(self, item):
        return within(self, item)

    def isoformat(self,
                  dt_sep=_DT_SEP,
                  timespec=_TIMESPEC,
                  sep: str = _SEP) -> str:
        return isoformat(self, dt_sep=dt_sep, timespec=timespec, sep=sep)

    def strftime(self, date_fmt: str, sep: str = _SEP) -> str:
        return strftime(self, date_fmt=date_fmt, sep=sep)

    def __str__(self) -> str:
        return isoformat(self)

    def as_tuple(self):
        return as_args(self)

    @property
    def edges(self):
        return self.as_tuple()

    def as_kwargs(self):
        return as_kwargs(self)

    @classmethod
    def fromisoformat(cls, s: str, sep: str = _SEP) -> Period:
        return fromisoformat(s=s, sep=sep, factory=cls)

    @classmethod
    def strptime(cls,
                 period_string: str,
                 date_format: str,
                 sep: str = _SEP) -> Period:
        return strptime(period_string=period_string,
                        date_format=date_format,
                        sep=sep,
                        factory=cls)

# TODO(d.burmistrov):
#  - timezone support
#  - wrap errors (in all validate funcs)?
#  - review exceptions
#  - add/review unit tests
#  - do performance tests
#  - docstrings
#  - readme.rst
#  - read the docs (+examples)
#  - ensure pickling


# misc

def to_timestamps(*periods: PeriodProto,
                  ) -> t.Generator[datetime.datetime, None, None]:
    """Flatten periods into sequence of edges

    :param periods: period-like objects
    """

    for period in periods:
        yield period.start
        yield period.end


# sorting

def ascend_start(*periods: PeriodProto,
                 reverse: bool = False,
                 ) -> list[PeriodProto]:
    f"""Sort periods by '{_F_START}' attribute

    Sorting is ascending by default.

    :param periods: period-like objects
    :param reverse: switch ascending to descending
    """

    return sorted(periods, key=_sort_key_start, reverse=reverse)


def descend_end(*periods: PeriodProto,
                reverse: bool = False,
                ) -> list[PeriodProto]:
    f"""Sort periods by '{_F_END}' attribute

    Sorting is descending by default.

    :param periods: period-like objects
    :param reverse: switch descending to ascending
    """

    return sorted(periods, key=_sort_key_end, reverse=(not reverse))


# validation

def validate_edges(start: datetime.datetime, end: datetime.datetime) -> None:
    f"""Validate edges of Period

    Exception will be raised for invalid data.
    Validations:
    - edge value types
    - edge order ('{_F_START}' before '{_F_END}')

    :param start: datetime.datetime
    :param end: datetime.datetime
    """

    # types
    if not isinstance(start, datetime.datetime):
        raise TypeError(f"'{_F_START}' must be datetime: '{type(start)}'")
    elif not isinstance(end, datetime.datetime):
        raise TypeError(f"'{_F_END}' must be datetime: '{type(end)}'")

    # timezones
    start_offset = start.utcoffset()
    end_offset = end.utcoffset()
    if start_offset is None:
        if end_offset is not None:
            msg = f"Can't mix naive ({_F_START}) and aware ({_F_END}) edges"
            raise ValueError(msg)
    elif end_offset is None:
        msg = f"Can't mix naive ({_F_END}) and aware ({_F_START}) edges"
        raise ValueError(msg)

    # values
    if start >= end:
        msg = (f"'{_F_START}' must be '<' (before) '{_F_END}':"
               f" '{start}' >= '{end}'")
        raise ValueError(msg)


def validate_period(period: PeriodProto) -> None:
    f"""Validate period-like object

    See `{validate_edges.__name__}` for details.

    :param period: period-like object
    """

    validate_edges(period.start, period.end)


# ~set proto

def within(period: PeriodProto, item: datetime.datetime | PeriodProto) -> bool:
    if isinstance(item, datetime.datetime):
        return period.start <= item <= period.end

    return (period.start <= item.start) and (item.end <= period.end)


def join(period: PeriodProto,
         other: PeriodProto,
         *others: PeriodProto,
         factory: _T_FACTORY = Period):
    if others:
        others = ascend_start(period, other, *others)  # type: ignore
        period = others[0]
        for other in others[1:]:
            if period.end != other.start:
                return None
            period = other
        return factory(others[0].start, others[-1].end)
    elif period.end == other.start:  # `p1` on the left
        return factory(period.start, other.end)
    elif period.start == other.end:  # `p1` on the right
        return factory(other.start, period.end)
    else:
        return None


def union(period: PeriodProto,
          other: PeriodProto,
          *others: PeriodProto,
          factory: _T_FACTORY = Period,
          ) -> Period | _T_DT_PAIR | None:
    if others:
        others = ascend_start(period, other, *others)  # type: ignore
        period = others[0]
        max_end = period.end
        for other in others[1:]:
            if within(period, other.start):
                period = other
                max_end = max(other.end, max_end)
            else:
                return None
        return factory(others[0].start, max_end)
    elif intersection(period, other, factory=Tuple):
        return factory(min(period.start, other.start),
                       max(period.end, other.end))
    else:
        return join(period, other, factory=factory)


def intersection(period: PeriodProto,
                 other: PeriodProto,
                 *others: PeriodProto,
                 factory: _T_FACTORY = Period,
                 ) -> Period | _T_DT_PAIR | None:
    max_start = max(period.start, other.start)
    min_end = min(period.end, other.end)
    for p in others:
        if max_start >= min_end:
            return None
        max_start = max(p.start, max_start)
        min_end = min(p.end, min_end)

    if max_start >= min_end:
        return None

    return factory(max_start, min_end)


def difference(period: PeriodProto,
               other: PeriodProto,
               *others: PeriodProto,
               factory: _T_FACTORY = Period,
               ) -> t.Generator[(Period | _T_DT_PAIR), None, None]:
    if others:
        # aggregate
        others = ascend_start(  # type: ignore[assignment]
            *(o for o in others + (other,)
              if intersection(period, o, factory=Tuple))
        )

    if others:
        # then having one of this pictures:
        #
        #   I.
        #       |-----------------------|
        #     |------|  |----| |--|  |-----|
        #
        #   II.
        #       |-----------------------|
        #         |--|  |----| |--|  |-----|
        #
        #   III.
        #       |-----------------------|
        #     |------|  |----| |--| |-|
        #
        #   IV.
        #       |-----------------------|
        #         |--|  |----| |--| |-|

        cross = others[0]
        # first
        if period.start < cross.start:
            yield factory(period.start, cross.start)

        # aggregate + mids
        for item in others[1:]:
            if x := union(item, cross):
                cross = t.cast(PeriodProto, x)
            else:
                yield factory(cross.end, item.start)
                cross = item

        # last
        if period.end > cross.end:
            yield factory(cross.end, period.end)

    elif x := intersection(period, other, factory=Tuple):
        # I.
        #   |-----p-----|
        #      |--i--|
        # II.
        #   |-----p-----|
        #         |--r--|
        # III.
        #   |-----p-----|
        #   |--l--|

        start, end = t.cast(_T_DT_PAIR, x)
        if period.start < start:  # I./II. left
            yield factory(period.start, start)
            if period.end > end:  # I. right
                yield factory(end, period.end)
        elif period.end != end:  # III. right
            yield factory(end, period.end)
        # no `else` -- because `cross` equals `period`

    else:
        yield factory(period.start, period.end)


# math operations

# I.  "p + timedelta"
# II. "p1 + p2"
def add(period: PeriodProto,
        other: PeriodProto | datetime.timedelta,
        factory: _T_FACTORY = Period,
        ) -> Period | _T_DT_PAIR | None:
    if isinstance(other, datetime.timedelta):
        if not other.total_seconds():
            return factory(period.start, period.end)
        elif other.total_seconds() > 0:
            return factory(period.start, period.end + other)
        else:
            end = period.end + other
            validate_edges(period.start, end)
            return factory(period.start, end)

    return join(period, other, factory=factory)
# TODO(d.burmistrov): decorator to raise on None result & add wrapped API funcs


# I.  "p - timedelta"
# II. "p1 - p2"
def sub(period: PeriodProto,
        other: PeriodProto | datetime.timedelta,
        factory: _T_FACTORY = Period,
        ) -> Period | _T_DT_PAIR | None:
    if isinstance(other, datetime.timedelta):
        return add(period, -other, factory=factory)

    # TODO(d.burmistrov): extract this to `cut(period, other, *others, ...)`
    if period.start == other.start:
        return factory(other.end, period.end)
    elif period.end == other.end:
        return factory(period.start, other.start)
    else:
        raise ValueError()


# I.  "p * number"
def mul(period: PeriodProto, factor: int | float, factory: _T_FACTORY = Period,
        ) -> Period | _T_DT_PAIR | None:
    if factor <= 0:
        return None

    start = period.start
    return factory(start, start + ((period.end - start) * factor))


and_ = intersection
or_ = union
contains = within


def floordiv(period: PeriodProto, other: datetime.timedelta | int
             ) -> datetime.timedelta | int:
    if isinstance(other, (datetime.timedelta, int)):
        return (period.end - period.start) // other

    raise NotImplementedError()


def mod(period: PeriodProto, other: datetime.timedelta) -> datetime.timedelta:
    if isinstance(other, datetime.timedelta):
        return (period.end - period.start) % other

    raise NotImplementedError()


def truediv(period: PeriodProto, other: datetime.timedelta | int | float
            ) -> datetime.timedelta | float:
    if isinstance(other, (datetime.timedelta, int, float)):
        return (period.end - period.start) / other

    raise NotImplementedError()


def xor(period: PeriodProto,
        other: PeriodProto,
        factory: _T_FACTORY = Period):
    result = (sub(period, other, factory=factory),
              sub(other, period, factory=factory))
    return tuple(item for item in result if item is not None) or None


# extras

def eq(period: PeriodProto, other: PeriodProto, *others: PeriodProto) -> bool:
    result = period.start == other.start and period.end == other.end
    if not result:
        return result
    for other in others:
        result = period.start == other.start and period.end == other.end
        if not result:
            return result
    return result


# "p << delta"
def lshift(period: PeriodProto,
           other: datetime.timedelta,
           factory: _T_FACTORY = Period,
           ) -> Period | _T_DT_PAIR:
    if isinstance(other, datetime.timedelta):
        return factory(period.start - other, period.end - other)

    raise NotImplementedError()


# "p >> delta"
def rshift(period: PeriodProto,
           other: datetime.timedelta,
           factory: _T_FACTORY = Period,
           ) -> Period | _T_DT_PAIR:
    if isinstance(other, datetime.timedelta):
        return factory(period.start + other, period.end + other)

    raise NotImplementedError()


# formatting

def fromisoformat(s: str, sep: str = _SEP, factory: _T_FACTORY = Period):
    conv = datetime.datetime.fromisoformat
    start, _, end = s.partition(sep)
    return factory(conv(start), conv(end))


def isoformat(obj: PeriodProto,
              dt_sep=_DT_SEP,
              timespec=_TIMESPEC,
              sep: str = _SEP) -> str:
    conv = functools.partial(datetime.datetime.isoformat,
                             sep=dt_sep, timespec=timespec)
    return f"{conv(obj.start)}{sep}{conv(obj.end)}"


# TODO(d.burmistrov): object class
def strptime(period_string: str,
             date_format: str,
             sep: str = _SEP,
             factory: _T_FACTORY = Period):
    """Parse Period from string by an explicit formatting

    Parse Period from the string by an explicit datetime format string and
    combining separator. Resulting type can be changed with factory argument.
    See datetime `strptime` documentation for format details.

    :param period_string: string containing period
    :param date_format: format string for period edges
    :param sep: separator string
    :param factory: resulting type factory to convert edges to the end result
    """

    sep_len = len(sep)
    jumper = _jumping_sequence(len(period_string) - sep_len + 1)
    for i in jumper:
        j = i + sep_len
        if period_string[i:j] != sep:
            continue

        try:
            start = datetime.datetime.strptime(period_string[:i], date_format)
            end = datetime.datetime.strptime(period_string[j:], date_format)
        except ValueError:
            continue
        else:
            return factory(start, end)

    msg = (f"period data '{period_string}' does not match"
           f" time format '{date_format}' with separator '{sep}'")
    raise ValueError(msg)


def strftime(obj: PeriodProto, date_fmt: str, sep: str = _SEP) -> str:
    """Represent Period as string by an explicit formatting

    Return a string representing the Period, controlled by an explicit
    datetime format string and combining separator. See datetime `strftime`
    documentation for format details.

    :param obj: Period object to serialize
    :param date_fmt: format string for period edges
    :param sep: separator string
    """

    return f"{obj.start.strftime(date_fmt)}{sep}{obj.end.strftime(date_fmt)}"


def as_args(period: PeriodProto) -> _T_DT_PAIR:
    """Return a tuple of edges"""

    return period.start, period.end


def as_kwargs(period: PeriodProto) -> dict[str, datetime.datetime]:
    """Return a dictionary of edges"""

    return dict(start=period.start, end=period.end)

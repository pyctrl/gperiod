from __future__ import annotations

from datetime import datetime, timedelta  # noqa: H301
import functools
import operator
import typing as t


_F_START = "start"
_F_END = "end"
_F__DURATION = "_duration"

_SEP = "/"
_DT_SEP = "T"
_TIMESPEC = "auto"

_SORT_KEY_START = operator.attrgetter(_F_START)


def _jumping_sequence(length: int) -> t.Generator[int, None, None]:
    middle, tail = divmod(length, 2)
    for left, right in zip(range(middle - 1, -1, -1),
                           range(middle, length)):
        yield left
        yield right
    if tail:
        yield length - 1


def Tuple(start: datetime, end: datetime) -> _T_DT_PAIR:
    return start, end


class PeriodProto(t.Protocol):
    start: datetime
    end: datetime


_T_DT_PAIR = t.Tuple[datetime, datetime]

_T_FACTORY = t.Callable[[datetime, datetime], t.Any]
_T_FACTORY_RESULT = t.Union[PeriodProto, t.Tuple[datetime, datetime]]
_T_FACTORY_RESULT_OPT = t.Union[PeriodProto, t.Tuple[datetime, datetime], None]


class Period:

    start: datetime
    end: datetime

    __slots__ = (_F_START, _F_END, _F__DURATION)

    def __init__(self, start: datetime, end: datetime):
        validate_edges(start, end)
        object.__setattr__(self, _F_START, start)
        object.__setattr__(self, _F_END, end)

    def __set_duration(self) -> timedelta:
        duration = self.end - self.start
        object.__setattr__(self, _F__DURATION, duration)
        return duration

    @property
    def duration(self) -> timedelta:
        try:
            return getattr(self, _F__DURATION)
        except AttributeError:
            return self.__set_duration()

    @classmethod
    def load_edges(cls, start: datetime, end: datetime) -> Period:
        """Unsafe load Period from edges without edge validation"""
        inst = cls.__new__(cls)
        object.__setattr__(inst, _F_START, start)
        object.__setattr__(inst, _F_END, end)
        return inst

    @classmethod
    def from_start(cls, start: datetime, duration: timedelta) -> Period:
        """Make a Period from start and duration"""

        return cls(start, start + duration)

    @classmethod
    def from_end(cls, end: datetime, duration: timedelta) -> Period:
        """Make a Period from end and duration"""

        return cls(end - duration, end)

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

        return type(self)(self.start, self.end)

    def __copy__(self) -> Period:
        return self.copy()

    def __deepcopy__(self, memo):  # TODO(d.burmistrov)
        if self not in memo:
            memo[self] = self.copy()
        return memo[self]

    def replace(self,
                start: t.Optional[datetime] = None,
                end: t.Optional[datetime] = None,
                ) -> Period:
        """Return Period with new specified fields."""

        if start is None:
            start = self.start
        if end is None:
            end = self.end
        return type(self)(start=start, end=end)

    @property
    def edges(self):
        return self.as_tuple()

    def as_args(self) -> _T_DT_PAIR:
        """Return a tuple of edges"""

        return self.start, self.end

    def as_tuple(self):  # TOD
        return as_tuple(self)

    def as_kwargs(self) -> dict[str, datetime]:
        """Return a dictionary of edges"""

        return dict(start=self.start, end=self.end)

    def as_dict(self) -> dict[str, datetime | timedelta]:
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
        return contains(self, item)

    def isoformat(self,
                  dt_sep=_DT_SEP,
                  timespec=_TIMESPEC,
                  sep: str = _SEP) -> str:
        return isoformat(self, dt_sep=dt_sep, timespec=timespec, sep=sep)

    def strftime(self, date_fmt: str, sep: str = _SEP) -> str:
        return strftime(self, date_fmt=date_fmt, sep=sep)

    def __str__(self) -> str:
        return isoformat(self)

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
#  - NEGATIVE TIMEDELTAS
#  - timezone support
#  - wrap errors (in all validate funcs)?
#  - review exceptions
#  - add/review unit tests
#  - do performance tests
#  - docstrings
#  - readme.rst
#  - ensure pickling


# sorting

def ascend_start(*periods: PeriodProto,
                 reverse: bool = False,
                 ) -> t.List[PeriodProto]:
    f"""Sort periods by '{_F_START}' attribute

    Sorting is ascending by default.

    :param periods: period-like objects
    :param reverse: switch ascending to descending
    """

    return sorted(periods, key=_SORT_KEY_START, reverse=reverse)


# validation

def validate_edges(start: datetime, end: datetime) -> None:
    f"""Validate period edges

    Exception will be raised for invalid data.
    Validations:
    - edge value types
    - edge order ('{_F_START}' before '{_F_END}')

    :param start: datetime
    :param end: datetime
    """

    # types
    if not isinstance(start, datetime):
        raise TypeError(f"'{_F_START}' must be datetime: '{type(start)}'")
    elif not isinstance(end, datetime):
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

def contains(period: PeriodProto, item: datetime | PeriodProto) -> bool:
    """Report whether period contains another period or timestamp

    :param period: period-like object
    :param item: timestamp or period-like object
    """

    if isinstance(item, datetime):
        return period.start <= item <= period.end

    return (period.start <= item.start) and (item.end <= period.end)


def join(period: PeriodProto,
         other: PeriodProto,
         *others: PeriodProto,
         factory: _T_FACTORY = Period,
         ) -> _T_FACTORY_RESULT_OPT:
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
          ) -> _T_FACTORY_RESULT_OPT:
    if others:
        others = ascend_start(period, other, *others)  # type: ignore
        period = others[0]
        max_end = period.end
        for other in others[1:]:
            if contains(period, other.start):
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
                 ) -> _T_FACTORY_RESULT_OPT:
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
               ) -> t.Generator[(_T_FACTORY_RESULT), None, None]:
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
        other: PeriodProto | timedelta,
        factory: _T_FACTORY = Period,
        ) -> _T_FACTORY_RESULT_OPT:
    if not isinstance(other, timedelta):
        return join(period, other, factory=factory)

    secs = other.total_seconds()
    if not secs:
        return factory(period.start, period.end)
    elif secs > 0:
        return factory(period.start, period.end + other)
    else:
        end = period.end + other
        validate_edges(period.start, end)
        return factory(period.start, end)
# TODO(d.burmistrov): decorator to raise on None result & add wrapped API funcs


# I.  "p - timedelta"
# II. "p1 - p2"
def sub(period: PeriodProto,
        other: PeriodProto | timedelta,
        factory: _T_FACTORY = Period,
        ) -> _T_FACTORY_RESULT_OPT:
    if isinstance(other, timedelta):
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
        ) -> _T_FACTORY_RESULT_OPT:
    if factor == 0:
        return None

    duration = period.end - period.start
    if factor > 0:
        end = period.start + (duration * factor)
        return factory(period.start, end)
    else:
        start = period.start - (duration * -factor)
        return factory(start, period.end)


def floordiv(period: PeriodProto, other: timedelta | int,
             ) -> timedelta | int:
    if not isinstance(other, (timedelta, int)):
        raise NotImplementedError()

    return (period.end - period.start) // other


def mod(period: PeriodProto, other: timedelta) -> timedelta:
    if not isinstance(other, timedelta):
        raise NotImplementedError()

    return (period.end - period.start) % other


def truediv(period: PeriodProto, other: timedelta | int | float,
            ) -> timedelta | float:
    if not isinstance(other, (timedelta, int, float)):
        raise NotImplementedError()

    return (period.end - period.start) / other


def xor(period: PeriodProto,
        other: PeriodProto,
        factory: _T_FACTORY = Period):
    result = (sub(period, other, factory=factory),
              sub(other, period, factory=factory))
    return tuple(item for item in result if item is not None) or None


# extras

and_ = intersection
or_ = union


def eq(period: PeriodProto, other: PeriodProto, *others: PeriodProto) -> bool:
    """Compare periods for equality

    To be equal all periods have to have same starts and ends
    """

    result = ((period.start == other.start) and (period.end == other.end))
    if not result:
        return result
    for other in others:
        result = period.start == other.start and period.end == other.end
        if not result:
            return result
    return result


def lshift(period: PeriodProto,
           delta: timedelta,
           factory: _T_FACTORY = Period,
           ) -> _T_FACTORY_RESULT:
    """Shift left right by timedelta (p << delta)"""

    if not isinstance(delta, timedelta):
        raise NotImplementedError()

    return factory(period.start - delta, period.end - delta)


def rshift(period: PeriodProto,
           delta: timedelta,
           factory: _T_FACTORY = Period,
           ) -> _T_FACTORY_RESULT:
    """Shift period right by timedelta (p >> delta)"""

    if not isinstance(delta, timedelta):
        raise NotImplementedError()

    return factory(period.start + delta, period.end + delta)


# formatting

# TODO(d.burmistrov): jumping search + check ISO spec for sep alphabets
def fromisoformat(s: str, sep: str = _SEP, factory: _T_FACTORY = Period):
    conv = datetime.fromisoformat
    start, _, end = s.partition(sep)
    return factory(conv(start), conv(end))


# TODO(d.burmistrov): check ISO spec for sep alphabets
def isoformat(obj: PeriodProto,
              dt_sep=_DT_SEP,
              timespec=_TIMESPEC,
              sep: str = _SEP) -> str:
    conv = functools.partial(datetime.isoformat,
                             sep=dt_sep, timespec=timespec)
    return f"{conv(obj.start)}{sep}{conv(obj.end)}"


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
            start = datetime.strptime(period_string[:i], date_format)
            end = datetime.strptime(period_string[j:], date_format)
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


def as_tuple(period: PeriodProto) -> _T_DT_PAIR:
    """Return a tuple of edges"""

    return period.start, period.end


def as_dict(period: PeriodProto) -> dict[str, datetime]:
    """Return a dictionary of edges"""

    return dict(start=period.start, end=period.end)

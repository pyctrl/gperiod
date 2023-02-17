from __future__ import annotations

import datetime
import operator
import typing as t


_F_START = "start"
_F_END = "end"
_F__DURATION = "_duration"
_T_DT_PAIR = tuple[datetime.datetime, datetime.datetime]
_SEP = "/"

_sort_key_start = operator.attrgetter(_F_START)
_sort_key_end = operator.attrgetter(_F_END)


# TODO(d.burmistrov):
#  - [im]mutable
#  - assert `start < end`
#  - timezone support
#  - wrap errors (in all validate funcs)?
#  - review exceptions
#  - add/review unit tests
#  - review Period class implementation
#  - do performance tests
#  - packaging
#  - docstrings
#  - readme.rst
#  - read the docs (+examples)
#  - ensure pickling


# base proto

class PeriodProto(t.Protocol):
    start: datetime.datetime
    end: datetime.datetime


class Period(object):

    start: datetime.datetime
    end: datetime.datetime

    __slots__ = (_F_START, _F_END, _F__DURATION)

    def __init__(self,
                 start: datetime.datetime,
                 end: datetime.datetime,
                 validate: bool = True):
        if validate:
            validate_flat(start, end)
        object.__setattr__(self, _F_START, start)
        object.__setattr__(self, _F_END, end)

    @property
    def duration(self) -> datetime.timedelta:
        try:
            return getattr(self, _F__DURATION)
        except AttributeError:
            object.__setattr__(self, _F__DURATION, self.end - self.start)
            return getattr(self, _F__DURATION)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.start!r}, {self.end!r})"

    def __str__(self):
        return self.isoformat()

    def __setattr__(self, key, value):
        raise NotImplementedError("method not allowed")

    def __delattr__(self, item):
        raise NotImplementedError("method not allowed")

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Period):
            return self.start == other.start and self.end == other.end
        elif hasattr(other, _F_START) and hasattr(other, _F_END):
            return False
        else:
            raise NotImplementedError()

    def __add__(self, other: PeriodProto | datetime.timedelta
                ) -> Period | None:  # "p1 + p2"
        if isinstance(other, datetime.timedelta):
            return Period(self.start, self.end + other, False)

        return join(self, other)  # type: ignore[return-value]

    __radd__ = __add__

    def __and__(self, other: PeriodProto) -> Period | None:  # "p1 & p2"
        return intersection(self, other)  # type: ignore[return-value]

    __rand__ = __and__

    def __or__(self, other: PeriodProto) -> Period | None:  # "p1 | p2"
        return union(self, other)  # type: ignore[return-value]

    __ror__ = __or__

    def __lshift__(self, other: datetime.timedelta) -> Period:  # "p << delta"
        if isinstance(other, datetime.timedelta):
            return Period(self.start - other, self.end - other, False)

        raise NotImplementedError()

    def __rshift__(self, other: datetime.timedelta) -> Period:  # "p >> delta"
        if isinstance(other, datetime.timedelta):
            return Period(self.start + other, self.end + other, False)

        raise NotImplementedError()

    def __contains__(self, item: PeriodProto | datetime.datetime) -> bool:
        return within(self, item)

    @classmethod
    def fromisoformat(cls, s: str) -> Period:
        items = s.partition(_SEP)
        fromisoformat = datetime.datetime.fromisoformat
        return Period(fromisoformat(items[0]), fromisoformat(items[2]))

    def isoformat(self, sep="T", timespec="auto") -> str:
        return _SEP.join(
            datetime.datetime.isoformat(item, sep=sep, timespec=timespec)
            for item in (self.start, self.end)
        )

    @classmethod
    def strptime(cls, period_string: str, date_format: str,
                 separator: str = _SEP) -> Period:
        strptime = datetime.datetime.strptime
        for i, j in zip(range(len(period_string)),
                        range(len(separator), len(period_string))):
            if period_string[slice(i, j)] == separator:
                try:
                    start = strptime(period_string[:i], date_format)
                    end = strptime(period_string[j:], date_format)
                except ValueError:
                    continue
                else:
                    return cls(start, end)

        raise ValueError(f"period data '{period_string}' does not match"
                         f" time format '{date_format}'"
                         f" with separator '{separator}'")

    def strftime(self, date_fmt: str, separator: str = _SEP) -> str:
        return (self.start.strftime(date_fmt)
                + separator
                + self.end.strftime(date_fmt))

    # TODO(d.burmistrov): __deepcopy__
    def __copy__(self) -> Period:
        return Period(self.start, self.end, False)

    def copy(self) -> Period:
        return Period(self.start, self.end, False)

    def as_tuple(self) -> tuple[datetime.datetime, datetime.datetime]:
        return self.start, self.end

    def as_kwargs(self) -> dict[str, datetime.datetime]:
        return dict(start=self.start, end=self.end)

    def as_dict(self) -> dict[str, datetime.datetime | datetime.timedelta]:
        return dict(start=self.start, end=self.end, duration=self.duration)

    def replace(self,
                start: t.Optional[datetime.datetime] = None,
                end: t.Optional[datetime.datetime] = None,
                ) -> Period:
        # TODO(d.burmistrov): validate isinstance?

        if start is None:
            start = self.start
        if end is None:
            end = self.end

        return type(self)(start=start, end=end)


# base API

def to_timestamps(*periods: PeriodProto
                  ) -> t.Generator[datetime.datetime, None, None]:
    for p in periods:
        yield p.start
        yield p.end


def ascend_start(*periods: PeriodProto, reverse: bool = False,
                 ) -> list[PeriodProto]:
    return sorted(periods, key=_sort_key_start, reverse=reverse)


def descend_end(*periods: PeriodProto, reverse: bool = False,
                ) -> list[PeriodProto]:
    return sorted(periods, key=_sort_key_end, reverse=(not reverse))


def validate_flat(start: datetime.datetime, end: datetime.datetime) -> None:
    if not isinstance(start, datetime.datetime):
        raise TypeError(f"'{_F_START}' must be datetime: '{type(start)}'")
    elif not isinstance(end, datetime.datetime):
        raise TypeError(f"'{_F_END}' must be datetime: '{type(end)}'")

    if start >= end:
        raise ValueError(f"'{_F_START}' must be '<' (before) '{_F_END}':"
                         f" '{start}' >= '{end}'")


def validate_period(period: PeriodProto) -> None:
    validate_flat(period.start, period.end)


def within(period: PeriodProto, item: datetime.datetime | PeriodProto) -> bool:
    if isinstance(item, datetime.datetime):
        return period.start <= item <= period.end

    return (period.start <= item.start) and (item.end <= period.end)


def join(period: PeriodProto,
         other: PeriodProto,
         *others: PeriodProto,
         flat: bool = False,
         ) -> Period | _T_DT_PAIR | None:
    if others:
        others = ascend_start(period, other,  # type: ignore[assignment]
                              *others)
        period = others[0]
        for other in others[1:]:
            if period.end != other.start:
                return None
            period = other
        result = (others[0].start, others[-1].end)
    elif period.end == other.start:  # `p1` on the left
        result = (period.start, other.end)
    elif period.start == other.end:  # `p1` on the right
        result = (other.start, period.end)
    else:
        return None

    return result if flat else Period(*result, False)


def union(period: PeriodProto,
          other: PeriodProto,
          *others: PeriodProto,
          flat: bool = False,
          ) -> Period | _T_DT_PAIR | None:
    if others:
        others = ascend_start(period, other,  # type: ignore[assignment]
                              *others)
        period = others[0]
        max_end = period.end
        for other in others[1:]:
            if within(period, other.start):
                period = other
                max_end = max(other.end, max_end)
            else:
                return None
        result = (others[0].start, max_end)
    elif intersection(period, other, flat=True):
        result = (min(period.start, other.start), max(period.end, other.end))
    else:
        return join(period, other, flat=flat)

    return result if flat else Period(*result, False)


def intersection(period: PeriodProto,
                 other: PeriodProto,
                 *others: PeriodProto,
                 flat: bool = False,
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

    return _conv(max_start, min_end, flat)


def _conv(start: datetime.datetime, end: datetime.datetime, flat: bool,
          ) -> Period | tuple[datetime.datetime, datetime.datetime]:
    return (start, end) if flat else Period(start, end, False)


def difference(period: PeriodProto,
               other: PeriodProto,
               *others: PeriodProto,
               flat: bool = False,
               ) -> t.Generator[(Period | _T_DT_PAIR), None, None]:
    if others:
        # aggregate
        others = ascend_start(  # type: ignore[assignment]
            *(o for o in others + (other,)
              if intersection(period, o, flat=True))
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
            yield _conv(period.start, cross.start, flat=flat)

        # aggregate + mids
        for item in others[1:]:
            if x := union(item, cross):
                cross = t.cast(PeriodProto, x)
            else:
                yield _conv(cross.end, item.start, flat=flat)
                cross = item

        # last
        if period.end > cross.end:
            yield _conv(cross.end, period.end, flat=flat)

    elif x := intersection(period, other, flat=True):
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
            yield _conv(start=period.start, end=start, flat=flat)
            if period.end > end:  # I. right
                yield _conv(start=end, end=period.end, flat=flat)
        elif period.end != end:  # III. right
            yield _conv(start=end, end=period.end, flat=flat)
        # no `else` -- because `cross` equals `period`

    else:
        yield _conv(start=period.start, end=period.end, flat=flat)

from __future__ import annotations

import datetime
import operator
import typing as t


_F_START = "start"
_F_END = "end"
_T_DT_PAIR = tuple[datetime.datetime, datetime.datetime]
_SEP = "/"

_sort = operator.attrgetter(_F_START)


# TODO(d.burmistrov):
#  - timezone support
#  - review exceptions
#  - review Period class implementation
#  - do performance tests
#  - assert `start < end`
#  - treat `date` similar to `datetime`?


# base proto

class PeriodProto(t.Protocol):
    start: datetime.datetime
    end: datetime.datetime


class Period(PeriodProto):

    __slots__ = (_F_START, _F_END)

    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        object.__setattr__(self, _F_START, start)
        object.__setattr__(self, _F_END, end)
        # TODO(d.burmistrov): self.duration = end - start

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
            return Period(self.start,  # type: ignore[abstract]
                          self.end + other)
        else:
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
            return Period(self.start - other,  # type: ignore[abstract]
                          self.end - other)
        else:
            raise NotImplementedError

    def __rshift__(self, other: datetime.timedelta) -> Period:  # "p >> delta"
        if isinstance(other, datetime.timedelta):
            return Period(self.start + other,  # type: ignore[abstract]
                          self.end + other)
        else:
            raise NotImplementedError

    def __contains__(self, item: PeriodProto | datetime.datetime) -> bool:
        return within(self, item)

    @classmethod
    def fromisoformat(cls, s: str) -> Period:
        items = s.split(_SEP, maxsplit=1)
        if len(items) != 2:
            raise ValueError("Invalid period format")
        return Period(  # type: ignore[abstract]
            datetime.datetime.fromisoformat(items[0]),
            datetime.datetime.fromisoformat(items[1]),
        )

    def isoformat(self, sep="T", timespec="auto") -> str:
        return _SEP.join(
            datetime.datetime.isoformat(item, sep=sep, timespec=timespec)
            for item in (self.start, self.end)
        )

    # TODO(d.burmistrov): __deepcopy__
    def __copy__(self) -> Period:
        return Period(self.start, self.end)  # type: ignore[abstract]

    def copy(self) -> Period:
        return Period(self.start, self.end)  # type: ignore[abstract]

    def as_tuple(self) -> tuple[datetime.datetime, datetime.datetime]:
        return self.start, self.end

    # TODO(d.burmistrov): duration?
    def as_dict(self) -> dict[str, datetime.datetime]:
        return dict(start=self.start, end=self.end)


# base API

def within(period: PeriodProto, item: datetime.datetime | PeriodProto) -> bool:
    if isinstance(item, datetime.datetime):
        return period.start <= item <= period.end
    else:
        return (period.start <= item.start) and (item.end <= period.end)


def join(period: PeriodProto,
         other: PeriodProto,
         *others: PeriodProto,
         flat: bool = False,
         ) -> Period | _T_DT_PAIR | None:
    if others:
        others = sorted((period, other) + others,  # type: ignore[assignment]
                        key=_sort)
        period = others[0]
        for other in others[1:]:
            if period.end == other.start:
                period = other
            else:
                return None
        result = (others[0].start, others[-1].end)
    elif period.end == other.start:  # `p1` on the left
        result = (period.start, other.end)
    elif period.start == other.end:  # `p1` on the right
        result = (other.start, period.end)
    else:
        return None

    return result if flat else Period(*result)  # type: ignore[abstract]


def union(period: PeriodProto,
          other: PeriodProto,
          *others: PeriodProto,
          flat: bool = False,
          ) -> Period | _T_DT_PAIR | None:
    if others:
        others = sorted((period, other) + others,  # type: ignore[assignment]
                        key=_sort)
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

    return result if flat else Period(*result)  # type: ignore[abstract]


def intersection(period: PeriodProto,
                 other: PeriodProto,
                 *others: PeriodProto,
                 flat: bool = False,
                 ) -> t.Optional[Period | _T_DT_PAIR]:
    max_start = max(period.start, other.start)
    min_end = min(period.end, other.end)
    for p in others:
        if max_start >= min_end:
            return None
        max_start = max(p.start, max_start)
        min_end = min(p.end, min_end)

    if max_start >= min_end:
        return None
    elif flat:
        return max_start, min_end
    else:
        return Period(max_start, min_end)  # type: ignore[abstract]


def difference(period: PeriodProto,
               other: PeriodProto,
               *others: PeriodProto,
               flat: bool = False,
               ) -> t.Generator[(Period | _T_DT_PAIR), None, None]:
    raise NotImplementedError()

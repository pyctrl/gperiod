from __future__ import annotations
import datetime
import operator
import typing as t


_F_START = "start"
_F_END = "end"
_T_DT_PAIR = tuple[datetime.datetime, datetime.datetime]

_sort = operator.attrgetter(_F_START)


# TODO(d.burmistrov):
#  - timezone support
#  - review exceptions
#  - review Period class implementation
#  - do performance tests
#  - assert `start < end`
#  - treat `date` similar to `datetime`?


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

    def __add__(self, other) -> Period | None:  # "p1 + p2"
        if isinstance(other, datetime.timedelta):
            return Period(self.start,  # type: ignore[abstract]
                          self.end + other)
        else:
            return join(self, other)  # type: ignore[return-value]

    __radd__ = __add__

    def __and__(self, other) -> Period | None:  # "p1 & p2"
        return intersection(self, other)  # type: ignore[return-value]

    __rand__ = __and__

    @classmethod
    def fromisoformat(cls, s: str) -> Period:
        items = s.split("/", maxsplit=1)
        if len(items) != 2:
            raise ValueError("Invalid period format")
        return Period(  # type: ignore[abstract]
            datetime.datetime.fromisoformat(items[0]),
            datetime.datetime.fromisoformat(items[1]),
        )

    def isoformat(self, sep="T", timespec="auto") -> str:
        return "/".join(
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Period):  # TODO(d.burmistrov): questionable
            return NotImplemented
        return self.start == other.start and self.end == other.end


def within(p: PeriodProto, item: datetime.datetime | PeriodProto) -> bool:
    if isinstance(item, datetime.datetime):
        return p.start <= item <= p.end
    else:
        return (p.start <= item.start) and (item.end <= p.end)


def join(p1: PeriodProto,
         p2: PeriodProto,
         *periods: PeriodProto,
         flat: bool = False,
         ) -> Period | _T_DT_PAIR | None:
    if periods:
        periods = sorted((p1, p2) + periods,  # type: ignore[assignment]
                         key=_sort)
        p1 = periods[0]
        for p2 in periods[1:]:
            if p1.end == p2.start:
                p1 = p2
            else:
                return None
        result = (periods[0].start, periods[-1].end)
    elif p1.end == p2.start:  # `p1` on the left
        result = (p1.start, p2.end)
    elif p1.start == p2.end:  # `p1` on the right
        result = (p2.start, p1.end)
    else:
        return None

    return result if flat else Period(*result)  # type: ignore[abstract]


def union(p1: PeriodProto,
          p2: PeriodProto,
          *periods: PeriodProto,
          flat: bool = False,
          ) -> Period | _T_DT_PAIR | None:
    if periods:
        periods = sorted((p1, p2) + periods,  # type: ignore[assignment]
                         key=_sort)
        p1 = periods[0]
        max_end = p1.end
        for p2 in periods[1:]:
            if within(p1, p2.start):
                p1 = p2
                max_end = max(p2.end, max_end)
            else:
                return None
        result = (periods[0].start, max_end)
    elif intersection(p1, p2, flat=True):
        result = (min(p1.start, p2.start), max(p1.end, p2.end))
    else:
        return join(p1, p2, flat=flat)

    return result if flat else Period(*result)  # type: ignore[abstract]


def split(p: PeriodProto,
          *datetimes: datetime.datetime,
          ) -> t.Generator[Period | _T_DT_PAIR, None, None]:
    raise NotImplementedError()


def intersection(p1: PeriodProto,
                 p2: PeriodProto,
                 *periods: PeriodProto,
                 flat: bool = False
                 ) -> t.Optional[Period | _T_DT_PAIR]:
    max_start = max(p1.start, p2.start)
    min_end = min(p1.end, p2.end)
    for p in periods:
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


def difference(p1: PeriodProto,
               p2: PeriodProto,
               *periods: PeriodProto,
               flat: bool = False,
               ) -> t.Generator[(Period | _T_DT_PAIR), None, None]:
    raise NotImplementedError()

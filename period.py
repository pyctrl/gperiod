from __future__ import annotations
import datetime
import typing as t


_F_START = "start"
_F_END = "end"
_T_DT_PAIR = tuple[datetime.datetime, datetime.datetime]


# TODO(d.burmistrov):
#  - timezone support
#  - review exceptions
#  - review Period class implementation
#  - do performance tests
#  - assert `start < end`


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

    def __setattr__(self, key, value):
        raise NotImplementedError("method not allowed")

    def __delattr__(self, item):
        raise NotImplementedError("method not allowed")

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


def join(*periods: PeriodProto,
         flat: bool = False,
         ) -> Period | _T_DT_PAIR:
    if not periods:
        raise TypeError("not enough periods")

    result = [periods[0].start, periods[0].end]
    for p in periods[1:]:
        if p.end == result[0]:  # `p` on the left
            result[0] = p.start
        elif p.start == result[1]:  # `p` on the right
            result[1] = p.end
        else:
            raise ValueError("periods must be consecutive")

    if flat:
        return t.cast(tuple[datetime.datetime, datetime.datetime],
                      tuple(result))
    else:
        return Period(*result)  # type: ignore[abstract]


def union(*periods: PeriodProto,
          flat: bool = False,
          ) -> Period | _T_DT_PAIR:
    raise NotImplementedError()


def split(p: PeriodProto,
          *datetimes: datetime.datetime,
          ) -> t.Generator[Period | _T_DT_PAIR, None, None]:
    raise NotImplementedError()


def intersection(*periods: PeriodProto,
                 flat: bool = False
                 ) -> t.Optional[Period | _T_DT_PAIR]:
    raise NotImplementedError()


def difference(p: PeriodProto,
               *periods: PeriodProto,
               flat: bool = False,
               ) -> t.Generator[Period | _T_DT_PAIR, None, None]:
    raise NotImplementedError()

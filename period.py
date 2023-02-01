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


class PeriodProto(t.Protocol):
    start: datetime.datetime
    end: datetime.datetime


class Period(PeriodProto):

    __slots__ = (_F_START, _F_END)

    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        object.__setattr__(self, _F_START, start)
        object.__setattr__(self, _F_END, end)
        # TODO(d.burmistrov): self.duration = end - start

    def __setattr__(self, key, value):
        raise NotImplementedError("method not allowed")

    def __delattr__(self, item):
        raise NotImplementedError("method not allowed")


def join(*periods: PeriodProto,
         flat: bool = False,
         ) -> Period | _T_DT_PAIR:
    raise NotImplementedError()


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

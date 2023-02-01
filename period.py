import datetime
import typing as t


_F_START = "start"
_F_END = "end"
_T_DT_PAIR = t.Tuple[datetime.datetime, datetime.datetime]


# TODO(d.burmistrov):
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
    pass


def union(*periods: PeriodProto,
          flat: bool = False,
          ) -> Period | _T_DT_PAIR:
    pass


def split(p: PeriodProto,
          *datetimes: datetime.datetime,
          ) -> t.Generator[Period | _T_DT_PAIR, None, None]:
    pass


def intersection(*periods: PeriodProto,
                 flat: bool = False
                 ) -> t.Optional[Period | _T_DT_PAIR]:
    pass


def difference(p: PeriodProto,
               *periods: PeriodProto,
               flat: bool = False,
               ) -> t.Generator[Period | _T_DT_PAIR, None, None]:
    pass

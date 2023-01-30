import datetime
import typing as t


_T_DT_PAIR = t.Tuple[datetime.datetime, datetime.datetime]


class PeriodProto(t.Protocol):
    start: datetime.datetime
    end: datetime.datetime


# TODO(d.burmistrov): temporary fake period
class Period:
    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        self.start = start
        self.end = end


def join(*periods: PeriodProto,
         return_datetime: bool = False,
         ) -> Period | _T_DT_PAIR:
    pass


def union(*periods: PeriodProto,
          return_datetime: bool = False,
          ) -> Period | _T_DT_PAIR:
    pass


def split(p: PeriodProto,
          *datetimes: datetime.datetime,
          ) -> t.Generator[Period | _T_DT_PAIR, None, None]:
    pass


def intersection(*periods: PeriodProto,
                 return_datetime: bool = False
                 ) -> t.Optional[Period | _T_DT_PAIR]:
    pass


def difference(p: PeriodProto,
               *periods: PeriodProto,
               return_datetime: bool = False,
               ) -> t.Generator[Period | _T_DT_PAIR, None, None]:
    pass

from datetime import datetime
import operator
import typing as t

from gperiod import g


_SORT_KEY_END = operator.attrgetter(g._F_END)


# sorting

def descend_end(*periods: g.PeriodProto, reverse: bool = False,
                ) -> t.List[g.PeriodProto]:
    f"""Sort periods by '{g._F_END}' attribute

    Sorting is descending by default.

    :param periods: period-like objects
    :param reverse: switch descending to ascending
    """

    return sorted(periods, key=_SORT_KEY_END, reverse=(not reverse))


# misc

def to_timestamps(*periods: g.PeriodProto,
                  ) -> t.Generator[datetime, None, None]:
    """Flatten periods into sequence of edges

    :param periods: period-like objects
    """

    for period in periods:
        yield period.start
        yield period.end

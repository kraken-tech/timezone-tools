import datetime
from collections.abc import Callable
from typing import Any

from dateutil import parser as date_parser
from dateutil import relativedelta
from django.utils import timezone

from datetime_tools import localtime


class DateTimeFactory:
    """
    A class for generating datetimes in a certain timezone.
    """

    def __init__(
        self,
        str_to_dt_fn: Callable[[str], datetime.datetime],
        now_fn: Callable[[], datetime.datetime],
    ) -> None:
        self._str_to_dt_fn = str_to_dt_fn
        self._now_fn = now_fn

    def dt(self, dt_str: str) -> datetime.datetime:
        """
        Return a datetime from a string.
        """
        return self._str_to_dt_fn(dt_str)

    def now(self) -> datetime.datetime:
        return self._now_fn()

    def in_the_past(self, **kwargs: Any) -> datetime.datetime:
        return self.now() - relativedelta.relativedelta(**kwargs)

    def in_the_future(self, **kwargs: Any) -> datetime.datetime:
        return self.now() + relativedelta.relativedelta(**kwargs)


def _utc_dt(value: str) -> datetime.datetime:
    """
    Return a UTC datetime from the passed string.

    Examples: datetime('31/5/2010') or datetime("Aug 28 1999 12:00AM")

    UK date format is assumed, so DD/MM/YYYY works as expected.
    """
    _datetime = date_parser.parse(value, dayfirst=("/" in value))
    return _datetime.replace(tzinfo=datetime.timezone.utc)


def _local_dt(value: str) -> datetime.datetime:
    """
    Return a LOCAL datetime from the passed string.
    """
    _datetime = date_parser.parse(value, dayfirst=("/" in value))
    return timezone.make_aware(_datetime)


utc = DateTimeFactory(str_to_dt_fn=_utc_dt, now_fn=timezone.now)
local = DateTimeFactory(str_to_dt_fn=_local_dt, now_fn=localtime.now)


def date(value: str) -> datetime.date:
    _datetime = date_parser.parse(value, dayfirst=("/" in value))
    return _datetime.date()


def time(_time: str) -> datetime.time:
    return datetime.datetime.strptime(_time, "%H:%M").time()

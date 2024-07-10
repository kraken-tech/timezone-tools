import dataclasses
import datetime
import zoneinfo

from dateutil import relativedelta


@dataclasses.dataclass(frozen=True, init=False)
class Clock:
    """Get the current date/time in a specific timezone."""

    tzinfo: zoneinfo.ZoneInfo

    def __init__(self, timezone: str) -> None:
        object.__setattr__(self, "tzinfo", zoneinfo.ZoneInfo(timezone))

    # Current time/date

    def now(self) -> datetime.datetime:
        return datetime.datetime.now(tz=self.tzinfo)

    def today(self) -> datetime.date:
        return self.now().date()

    # Relative times/dates

    def yesterday(self) -> datetime.date:
        return self.days_in_the_past(1)

    def tomorrow(self) -> datetime.date:
        return self.days_in_the_future(1)

    def days_in_the_past(self, days: int) -> datetime.date:
        return self.today() - datetime.timedelta(days=days)

    def days_in_the_future(self, days: int) -> datetime.date:
        return self.today() + datetime.timedelta(days=days)

    def months_in_the_past(self, months: int) -> datetime.date:
        """Get the date some number of months ago.

        If the target month does not have enough days, the closest day will be
        returned (e.g. 3 months before July 31st is April 30th, not April
        31st).
        """
        return self.today() - relativedelta.relativedelta(months=months)

    def months_in_the_future(self, months: int) -> datetime.date:
        """Get the date some number of months in the future.

        If the target month does not have enough days, the closest day will be
        returned (e.g. 4 months after July 31st is November 30th, not November
        31st).
        """
        return self.today() + relativedelta.relativedelta(months=months)

    def is_in_the_past(
        self, candidate: datetime.datetime | datetime.date
    ) -> bool:
        """Check whether a date/time is before the current date/time."""
        if isinstance(candidate, datetime.datetime):
            return candidate < self.now()
        else:
            return candidate < self.today()

    def is_in_the_future(
        self, candidate: datetime.datetime | datetime.date
    ) -> bool:
        """Check whether a date/time is after the current date/time."""
        if isinstance(candidate, datetime.datetime):
            return self.now() < candidate
        else:
            return self.today() < candidate

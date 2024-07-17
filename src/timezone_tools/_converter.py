import dataclasses
import datetime as datetime_
import zoneinfo
from typing import Literal

from dateutil import relativedelta
from typing_extensions import assert_never


@dataclasses.dataclass(frozen=True, init=False)
class TimezoneConverter:
    """Manage dates and datetimes in a specific timezone."""

    tzinfo: zoneinfo.ZoneInfo

    def __init__(self, timezone: str) -> None:
        object.__setattr__(self, "tzinfo", zoneinfo.ZoneInfo(timezone))

    # Constructors

    def datetime(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        *,
        fold: int = 0,
    ) -> datetime_.datetime:
        """Create a timezone-aware datetime."""
        return datetime_.datetime(
            year,
            month,
            day,
            hour,
            minute,
            second,
            microsecond,
            fold=fold,
            tzinfo=self.tzinfo,
        )

    def combine(
        self, date: datetime_.date, time: datetime_.time
    ) -> datetime_.datetime:
        """Create a timezone-aware datetime from a date and time.

        If the time is timezone-aware, it will be converted to this timezone;
        if it is naive, it will be made timezone-aware in this timezone.
        """
        inferred_timezone = time.tzinfo or self.tzinfo
        return datetime_.datetime.combine(
            date, time, tzinfo=inferred_timezone
        ).astimezone(self.tzinfo)

    @property
    def far_past(self) -> datetime_.datetime:
        return datetime_.datetime.min.replace(tzinfo=self.tzinfo)

    @property
    def far_future(self) -> datetime_.datetime:
        return datetime_.datetime.max.replace(tzinfo=self.tzinfo)

    # Conversions

    class AlreadyAware(Exception):
        pass

    def make_aware(self, datetime: datetime_.datetime) -> datetime_.datetime:
        """Make a naive datetime timezone-aware in this timezone.

        Raises:
            AlreadyAware: The datetime is already timezone-aware.
                Use `localize` to convert the time into this timezone.
        """
        if datetime.tzinfo:
            raise self.AlreadyAware

        return datetime.replace(tzinfo=self.tzinfo)

    class NaiveDatetime(Exception):
        pass

    def localize(self, datetime: datetime_.datetime) -> datetime_.datetime:
        """Localize a timezone-aware datetime to this timezone.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        if not datetime.tzinfo:
            raise self.NaiveDatetime

        return datetime.astimezone(self.tzinfo)

    def date(self, datetime: datetime_.datetime) -> datetime_.date:
        """Get the date in this timezone at a moment in time.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        return self.localize(datetime).date()

    # Quantize

    ROUND_DOWN: Literal["ROUND_DOWN"] = "ROUND_DOWN"
    ROUND_UP: Literal["ROUND_UP"] = "ROUND_UP"

    class ResolutionTooLarge(Exception):
        pass

    def quantize(
        self,
        datetime: datetime_.datetime,
        resolution: datetime_.timedelta,
        rounding: Literal["ROUND_UP", "ROUND_DOWN"],
    ) -> datetime_.datetime:
        """'Round' a datetime to some resolution.

        This will truncate the datetime to a whole value of the resolution in
        the given timezone. The resolution must not exceed a day (because then
        the reference point is ambiguous.)

        Raises:
            ResolutionTooLarge: The resolution is too large.
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        if resolution > datetime_.timedelta(days=1):
            raise self.ResolutionTooLarge

        # start with round-down and round-up candidates at the start of the day
        # in this timezone
        lower_candidate = self.combine(
            self.date(datetime), datetime_.time(00, 00, 00)
        )
        upper_candidate = lower_candidate + resolution

        # walk forwards in steps of `resolution` until the datetime is inside
        # the bounds
        while upper_candidate < datetime:
            lower_candidate, upper_candidate = (
                upper_candidate,
                upper_candidate + resolution,
            )

        if rounding == self.ROUND_DOWN:
            return lower_candidate
        elif rounding == self.ROUND_UP:
            return upper_candidate
        else:  # pragma: no cover
            assert_never(rounding)

    # Relative dates and times

    def day_before(
        self, when: datetime_.datetime | datetime_.date
    ) -> datetime_.date:
        """Find the date of the day before this moment in this timezone.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        if isinstance(when, datetime_.datetime):
            date = self.date(when)
        else:
            date = when

        return date - datetime_.timedelta(days=1)

    def day_after(
        self, when: datetime_.datetime | datetime_.date
    ) -> datetime_.date:
        """Find the date of the day after this moment in this timezone.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        if isinstance(when, datetime_.datetime):
            date = self.date(when)
        else:
            date = when

        return date + datetime_.timedelta(days=1)

    def midnight(
        self, when: datetime_.datetime | datetime_.date
    ) -> datetime_.datetime:
        """Find the moment of midnight on this day in this timezone.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        if isinstance(when, datetime_.datetime):
            date = self.date(when)
        else:
            date = when

        return self.combine(date, datetime_.time(00, 00))

    def midday(
        self, when: datetime_.datetime | datetime_.date
    ) -> datetime_.datetime:
        """Find the moment of midday on this day in this timezone.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        if isinstance(when, datetime_.datetime):
            date = self.date(when)
        else:
            date = when

        return self.combine(date, datetime_.time(12, 00))

    def next_midnight(
        self, when: datetime_.datetime | datetime_.date
    ) -> datetime_.datetime:
        """Find the moment of midnight at the end of this day in this timezone.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        return self.midnight(self.day_after(when))

    def start_of_month(
        self, datetime: datetime_.datetime
    ) -> datetime_.datetime:
        """Find the moment of the start of this month in this timezone.

        This will be midnight on the first day of the month.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        return self.midnight(self.first_day_of_month(datetime))

    def end_of_month(self, datetime: datetime_.datetime) -> datetime_.datetime:
        """Find the moment of the end of this month in this timezone.

        This will be midnight on the first day of the following month.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        return self.start_of_month(datetime) + relativedelta.relativedelta(
            months=1
        )

    def first_day_of_month(
        self, datetime: datetime_.datetime
    ) -> datetime_.date:
        """Find the date of the first day of this month in this timezone.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        return self.date(datetime).replace(day=1)

    def last_day_of_month(
        self, datetime: datetime_.datetime
    ) -> datetime_.date:
        """Find the date of the last day of this month in this timezone.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        return self.first_day_of_month(datetime) + relativedelta.relativedelta(
            months=1, days=-1
        )

    def is_midnight(self, datetime: datetime_.datetime) -> bool:
        """Check whether a time is midnight in this timezone.

        Raises:
            NaiveDatetime: The datetime is naive, so we do not know which
                timezone to localize from. Use `make_aware` to make a naive
                datetime timezone-aware.
        """
        return self.localize(datetime).time() == datetime_.time(00, 00)

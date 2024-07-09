import datetime as datetime_
import zoneinfo
from typing import Literal

from typing_extensions import assert_never


class TimezoneConverter:
    """Manage dates and datetimes in a specific timezone."""

    def __init__(self, timezone: str) -> None:
        self.tzinfo = zoneinfo.ZoneInfo(timezone)

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

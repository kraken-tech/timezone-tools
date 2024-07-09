import datetime as datetime_
import zoneinfo


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

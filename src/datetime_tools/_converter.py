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

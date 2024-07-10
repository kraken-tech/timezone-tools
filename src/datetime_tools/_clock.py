import datetime
import zoneinfo


class Clock:
    """Get the current date/time in a specific timezone."""

    def __init__(self, timezone: str) -> None:
        self.tzinfo = zoneinfo.ZoneInfo(timezone)

    # Current time/date

    def now(self) -> datetime.datetime:
        return datetime.datetime.now(tz=self.tzinfo)

    def today(self) -> datetime.date:
        return self.now().date()

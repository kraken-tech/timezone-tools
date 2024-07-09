import datetime
import zoneinfo

from datetime_tools import TimezoneConverter

# Note [Use Europe/Paris for tests]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# These tests use the Europe/Paris timezone. This is to make sure that
# localized times cannot be confused with naive times that have had timezone
# info added. If a naive time is assumed to be in UTC, it will be different
# when localized to Europe/Paris, regardless of DST.


def test_datetime() -> None:
    paris_time = TimezoneConverter("Europe/Paris")

    assert paris_time.datetime(2024, 7, 9, 12, 45, 0) == datetime.datetime(
        2024, 7, 9, 12, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
    )


def test_combine_naive() -> None:
    """Check that a naive time is made timezone-aware."""
    paris_time = TimezoneConverter("Europe/Paris")

    assert paris_time.combine(
        datetime.date(2024, 7, 9), datetime.time(12, 45, 0)
    ) == datetime.datetime(
        2024, 7, 9, 12, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
    )


def test_combine_and_convert() -> None:
    """Check that a timezone-aware time is converted."""
    paris_time = TimezoneConverter("Europe/Paris")

    assert paris_time.combine(
        datetime.date(2024, 7, 9),
        datetime.time(12, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/London")),
    ) == datetime.datetime(
        2024, 7, 9, 13, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
    )


def test_far_past() -> None:
    paris_time = TimezoneConverter("Europe/Paris")

    assert paris_time.far_past == datetime.datetime(
        1, 1, 1, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
    )


def test_far_future() -> None:
    paris_time = TimezoneConverter("Europe/Paris")

    assert paris_time.far_future == datetime.datetime(
        9999,
        12,
        31,
        23,
        59,
        59,
        999999,
        tzinfo=zoneinfo.ZoneInfo("Europe/Paris"),
    )

import datetime
import zoneinfo

import pytest

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


def test_make_aware() -> None:
    paris_time = TimezoneConverter("Europe/Paris")

    assert paris_time.make_aware(
        datetime.datetime(2024, 7, 9, 12, 45, 0, tzinfo=None)
    ) == datetime.datetime(
        2024, 7, 9, 12, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
    )


def test_make_aware_requires_naive_datetime() -> None:
    paris_time = TimezoneConverter("Europe/Paris")
    already_aware = datetime.datetime(
        2024, 7, 9, 12, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
    )

    with pytest.raises(paris_time.AlreadyAware):
        paris_time.make_aware(already_aware)


def test_localize() -> None:
    paris_time = TimezoneConverter("Europe/Paris")

    assert paris_time.localize(
        datetime.datetime(
            2024, 7, 9, 12, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/London")
        )
    ) == datetime.datetime(
        2024, 7, 9, 13, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
    )


def test_localize_requires_aware_datetime() -> None:
    paris_time = TimezoneConverter("Europe/Paris")
    naive_datetime = datetime.datetime(2024, 7, 9, 12, 45, 0, tzinfo=None)

    with pytest.raises(paris_time.NaiveDatetime):
        paris_time.localize(naive_datetime)


def test_date() -> None:
    paris_time = TimezoneConverter("Europe/Paris")

    assert paris_time.date(
        datetime.datetime(
            2024, 7, 9, 12, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
        )
    ) == datetime.date(2024, 7, 9)


def test_date_from_different_timezone() -> None:
    paris_time = TimezoneConverter("Europe/Paris")

    # just before midnight in London is after midnight in Paris
    assert paris_time.date(
        datetime.datetime(
            2024, 7, 8, 23, 30, 0, tzinfo=zoneinfo.ZoneInfo("Europe/London")
        )
    ) == datetime.date(2024, 7, 9)


def test_date_requires_aware_datetime() -> None:
    paris_time = TimezoneConverter("Europe/Paris")
    naive_datetime = datetime.datetime(2024, 7, 9, 12, 45, 0, tzinfo=None)

    with pytest.raises(paris_time.NaiveDatetime):
        paris_time.date(naive_datetime)

import datetime
import zoneinfo
from typing import Literal

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


_half_hour = datetime.timedelta(minutes=30)
_two_hours = datetime.timedelta(hours=2)
_day = datetime.timedelta(days=1)


@pytest.mark.parametrize(
    "initial_datetime, resolution, rounding, expected_result",
    (
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 12, 45, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            _half_hour,
            TimezoneConverter.ROUND_DOWN,
            datetime.datetime(
                2024, 7, 9, 12, 30, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="same timezone, round down 1/2 hour",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 12, 45, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            _half_hour,
            TimezoneConverter.ROUND_UP,
            datetime.datetime(
                2024, 7, 9, 13, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="same timezone, round up 1/2 hour",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 45, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            _two_hours,
            TimezoneConverter.ROUND_DOWN,
            datetime.datetime(
                2024, 7, 9, 12, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="same timezone, round down 2 hours",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 45, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            _two_hours,
            TimezoneConverter.ROUND_UP,
            datetime.datetime(
                2024, 7, 9, 14, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="same timezone, round up 2 hours",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 45, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            _day,
            TimezoneConverter.ROUND_DOWN,
            datetime.datetime(
                2024, 7, 9, 00, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="same timezone, round down 1 day",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 45, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            _day,
            TimezoneConverter.ROUND_UP,
            datetime.datetime(
                2024, 7, 10, 00, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="same timezone, round up 1 day",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 12, 45, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            _half_hour,
            TimezoneConverter.ROUND_DOWN,
            datetime.datetime(
                2024, 7, 9, 13, 30, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="different timezone, round down 1/2 hour",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 12, 45, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            _half_hour,
            TimezoneConverter.ROUND_UP,
            datetime.datetime(
                2024, 7, 9, 14, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="different timezone, round up 1/2 hour",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 12, 45, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            _two_hours,
            TimezoneConverter.ROUND_DOWN,
            datetime.datetime(
                2024, 7, 9, 12, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="different timezone, round down 2 hours",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 45, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            _two_hours,
            TimezoneConverter.ROUND_UP,
            datetime.datetime(
                2024, 7, 9, 16, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="different timezone, round up 2 hours",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 23, 30, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            _day,
            TimezoneConverter.ROUND_DOWN,
            datetime.datetime(
                2024, 7, 10, 00, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="different timezone, round down 1 day",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 23, 30, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            _day,
            TimezoneConverter.ROUND_UP,
            datetime.datetime(
                2024, 7, 11, 00, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            id="different timezone, round up 1 day",
        ),
    ),
)
def test_quantize(
    initial_datetime: datetime.datetime,
    resolution: datetime.timedelta,
    rounding: Literal["ROUND_UP", "ROUND_DOWN"],
    expected_result: datetime.datetime,
) -> None:
    paris_time = TimezoneConverter("Europe/Paris")

    assert (
        paris_time.quantize(initial_datetime, resolution, rounding)
        == expected_result
    )


def test_quantize_requires_resolution_less_than_a_day() -> None:
    paris_time = TimezoneConverter("Europe/Paris")
    some_datetime = datetime.datetime(
        2024, 7, 9, 12, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
    )

    with pytest.raises(paris_time.ResolutionTooLarge):
        paris_time.quantize(
            some_datetime,
            datetime.timedelta(hours=25),
            rounding=paris_time.ROUND_DOWN,
        )


def test_quantize_requires_aware_datetime() -> None:
    paris_time = TimezoneConverter("Europe/Paris")
    naive_datetime = datetime.datetime(2024, 7, 9, 12, 45, 0, tzinfo=None)

    with pytest.raises(paris_time.NaiveDatetime):
        paris_time.quantize(
            naive_datetime,
            datetime.timedelta(minutes=1),
            rounding=paris_time.ROUND_DOWN,
        )

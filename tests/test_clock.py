import dataclasses
import datetime
import zoneinfo

import pytest
import time_machine

from timezone_tools import Clock

# See Note [Use Europe/Paris for tests]


def test_timezone_cannot_be_changed() -> None:
    clock = Clock("Europe/Paris")

    with pytest.raises(dataclasses.FrozenInstanceError):
        clock.tzinfo = zoneinfo.ZoneInfo("Europe/London")  # type: ignore[misc]


def test_now() -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(  # assumes UTC
        datetime.datetime(2024, 7, 9, 12, 45, 00), tick=False
    ):
        assert clock.now() == datetime.datetime(
            2024, 7, 9, 14, 45, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
        )


def test_today() -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(  # assumes UTC
        datetime.datetime(2024, 7, 9, 22, 45, 00), tick=False
    ):
        assert clock.today() == datetime.date(2024, 7, 10)


def test_yesterday() -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(  # assumes UTC
        datetime.datetime(2024, 7, 9, 22, 45, 00), tick=False
    ):
        assert clock.yesterday() == datetime.date(2024, 7, 9)


def test_tomorrow() -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(  # assumes UTC
        datetime.datetime(2024, 7, 9, 22, 45, 00), tick=False
    ):
        assert clock.tomorrow() == datetime.date(2024, 7, 11)


def test_days_in_the_past() -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(  # assumes UTC
        datetime.datetime(2024, 7, 9, 22, 45, 00), tick=False
    ):
        assert clock.days_in_the_past(3) == datetime.date(2024, 7, 7)


def test_days_in_the_future() -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(  # assumes UTC
        datetime.datetime(2024, 7, 9, 22, 45, 00), tick=False
    ):
        assert clock.days_in_the_future(3) == datetime.date(2024, 7, 13)


@pytest.mark.parametrize(
    "today, three_months_ago",
    (
        pytest.param(
            datetime.date(2024, 7, 1), datetime.date(2024, 4, 1), id="1st"
        ),
        pytest.param(
            datetime.date(2024, 7, 28), datetime.date(2024, 4, 28), id="28th"
        ),
        pytest.param(
            datetime.date(2024, 7, 31), datetime.date(2024, 4, 30), id="31st"
        ),
    ),
)
def test_months_in_the_past(
    today: datetime.date, three_months_ago: datetime.date
) -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(today, tick=False):
        assert clock.months_in_the_past(3) == three_months_ago


@pytest.mark.parametrize(
    "today, four_months_time",
    (
        pytest.param(
            datetime.date(2024, 7, 1), datetime.date(2024, 11, 1), id="1st"
        ),
        pytest.param(
            datetime.date(2024, 7, 28), datetime.date(2024, 11, 28), id="28th"
        ),
        pytest.param(
            datetime.date(2024, 7, 31), datetime.date(2024, 11, 30), id="31st"
        ),
    ),
)
def test_months_in_the_future(
    today: datetime.date, four_months_time: datetime.date
) -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(today, tick=False):
        assert clock.months_in_the_future(4) == four_months_time


@pytest.mark.parametrize(
    "when, is_in_the_past",
    (
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 59, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            True,
            id="same timezone, past",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 14, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            False,
            id="same timezone, now",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 14, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            False,
            id="same timezone, future",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 12, 59, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            True,
            id="different timezone, past",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 00, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            False,
            id="different timezone, now",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 1, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            False,
            id="different timezone, future",
        ),
        pytest.param(
            datetime.date(2024, 7, 8),
            True,
            id="day before",
        ),
        pytest.param(
            datetime.date(2024, 7, 9),
            False,
            id="same day",
        ),
        pytest.param(
            datetime.date(2024, 7, 10),
            False,
            id="day after",
        ),
    ),
)
def test_is_in_the_past(
    when: datetime.datetime | datetime.date, is_in_the_past: bool
) -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(
        datetime.datetime(2024, 7, 9, 12, 00, tzinfo=zoneinfo.ZoneInfo("UTC")),
        tick=False,
    ):
        assert clock.is_in_the_past(when) is is_in_the_past


@pytest.mark.parametrize(
    "when, is_in_the_future",
    (
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 59, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            False,
            id="same timezone, past",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 14, 00, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            False,
            id="same timezone, now",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 14, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
            ),
            True,
            id="same timezone, future",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 12, 59, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            False,
            id="different timezone, past",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 00, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            False,
            id="different timezone, now",
        ),
        pytest.param(
            datetime.datetime(
                2024, 7, 9, 13, 1, tzinfo=zoneinfo.ZoneInfo("Europe/London")
            ),
            True,
            id="different timezone, future",
        ),
        pytest.param(
            datetime.date(2024, 7, 8),
            False,
            id="day before",
        ),
        pytest.param(
            datetime.date(2024, 7, 9),
            False,
            id="same day",
        ),
        pytest.param(
            datetime.date(2024, 7, 10),
            True,
            id="day after",
        ),
    ),
)
def test_is_in_the_future(
    when: datetime.datetime | datetime.date, is_in_the_future: bool
) -> None:
    clock = Clock("Europe/Paris")

    with time_machine.travel(
        datetime.datetime(2024, 7, 9, 12, 00, tzinfo=zoneinfo.ZoneInfo("UTC")),
        tick=False,
    ):
        assert clock.is_in_the_future(when) is is_in_the_future

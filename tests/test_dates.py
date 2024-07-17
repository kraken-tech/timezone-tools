import datetime

import pytest

import timezone_tools


@pytest.mark.parametrize(
    "date, is_last_day_of_month",
    (
        (datetime.date(2024, 1, 31), True),
        (datetime.date(2023, 2, 28), True),
        (datetime.date(2024, 2, 29), True),  # leap year
        (datetime.date(2024, 12, 31), True),  # end of year
        (datetime.date(2024, 4, 30), True),
        (datetime.date(2024, 1, 30), False),
        (datetime.date(2024, 2, 28), False),  # leap year
    ),
)
def test_is_last_day_of_month(
    date: datetime.date, is_last_day_of_month: bool
) -> None:
    assert timezone_tools.is_last_day_of_month(date) is is_last_day_of_month


def test_is_last_day_of_month_requires_date() -> None:
    # See Note [datetimes are dates]
    with pytest.raises(TypeError):
        timezone_tools.is_last_day_of_month(datetime.datetime(2024, 1, 1))


@pytest.mark.parametrize(
    "period, day_of_month, latest_date",
    (
        pytest.param(
            (datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)),
            9,
            datetime.date(2024, 12, 9),
            id="in range",
        ),
        pytest.param(
            (datetime.date(2024, 1, 1), datetime.date(2024, 12, 8)),
            9,
            datetime.date(2024, 11, 9),
            id="in previous month",
        ),
        pytest.param(
            (datetime.date(2024, 1, 1), datetime.date(2024, 5, 1)),
            31,
            datetime.date(2024, 3, 31),
            id="short month",
        ),
        pytest.param(
            (datetime.date(2024, 1, 1), datetime.date(2024, 1, 31)),
            1,
            datetime.date(2024, 1, 1),
            id="period start",
        ),
        pytest.param(
            (datetime.date(2024, 1, 1), datetime.date(2024, 1, 31)),
            31,
            datetime.date(2024, 1, 31),
            id="period end",
        ),
    ),
)
def test_latest_date_for_day(
    period: tuple[datetime.date, datetime.date],
    day_of_month: int,
    latest_date: datetime.date,
) -> None:
    assert (
        timezone_tools.latest_date_for_day(period, day_of_month) == latest_date
    )


def test_latest_date_for_day_not_found() -> None:
    with pytest.raises(timezone_tools.DateNotFound):
        timezone_tools.latest_date_for_day(
            (datetime.date(2024, 1, 1), datetime.date(2024, 1, 30)), 31
        )


@pytest.mark.parametrize("day_of_month", (-1, 0, 32))
def test_latest_date_for_day_invalid_day(day_of_month: int) -> None:
    with pytest.raises(timezone_tools.DateNotFound):
        timezone_tools.latest_date_for_day(
            (datetime.date(2024, 1, 1), datetime.date(2024, 1, 31)),
            day_of_month,
        )


def test_latest_date_for_day_invalid_range() -> None:
    """Check that the period must start before it ends."""
    with pytest.raises(ValueError):
        timezone_tools.latest_date_for_day(
            (datetime.date(2024, 1, 2), datetime.date(2024, 1, 1)), 1
        )


def test_latest_date_for_day_requires_dates() -> None:
    # See Note [datetimes are dates]
    with pytest.raises(TypeError):
        timezone_tools.latest_date_for_day(
            (datetime.datetime(2024, 1, 2), datetime.datetime(2024, 1, 1)), 1
        )


@pytest.mark.parametrize(
    "after_date, preferred_day_of_month, closest_match",
    (
        pytest.param(
            datetime.date(2024, 1, 1),
            1,
            datetime.date(2024, 2, 1),
            id="one month after",
        ),
        pytest.param(
            datetime.date(2024, 1, 20),
            10,
            datetime.date(2024, 2, 10),
            id="during next month",
        ),
        pytest.param(
            datetime.date(2024, 4, 5),
            31,
            datetime.date(2024, 4, 30),
            id="end of current month",
        ),
        pytest.param(
            datetime.date(2023, 1, 30),
            30,
            datetime.date(2023, 2, 28),
            id="end of next month",
        ),
        pytest.param(
            datetime.date(2024, 1, 30),
            30,
            datetime.date(2024, 2, 29),
            id="end of next month (leap year)",
        ),
    ),
)
def test_closest_upcoming_match(
    after_date: datetime.date,
    preferred_day_of_month: int,
    closest_match: datetime.date,
) -> None:
    assert (
        timezone_tools.closest_upcoming_match(
            preferred_day_of_month, after_date=after_date
        )
        == closest_match
    )


@pytest.mark.parametrize("preferred_day_of_month", (-1, 0, 32))
def test_closest_upcoming_match_invalid_day(
    preferred_day_of_month: int,
) -> None:
    with pytest.raises(ValueError):
        timezone_tools.closest_upcoming_match(
            preferred_day_of_month, after_date=datetime.date(2024, 1, 1)
        )


def test_closest_upcoming_match_requires_date() -> None:
    # See Note [datetimes are dates]
    with pytest.raises(TypeError):
        timezone_tools.closest_upcoming_match(
            1, after_date=datetime.datetime(2024, 1, 1)
        )


def test_iter_dates() -> None:
    iterator = timezone_tools.iter_dates(
        datetime.date(2024, 1, 1), datetime.date(2024, 1, 4)
    )

    assert next(iterator) == datetime.date(2024, 1, 1)
    assert next(iterator) == datetime.date(2024, 1, 2)
    assert next(iterator) == datetime.date(2024, 1, 3)
    with pytest.raises(StopIteration):
        next(iterator)


@pytest.mark.parametrize(
    "start, stop",
    (
        pytest.param(
            datetime.date(2024, 1, 2),
            datetime.date(2024, 1, 1),
            id="stop before start",
        ),
        pytest.param(
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 1),
            id="stop at start",
        ),
    ),
)
def test_iter_dates_invalid_range(
    start: datetime.date, stop: datetime.date
) -> None:
    iterator = timezone_tools.iter_dates(start, stop)
    with pytest.raises(ValueError):
        next(iterator)


def test_iter_dates_requires_dates() -> None:
    # See Note [datetimes are dates]
    iterator = timezone_tools.iter_dates(
        datetime.datetime(2024, 1, 1), datetime.datetime(2024, 1, 4)
    )
    with pytest.raises(TypeError):
        next(iterator)


def test_get_contiguous_periods() -> None:
    assert timezone_tools.get_contiguous_periods(
        (
            # Jan 1 - Jan 3
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 2),
            datetime.date(2024, 1, 3),
            # Jan 10 on its own
            datetime.date(2024, 1, 10),
            # Jan 7 - Jan 8
            datetime.date(2024, 1, 7),
            datetime.date(2024, 1, 8),
            # Jan 4 - Jan 5
            datetime.date(2024, 1, 4),
            datetime.date(2024, 1, 5),
            # Jan 14 - Jan 12 (reverse order)
            datetime.date(2024, 1, 14),
            datetime.date(2024, 1, 13),
            datetime.date(2024, 1, 12),
        )
    ) == (
        # Jan 1 - Jan 5
        (datetime.date(2024, 1, 1), datetime.date(2024, 1, 5)),
        # Jan 7 - Jan 8
        (datetime.date(2024, 1, 7), datetime.date(2024, 1, 8)),
        # Jan 10 on its own
        (datetime.date(2024, 1, 10), datetime.date(2024, 1, 10)),
        # Jan 12 - Jan 14
        (datetime.date(2024, 1, 12), datetime.date(2024, 1, 14)),
    )


def test_get_contiguous_periods_empty() -> None:
    assert timezone_tools.get_contiguous_periods(()) == ()


def test_get_contiguous_periods_requires_dates() -> None:
    # See Note [datetimes are dates]
    with pytest.raises(TypeError):
        timezone_tools.get_contiguous_periods((datetime.datetime(2024, 1, 1),))

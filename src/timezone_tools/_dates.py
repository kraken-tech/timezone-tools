import datetime
from collections.abc import Collection, Iterator

from dateutil import relativedelta

# Note [datetimes are dates]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python `datetime` objects are also `date` objects, so type checking will not
# prevent datetimes form being passed to functions that expect dates. To guard
# against unexpected behaviour, the functions in this module explcitly check
# for datetimes and raise a `TypeError` if they are passed in.


def is_last_day_of_month(date: datetime.date) -> bool:
    """Check whether a date is the last day of the month."""
    if isinstance(date, datetime.datetime):
        # See Note [datetimes are dates]
        raise TypeError(
            "is_last_day_of_month() argument must be a date, "
            f"not {type(date)!r}"
        )

    return date.month != (date + datetime.timedelta(days=1)).month


class DateNotFound(Exception):
    pass


def latest_date_for_day(
    period: tuple[datetime.date, datetime.date], day_of_month: int
) -> datetime.date:
    """Find the latest date in a period with the given calendar day.

    The period must have the dates in order: the start date must be before the
    end date.

    Raises:
        ValueError: The period is not valid.
        DateNotFound: The given date could not be found in the period.
    """
    period_start, period_end = period
    if isinstance(period_start, datetime.datetime) or isinstance(
        period_end, datetime.datetime
    ):
        # See Note [datetimes are dates]
        raise TypeError(
            "period must be a pair of dates, "
            f"not {(type(period_start), type(period_end))!r}"
        )
    if period_end < period_start:
        # the period ends before it starts
        raise ValueError

    # we can abort early if there will never be a date with this day
    if not (1 <= day_of_month <= 31):
        raise DateNotFound

    # starting at the end of the period, walk backwards until we reach a date
    # with the desired calendar day
    candidate = period_end
    while candidate >= period_start:
        if candidate.day == day_of_month:
            return candidate

        candidate -= datetime.timedelta(days=1)
    else:
        # we tried every date in the period and didn't find one with the
        # desired calendar day.
        raise DateNotFound


def closest_upcoming_match(
    preferred_day_of_month: int, after_date: datetime.date
) -> datetime.date:
    """Get the next date with the preferred calendar day, within a month.

    Returns:
        A date no more than 1 month after `after_date`.

        If there is no date with the preferred calendar day within a month of
        the start date (e.g. if the month is too short), the closest date will
        be returned. For example, attempting to find the next closest match to
        the 31st after April 5th will return April 30th, since that is the
        closest to that date within the next month.

    Raises:
        ValueError: The preferred calendar day is impossible
    """
    if isinstance(after_date, datetime.datetime):
        # See Note [datetimes are dates]
        raise TypeError(f"after_date must be a date, not {type(after_date)!r}")

    if not (1 <= preferred_day_of_month <= 31):
        raise ValueError

    # walk through the month following `after_date` until a matching date
    candidate = after_date + datetime.timedelta(days=1)
    last_day_in_range = after_date + relativedelta.relativedelta(months=1)
    while candidate <= last_day_in_range:
        if candidate.day == preferred_day_of_month:
            # matching date
            return candidate

        if preferred_day_of_month > candidate.day and is_last_day_of_month(
            candidate
        ):
            # end of month before reaching the preferred day; this means the
            # month is too short, so we should return this date.
            return candidate

        candidate += datetime.timedelta(days=1)
    else:  # pragma: no cover
        # This means we have found neither the end of the month, nor a matching
        # date. This should be impossible.
        raise RuntimeError


def iter_dates(
    start: datetime.date, stop: datetime.date
) -> Iterator[datetime.date]:
    """Iterate through consecutive dates in a period.

    The period must have the dates in order: the start date must be before the
    stop date.

    Yields:
        Each date in the period, including the start date and excluding the
        stop date.

    Raises:
        ValueError: The period is not valid.
    """
    if isinstance(start, datetime.datetime) or isinstance(
        stop, datetime.datetime
    ):
        # See Note [datetimes are dates]
        raise TypeError(
            "period must be a pair of dates, not {(type(start), type(stop))!r}"
        )

    if stop <= start:
        # the period ends before it starts
        raise ValueError

    date = start
    while date < stop:
        yield date
        date += datetime.timedelta(days=1)


def get_contiguous_periods(
    dates: Collection[datetime.date],
) -> tuple[tuple[datetime.date, datetime.date], ...]:
    """
    Find contiguous periods from a collection of dates.

    Returns:
        Pairs of dates that describe the boundaries (inclusive-inclusive) of
        contiguous periods of dates in the input sequence.

        For example:
            (2024-01-01, 2024-01-02, 2024-01-04, 2024-01-05, 2024-01-06)
        becomes
            ((2024-01-01, 2024-01-02), (2024-01-04, 2024-01-06))
    """
    if any(isinstance(date, datetime.datetime) for date in dates):
        # See Note [datetimes are dates]
        raise TypeError("consolidate_into_intervals() arguments must be dates")

    if not dates:
        return ()

    # step through dates in order and group into contiguous sequences
    sorted_dates = sorted(dates)
    sequences = [[sorted_dates[0]]]
    for date in sorted_dates[1:]:
        if sequences[-1][-1] == date - datetime.timedelta(days=1):
            # date is contiguous with last sequence: add it to that sequence
            sequences[-1].append(date)
        else:
            # date is disjoint from last sequence: start a new sequence
            sequences.append([date])

    return tuple((sequence[0], sequence[-1]) for sequence in sequences)

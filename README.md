# timezone-tools

Helpers for working with timezone-aware date-times.

This package provides:

- `TimezoneConverter`
  for making date-times timezone-aware
  and converting between timezones.
- `Clock`
  for getting the current time/date
  in a specific timezone.

## `TimezoneConverter`

This converter object can be used
to create timezone-aware `datetime` objects,
to make a naive `datetime` timezone-aware,
and to localize other timezone-aware `datetime` objects.

The converter also provides utilities
for converting a `datetime` into a `date` in the converter's timezone,
calculating dates and time relative to a `datetime`,
and rounding a `datetime` to the nearest increment of time
(e.g. to the nearest half-hour).

Create an instance of the timezone converter
by passing it an IANA time zone name.

```python
from timezone_tools import TimezoneConverter

paris_time = TimezoneConverter("Europe/Paris")
```

For more information about timezone support in Python,
see the [documentation for the `zoneinfo` module](https://docs.python.org/3/library/zoneinfo.html).

## `Clock`

This clock object can be used
to access the system clock
and provides timezone-aware dates and times.

The clock also provides utilities
for calculating dates and time relative to the current moment.

Create an instance of the clock
by passing it an IANA time zone name.

```python
from timezone_tools import Clock

paris_time = Clock("Europe/Paris")
```

For more information about timezone support in Python,
see the [documentation for the `zoneinfo` module](https://docs.python.org/3/library/zoneinfo.html).

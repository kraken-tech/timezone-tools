import datetime
import zoneinfo

import time_machine

from datetime_tools import Clock

# See Note [Use Europe/Paris for tests]


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

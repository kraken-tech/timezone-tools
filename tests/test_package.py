import datetime_tools as package


def test_has_docstring() -> None:
    assert package.__doc__ is not None

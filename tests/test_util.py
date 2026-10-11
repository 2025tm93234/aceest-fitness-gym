from datetime import date

import pytest

from aceest.util import non_negative_number, parse_date, positive_number


def test_parse_date_defaults_to_today():
    assert parse_date(None) == date.today().isoformat()


def test_parse_date_accepts_iso_date():
    assert parse_date("2026-10-08") == "2026-10-08"


def test_parse_date_rejects_other_formats():
    with pytest.raises(ValueError, match="date must be YYYY-MM-DD"):
        parse_date("08-10-2026")


def test_positive_number_converts_strings():
    assert positive_number("5", "age", int) == 5
    assert positive_number("72.5", "weight") == 72.5


@pytest.mark.parametrize("bad", [0, -1, "abc", None, True])
def test_positive_number_rejects_invalid_values(bad):
    with pytest.raises(ValueError, match="weight must be a positive number"):
        positive_number(bad, "weight")


def test_non_negative_number_allows_zero_but_not_negative():
    assert non_negative_number(0, "weight") == 0
    with pytest.raises(ValueError, match="weight must be a non-negative number"):
        non_negative_number(-1, "weight")

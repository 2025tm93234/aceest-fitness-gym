"""Small validation helpers shared by the feature modules."""
from datetime import date

from flask import request


def json_body():
    """Return the JSON request body as a dict (empty dict if missing or invalid)."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def parse_date(value, field="date"):
    """Return an ISO date string (YYYY-MM-DD); today's date when value is None."""
    if value is None:
        return date.today().isoformat()
    try:
        return date.fromisoformat(str(value)).isoformat()
    except ValueError:
        raise ValueError("{} must be YYYY-MM-DD".format(field))


def _number(value, field, kind, allow_zero):
    label = "a non-negative" if allow_zero else "a positive"
    if isinstance(value, bool):
        raise ValueError("{} must be {} number".format(field, label))
    try:
        number = kind(value)
    except (TypeError, ValueError):
        raise ValueError("{} must be {} number".format(field, label))
    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError("{} must be {} number".format(field, label))
    return number


def positive_number(value, field, kind=float):
    return _number(value, field, kind, allow_zero=False)


def non_negative_number(value, field, kind=float):
    return _number(value, field, kind, allow_zero=True)

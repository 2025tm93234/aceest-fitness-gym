"""Weekly adherence tracking and chart data (ACEest 2.x progress logging)."""
from datetime import datetime

from flask import Blueprint, jsonify

from .clients import find_client
from .db import get_db
from .util import json_body

bp = Blueprint("progress", __name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    week TEXT NOT NULL,
    adherence INTEGER NOT NULL
);
"""


def parse_adherence(value):
    message = "adherence must be an integer between 0 and 100"
    if value is None or isinstance(value, bool):
        raise ValueError(message)
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(message)
    if not 0 <= number <= 100:
        raise ValueError(message)
    return number


def _rows(name):
    return get_db().execute(
        "SELECT week, adherence FROM progress WHERE client_name = ? ORDER BY id", (name,)
    ).fetchall()


@bp.post("/clients/<name>/progress")
def log_progress(name):
    if find_client(name) is None:
        return jsonify(error="client not found"), 404
    data = json_body()
    try:
        adherence = parse_adherence(data.get("adherence"))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    week = str(data.get("week") or "").strip() or datetime.now().strftime("Week %U - %Y")
    db = get_db()
    db.execute(
        "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
        (name, week, adherence),
    )
    db.commit()
    return jsonify(name=name, week=week, adherence=adherence), 201


@bp.get("/clients/<name>/progress")
def list_progress(name):
    if find_client(name) is None:
        return jsonify(error="client not found"), 404
    return jsonify([dict(row) for row in _rows(name)]), 200


@bp.get("/clients/<name>/progress/chart")
def progress_chart(name):
    if find_client(name) is None:
        return jsonify(error="client not found"), 404
    rows = _rows(name)
    return jsonify(
        title="Weekly Adherence - {}".format(name),
        x_label="Week",
        y_label="Adherence (%)",
        y_min=0,
        y_max=100,
        labels=[row["week"] for row in rows],
        values=[row["adherence"] for row in rows],
        message=None if rows else "No progress data available for this client",
    ), 200

"""Body metrics logging and the weight-trend chart data (ACEest 2.2.4)."""
from flask import Blueprint, jsonify

from .clients import find_client
from .db import get_db
from .programs import calories_for
from .util import json_body, parse_date, positive_number

bp = Blueprint("metrics", __name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    date TEXT NOT NULL,
    weight REAL,
    waist REAL,
    bodyfat REAL
);
"""

MEASUREMENTS = ("weight", "waist", "bodyfat")


@bp.post("/clients/<name>/metrics")
def log_metrics(name):
    client = find_client(name)
    if client is None:
        return jsonify(error="client not found"), 404
    data = json_body()
    try:
        entry_date = parse_date(data.get("date"))
        values = {
            key: positive_number(data[key], key)
            for key in MEASUREMENTS
            if data.get(key) is not None
        }
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    if not values:
        return jsonify(error="at least one of weight, waist, bodyfat is required"), 400
    db = get_db()
    db.execute(
        "INSERT INTO metrics (client_name, date, weight, waist, bodyfat) VALUES (?, ?, ?, ?, ?)",
        (name, entry_date, values.get("weight"), values.get("waist"), values.get("bodyfat")),
    )
    if "weight" in values:
        # A new weight reading becomes the client's current weight (and calorie target).
        db.execute(
            "UPDATE clients SET weight = ?, calories = ? WHERE name = ?",
            (values["weight"], calories_for(client["program"], values["weight"]), name),
        )
    db.commit()
    return jsonify(name=name, date=entry_date, **values), 201


@bp.get("/clients/<name>/metrics")
def list_metrics(name):
    if find_client(name) is None:
        return jsonify(error="client not found"), 404
    rows = get_db().execute(
        "SELECT date, weight, waist, bodyfat FROM metrics "
        "WHERE client_name = ? ORDER BY date, id",
        (name,),
    ).fetchall()
    return jsonify([dict(row) for row in rows]), 200


@bp.get("/clients/<name>/metrics/weight-chart")
def weight_chart(name):
    if find_client(name) is None:
        return jsonify(error="client not found"), 404
    rows = get_db().execute(
        "SELECT date, weight FROM metrics "
        "WHERE client_name = ? AND weight IS NOT NULL ORDER BY date, id",
        (name,),
    ).fetchall()
    return jsonify(
        title="Weight Trend - {}".format(name),
        x_label="Date",
        y_label="Weight (kg)",
        labels=[row["date"] for row in rows],
        values=[row["weight"] for row in rows],
        message=None if rows else "No weight metrics available for this client",
    ), 200

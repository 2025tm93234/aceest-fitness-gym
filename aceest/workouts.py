"""Workout logging with optional exercise details and workout history (ACEest 2.2.4 / 3.2.4)."""
from flask import Blueprint, jsonify

from .clients import find_client
from .db import get_db
from .util import json_body, non_negative_number, parse_date, positive_number

bp = Blueprint("workouts", __name__)

WORKOUT_TYPES = ["Strength", "Hypertrophy", "Cardio", "Mobility"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    date TEXT NOT NULL,
    workout_type TEXT NOT NULL,
    duration_min INTEGER NOT NULL,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sets INTEGER,
    reps INTEGER,
    weight REAL
);
"""


def parse_exercise(data):
    """Validate the optional `exercise` object; return None when it is absent."""
    if data is None:
        return None
    if not isinstance(data, dict):
        raise ValueError("exercise must be an object")
    name = str(data.get("name") or "").strip()
    if not name:
        raise ValueError("exercise name is required")
    return {
        "name": name,
        "sets": positive_number(data.get("sets", 3), "sets", int),
        "reps": positive_number(data.get("reps", 10), "reps", int),
        "weight": non_negative_number(data.get("weight", 0), "weight"),
    }


@bp.post("/clients/<name>/workouts")
def log_workout(name):
    if find_client(name) is None:
        return jsonify(error="client not found"), 404
    data = json_body()
    try:
        workout_date = parse_date(data.get("date"))
        workout_type = str(data.get("workout_type") or "").strip()
        if workout_type not in WORKOUT_TYPES:
            raise ValueError("workout_type must be one of: " + ", ".join(WORKOUT_TYPES))
        duration = positive_number(data.get("duration_min", 60), "duration_min", int)
        exercise = parse_exercise(data.get("exercise"))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    notes = str(data.get("notes") or "").strip()
    db = get_db()
    cursor = db.execute(
        "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) "
        "VALUES (?, ?, ?, ?, ?)",
        (name, workout_date, workout_type, duration, notes),
    )
    workout_id = cursor.lastrowid
    if exercise:
        db.execute(
            "INSERT INTO exercises (workout_id, name, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
            (workout_id, exercise["name"], exercise["sets"], exercise["reps"], exercise["weight"]),
        )
    db.commit()
    return jsonify(id=workout_id, date=workout_date, workout_type=workout_type), 201


@bp.get("/clients/<name>/workouts")
def workout_history(name):
    if find_client(name) is None:
        return jsonify(error="client not found"), 404
    db = get_db()
    rows = db.execute(
        "SELECT id, date, workout_type, duration_min, notes FROM workouts "
        "WHERE client_name = ? ORDER BY date DESC, id DESC",
        (name,),
    ).fetchall()
    history = []
    for row in rows:
        item = dict(row)
        item["exercises"] = [
            dict(exercise)
            for exercise in db.execute(
                "SELECT name, sets, reps, weight FROM exercises WHERE workout_id = ? ORDER BY id",
                (row["id"],),
            ).fetchall()
        ]
        history.append(item)
    return jsonify(history), 200

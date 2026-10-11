"""Client management: add, save (update), load and list clients."""
import sqlite3

from flask import Blueprint, jsonify

from .db import get_db
from .programs import PROGRAMS, calories_for
from .util import json_body, parse_date, positive_number

bp = Blueprint("clients", __name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    age INTEGER,
    height REAL,
    weight REAL,
    program TEXT,
    calories INTEGER,
    target_weight REAL,
    target_adherence INTEGER,
    notes TEXT,
    membership_status TEXT NOT NULL DEFAULT 'Active',
    membership_end TEXT
);
"""

NUMERIC_FIELDS = {
    "age": int,
    "height": float,
    "weight": float,
    "target_weight": float,
    "target_adherence": int,
}


def find_client(name):
    return get_db().execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()


def parse_fields(data):
    """Validate the optional client fields present in `data`; raise ValueError if invalid."""
    fields = {}
    for key, kind in NUMERIC_FIELDS.items():
        if data.get(key) is not None:
            fields[key] = positive_number(data[key], key, kind)
    if fields.get("target_adherence", 0) > 100:
        raise ValueError("target_adherence must be between 1 and 100")
    if data.get("program") is not None:
        if data["program"] not in PROGRAMS:
            raise ValueError("program must be one of: " + ", ".join(PROGRAMS))
        fields["program"] = data["program"]
    if "notes" in data:
        fields["notes"] = str(data["notes"] or "").strip()
    if data.get("membership_status") is not None:
        status = str(data["membership_status"]).strip()
        if not status:
            raise ValueError("membership_status cannot be empty")
        fields["membership_status"] = status
    if data.get("membership_end") is not None:
        fields["membership_end"] = parse_date(data["membership_end"], "membership_end")
    return fields


@bp.post("/clients")
def create_client():
    data = json_body()
    name = str(data.get("name") or "").strip()
    if not name:
        return jsonify(error="name is required"), 400
    try:
        fields = parse_fields(data)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    fields["calories"] = calories_for(fields.get("program"), fields.get("weight"))
    # Column names come from the fixed whitelist above, never from user input.
    columns = ["name"] + list(fields)
    placeholders = ", ".join("?" for _ in columns)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO clients ({}) VALUES ({})".format(", ".join(columns), placeholders),
            [name] + list(fields.values()),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify(error="client '{}' already exists".format(name)), 409
    return jsonify(dict(find_client(name))), 201


@bp.get("/clients")
def list_clients():
    rows = get_db().execute("SELECT * FROM clients ORDER BY name").fetchall()
    return jsonify([dict(row) for row in rows]), 200


@bp.get("/clients/<name>")
def get_client(name):
    client = find_client(name)
    if client is None:
        return jsonify(error="client not found"), 404
    return jsonify(dict(client)), 200


@bp.put("/clients/<name>")
def update_client(name):
    client = find_client(name)
    if client is None:
        return jsonify(error="client not found"), 404
    try:
        fields = parse_fields(json_body())
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    if not fields:
        return jsonify(error="no valid fields supplied"), 400
    program = fields.get("program", client["program"])
    weight = fields.get("weight", client["weight"])
    fields["calories"] = calories_for(program, weight)
    assignments = ", ".join("{} = ?".format(column) for column in fields)
    db = get_db()
    db.execute(
        "UPDATE clients SET {} WHERE name = ?".format(assignments),
        list(fields.values()) + [name],
    )
    db.commit()
    return jsonify(dict(find_client(name))), 200

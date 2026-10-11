"""Role-based login (ACEest 3.x login screen). A default admin/admin account is seeded."""
from flask import Blueprint, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from .util import json_body

bp = Blueprint("auth", __name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);
"""


def seed(conn):
    conn.execute(
        """INSERT INTO users (username, password_hash, role)
           VALUES (?, ?, ?)
           ON CONFLICT(username) DO NOTHING""",
        ("admin", generate_password_hash("admin", method="pbkdf2:sha256"), "Admin"),
    )


@bp.post("/auth/login")
def login():
    data = json_body()
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "").strip()
    if not username or not password:
        return jsonify(error="username and password are required"), 400
    row = get_db().execute(
        "SELECT password_hash, role FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password):
        return jsonify(error="invalid credentials"), 401
    return jsonify(username=username, role=row["role"]), 200

"""
ACEest Fitness & Gym - Flask Application
Independent Flask implementation for the BITS DevOps assignment.
The supplied Tkinter versions are used as functional references.
"""

import os
import random
import sqlite3
from datetime import date

from flask import Flask, g, jsonify, request

DB_PATH = os.environ.get("DB_PATH", "aceest_fitness.db")

PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"],
}


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("weight_kg and height_m must be > 0")
    return round(weight_kg / (height_m ** 2), 2)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def create_app(db_path: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or DB_PATH

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        conn = sqlite3.connect(app.config["DB_PATH"])
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                age INTEGER,
                height REAL,
                weight REAL,
                program TEXT,
                membership_status TEXT DEFAULT 'Active'
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                date TEXT NOT NULL,
                workout_type TEXT,
                duration_min INTEGER,
                notes TEXT
            )
        """)
        conn.commit()
        conn.close()

    app.init_db = init_db
    app.get_db = get_db

    @app.get("/")
    def home():
        return jsonify(service="ACEest Fitness & Gym API", status="running")

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.post("/clients")
    def add_client():
        data = request.get_json(force=True) or {}
        name = data.get("name")
        if not name:
            return jsonify(error="name is required"), 400

        db = get_db()
        try:
            db.execute(
                "INSERT INTO clients (name, age, height, weight, membership_status) "
                "VALUES (?, ?, ?, ?, 'Active')",
                (name, data.get("age"), data.get("height"), data.get("weight")),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return jsonify(error=f"client '{name}' already exists"), 409
        return jsonify(message=f"client '{name}' created"), 201

    @app.get("/clients")
    def list_clients():
        db = get_db()
        rows = db.execute("SELECT * FROM clients ORDER BY name").fetchall()
        return jsonify([dict(row) for row in rows]), 200

    @app.get("/clients/<name>")
    def get_client(name):
        db = get_db()
        row = db.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
        if row is None:
            return jsonify(error="client not found"), 404
        return jsonify(dict(row)), 200

    @app.get("/clients/<name>/bmi")
    def client_bmi(name):
        db = get_db()
        row = db.execute(
            "SELECT height, weight FROM clients WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            return jsonify(error="client not found"), 404
        if row["height"] is None or row["weight"] is None:
            return jsonify(error="height/weight not set for this client"), 400
        bmi = calculate_bmi(row["weight"], row["height"])
        return jsonify(name=name, bmi=bmi, category=bmi_category(bmi)), 200

    @app.post("/clients/<name>/program")
    def generate_program(name):
        db = get_db()
        row = db.execute("SELECT name FROM clients WHERE name = ?", (name,)).fetchone()
        if row is None:
            return jsonify(error="client not found"), 404
        data = request.get_json(silent=True) or {}
        program_type = data.get("program_type") or random.choice(list(PROGRAM_TEMPLATES))
        if program_type not in PROGRAM_TEMPLATES:
            return jsonify(error=f"unknown program_type '{program_type}'"), 400
        detail = random.choice(PROGRAM_TEMPLATES[program_type])
        db.execute("UPDATE clients SET program = ? WHERE name = ?", (detail, name))
        db.commit()
        return jsonify(name=name, program_type=program_type, program=detail), 200

    @app.get("/clients/<name>/membership")
    def check_membership(name):
        db = get_db()
        row = db.execute(
            "SELECT membership_status FROM clients WHERE name = ?", (name,)
        ).fetchone()
        # INTENTIONAL BUG: an unknown client causes HTTP 500 because row is None.
        return jsonify(name=name, membership_status=row["membership_status"]), 200

    @app.post("/clients/<name>/workouts")
    def add_workout(name):
        db = get_db()
        client = db.execute("SELECT name FROM clients WHERE name = ?", (name,)).fetchone()
        if client is None:
            return jsonify(error="client not found"), 404
        data = request.get_json(force=True) or {}
        db.execute(
            "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                name,
                data.get("date", date.today().isoformat()),
                data.get("workout_type", "General"),
                data.get("duration_min", 30),
                data.get("notes", ""),
            ),
        )
        db.commit()
        return jsonify(message="workout logged"), 201

    @app.get("/clients/<name>/workouts")
    def list_workouts(name):
        db = get_db()
        client = db.execute("SELECT name FROM clients WHERE name = ?", (name,)).fetchone()
        if client is None:
            return jsonify(error="client not found"), 404
        rows = db.execute(
            "SELECT date, workout_type, duration_min, notes "
            "FROM workouts WHERE client_name = ? ORDER BY date DESC",
            (name,),
        ).fetchall()
        return jsonify([dict(row) for row in rows]), 200

    init_db()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
